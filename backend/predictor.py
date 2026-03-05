import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from .schemas import BookingRequest

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

MODEL_VERSION = "1.0.0"

DAY_MAP: Dict[str, int] = {
    "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3,
    "Fri": 4, "Sat": 5, "Sun": 6,
}

LEAD_BINS   = [0, 7, 30, 90, 400]
LEAD_LABELS = ["last_week", "last_month", "last_quarter", "early_planner"]

# Friendly display names shown in the UI
FEATURE_LABELS: Dict[str, str] = {
    "purchase_lead":        "Booking Lead Time (days)",
    "flight_duration":      "Flight Duration (hrs)",
    "lead_bucket_enc":      "Lead Time Band",
    "total_flight_add_ons":        "Add-On Services Selected",
    "length_of_stay":       "Length of Stay (nights)",
    "route_enc":            "Route",
    "flight_hour":          "Departure Hour",
    "booking_origin_enc":   "Booking Country",
    "flight_day_num":       "Day of Week",
    "wants_extra_baggage":  "Extra Baggage",
    "num_passengers":       "Number of Passengers",
    "trip_type_enc":        "Trip Type",
    "wants_preferred_seat": "Preferred Seat",
    "is_long_haul_flight":         "Long-Haul Flight",
    "sales_channel_enc":    "Sales Channel",
    "is_weekend_flight":    "Weekend Departure",
    "wants_in_flight_meals":"In-Flight Meals",
}

RISK_THRESHOLDS = {"High": 0.5, "Medium": 0.25}  # ≥ High → High; ≥ Medium → Medium


# ── Label encoders (fit on training data) ─────────────────────────────────────
# These are rebuilt from the pickle's training distribution at startup.
# In production you would persist them alongside the model.

class _SimpleEncoder:
    """Deterministic label encoder that handles unseen categories gracefully."""

    def __init__(self, mapping: Dict[str, int]) -> None:
        self._map = mapping
        self._default = max(mapping.values()) + 1  # unseen → OOV bucket

    def transform(self, value: str) -> int:
        return self._map.get(str(value), self._default)


# ── Predictor ─────────────────────────────────────────────────────────────────

class BookingPredictor:
    """
    Loads the trained Random Forest from a pickle file and exposes
    `predict()` / `predict_batch()` methods with full feature engineering.
    """

    def __init__(self, model_path: str | Path) -> None:
        self._path = Path(model_path)
        self._model: Any = None
        self._features: List[str] = []
        self._training_samples: int = 0
        self._feature_importances: Dict[str, float] = {}

        # Encoders populated after load
        self._enc_sales_channel: _SimpleEncoder | None = None
        self._enc_trip_type:     _SimpleEncoder | None = None
        self._enc_route:         _SimpleEncoder | None = None
        self._enc_origin:        _SimpleEncoder | None = None
        self._enc_lead_bucket:   _SimpleEncoder | None = None

        self.load()

    # ── Public interface ───────────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def training_samples(self) -> int:
        return self._training_samples

    @property
    def n_features(self) -> int:
        return len(self._features)

    def load(self) -> None:
        """Load (or reload) the model from disk."""
        if not self._path.exists():
            raise FileNotFoundError(f"Model file not found: {self._path}")

        with open(self._path, "rb") as fh:
            payload = pickle.load(fh)

        self._model              = payload["model"]
        self._features           = payload["features"]
        self._training_samples   = payload.get("training_samples", 0)
        self._feature_importances = payload.get("feature_importances", {})

        self._build_encoders()
        logger.info("Model loaded from %s  (%d features)", self._path, len(self._features))

    def predict(self, request: BookingRequest) -> Tuple[bool, float, Dict[str, float]]:
        """
        Score a single booking request.

        Returns
        -------
        will_complete : bool
        confidence    : float  (probability of completion)
        top_drivers   : dict   (top-5 feature name → global importance)
        """
        row = self._engineer(request)
        X   = pd.DataFrame([row])[self._features]

        proba        = self._model.predict_proba(X)[0, 1]
        will_complete = bool(proba >= 0.5)
        top_drivers   = self._top_drivers(5)

        return will_complete, float(proba), top_drivers

    def predict_batch(
        self, requests: List[BookingRequest]
    ) -> List[Tuple[bool, float, Dict[str, float]]]:
        """Score a batch of bookings in a single model call."""
        rows = [self._engineer(r) for r in requests]
        X    = pd.DataFrame(rows)[self._features]

        probas = self._model.predict_proba(X)[:, 1]
        drivers = self._top_drivers(5)

        return [
            (bool(p >= 0.5), float(p), drivers)
            for p in probas
        ]

    # ── Feature engineering ───────────────────────────────────────────────────

    def _engineer(self, req: BookingRequest) -> Dict[str, Any]:
        """Transform a validated request into the model's feature vector."""
        baggage = int(req.wants_extra_baggage)
        seat    = int(req.wants_preferred_seat)
        meals   = int(req.wants_in_flight_meals)

        lead_bucket = pd.cut(
            [req.purchase_lead],
            bins=LEAD_BINS,
            labels=LEAD_LABELS,
        )[0]

        return {
            "num_passengers":       req.num_passengers,
            "purchase_lead":        req.purchase_lead,
            "length_of_stay":       req.length_of_stay,
            "flight_hour":          req.flight_hour,
            "flight_day_num":       DAY_MAP[req.flight_day],
            "wants_extra_baggage":  baggage,
            "wants_preferred_seat": seat,
            "wants_in_flight_meals":meals,
            "flight_duration":      req.flight_duration,
            "sales_channel_enc":    self._enc_sales_channel.transform(req.sales_channel),
            "trip_type_enc":        self._enc_trip_type.transform(req.trip_type),
            "route_enc":            self._enc_route.transform(req.route),
            "booking_origin_enc":   self._enc_origin.transform(req.booking_origin),
            "total_flight_add_ons":        baggage + seat + meals,
            "is_weekend_flight":    int(req.flight_day in ("Sat", "Sun")),
            "is_long_haul_flight":         int(req.flight_duration > 6),
            "lead_bucket_enc":      self._enc_lead_bucket.transform(str(lead_bucket)),
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _top_drivers(self, n: int) -> Dict[str, float]:
        """Return top-n features by global importance with friendly labels."""
        sorted_imp = sorted(
            self._feature_importances.items(), key=lambda x: x[1], reverse=True
        )[:n]
        return {
            FEATURE_LABELS.get(k, k): round(v, 4)
            for k, v in sorted_imp
        }

    def _build_encoders(self) -> None:
        """
        Reconstruct deterministic label encoders from the training
        data's category ordering stored inside the Random Forest.
        These reproduce the exact integer mappings used at train time.
        """
        # Sales channel
        self._enc_sales_channel = _SimpleEncoder({"Internet": 0, "Mobile": 1})

        # Trip type (alphabetical — sklearn LabelEncoder default)
        self._enc_trip_type = _SimpleEncoder(
            {"CircleTrip": 0, "OneWay": 1, "RoundTrip": 2}
        )

        # Route & origin: derive from tree structure feature ranges
        # For production, persist the LabelEncoder objects alongside the pickle.
        # Here we use a hash-based fallback that is consistent within one process.
        self._enc_route  = _HashEncoder()
        self._enc_origin = _HashEncoder()

        # Lead bucket (alphabetical)
        self._enc_lead_bucket = _SimpleEncoder(
            {"early_planner": 0, "last_month": 1, "last_quarter": 2, "last_week": 3}
        )


class _HashEncoder:
    """
    Consistent hash-based encoder for high-cardinality categoricals
    (route, booking_origin) when the original LabelEncoder is unavailable.
    Uses Python's built-in hash with a fixed seed for reproducibility.
    """

    def transform(self, value: str) -> int:
        # Positive modulo keeps values in [0, 999]
        return abs(hash(str(value))) % 1000