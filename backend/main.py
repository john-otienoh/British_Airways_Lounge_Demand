import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .predictor import RISK_THRESHOLDS, MODEL_VERSION, BookingPredictor
from .schemas import (
    BatchPredictionResponse,
    BatchRequest,
    BookingRequest,
    HealthResponse,
    PredictionResponse,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ba.api")
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "models" / "british_Airways_Booking_Model.pkl"

# ── Application state ─────────────────────────────────────────────────────────
predictor: BookingPredictor | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once at startup; release resources on shutdown."""
    global predictor
    logger.info("Loading booking model from %s …", MODEL_PATH)
    try:
        predictor = BookingPredictor(model_path=MODEL_PATH)
        logger.info(
            "Model ready  |  features=%d  training_samples=%d",
            predictor.n_features,
            predictor.training_samples,
        )
    except FileNotFoundError as exc:
        logger.critical("Cannot find model file: %s", exc)
        raise SystemExit(1) from exc
    yield
    logger.info("Shutting down — releasing model resources")


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="British Airways  |  Customer Booking Prediction API",
    description=(
        "Predicts whether a customer will **complete** a flight booking "
        "given their booking characteristics. "
        "Intended for BA commercial teams — no ML knowledge required."
    ),
    version=MODEL_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow Streamlit frontend on any local port) ─────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request timing middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed:.1f}"
    logger.debug("%s %s  %.1f ms", request.method, request.url.path, elapsed)
    return response


# ── Global error handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# ── Utility ───────────────────────────────────────────────────────────────────
def _risk_band(confidence: float) -> str:
    if confidence >= RISK_THRESHOLDS["High"]:
        return "High"
    if confidence >= RISK_THRESHOLDS["Medium"]:
        return "Medium"
    return "Low"


def _guard_predictor() -> BookingPredictor:
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Please try again in a moment.",
        )
    return predictor


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    tags=["System"],
)
async def health() -> HealthResponse:
    """Returns model status and basic metadata. Use for monitoring / readiness probes."""
    p = _guard_predictor()
    return HealthResponse(
        status="ok",
        model_loaded=p.is_loaded,
        training_samples=p.training_samples,
        features=p.n_features,
        version=MODEL_VERSION,
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Score a single booking",
    tags=["Prediction"],
    status_code=status.HTTP_200_OK,
)
async def predict_single(booking: BookingRequest) -> PredictionResponse:
    """
    Submit one customer booking and receive a completion probability,
    a will-complete flag, a risk band, and the top predictive drivers.

    **Risk bands**
    - 🟢 **High** — model is confident the customer will complete (≥ 50% probability)
    - 🟡 **Medium** — borderline, recommend re-targeting (25–49%)
    - 🔴 **Low** — customer unlikely to complete (< 25%)
    """
    p = _guard_predictor()

    try:
        will_complete, confidence, drivers = p.predict(booking)
    except Exception as exc:
        logger.error("Prediction error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Prediction failed: {exc}",
        )

    logger.info(
        "predict  route=%s  channel=%s  lead=%d  →  p=%.3f  complete=%s",
        booking.route,
        booking.sales_channel,
        booking.purchase_lead,
        confidence,
        will_complete,
    )

    return PredictionResponse(
        will_complete=will_complete,
        confidence=round(confidence, 4),
        risk_level=_risk_band(confidence),
        top_drivers=drivers,
        model_version=MODEL_VERSION,
    )


@app.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Score up to 500 bookings in one call",
    tags=["Prediction"],
    status_code=status.HTTP_200_OK,
)
async def predict_batch(payload: BatchRequest) -> BatchPredictionResponse:
    """
    Submit a list of bookings (max 500) for bulk scoring.
    Returns individual predictions plus aggregate statistics.
    """
    p = _guard_predictor()

    try:
        results = p.predict_batch(payload.bookings)
    except Exception as exc:
        logger.error("Batch prediction error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Batch prediction failed: {exc}",
        )

    predictions = [
        PredictionResponse(
            will_complete=wc,
            confidence=round(conf, 4),
            risk_level=_risk_band(conf),
            top_drivers=drivers,
            model_version=MODEL_VERSION,
        )
        for wc, conf, drivers in results
    ]

    completed = sum(1 for r in predictions if r.will_complete)
    total     = len(predictions)

    logger.info("batch predict  n=%d  completed=%d", total, completed)

    return BatchPredictionResponse(
        total=total,
        completed_count=completed,
        not_completed_count=total - completed,
        completion_rate=round(completed / total, 4),
        predictions=predictions,
    )