from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class SalesChannel(str, Enum):
    internet = "Internet"
    mobile = "mobile"

class TripType(str, Enum):
    round_trip = "RoundTrip"
    one_way = "OneWay"
    circle_trip = "CircleTrip"

class FlightDay(str, Enum):
    mon = "Mon"
    tue = "Tue"
    wed = "Wed"
    thu = "Thu"
    fri = "Fri"
    sat = "Sat"
    sun = "Sun"

class BookingRequest(BaseModel):
    """
    All inputs required to score a single customer booking.
    Field descriptions are surfaced in the auto-generated OpenAPI docs.
    """

    num_passengers: int = Field(
        ..., ge=1, le=9,
        description="Number of passengers in the booking",
        examples=[2],
    )
    sales_channel: SalesChannel = Field(
        ...,
        description="Channel through which the booking was initiated",
        examples=["Internet"],
    )
    trip_type: TripType = Field(
        ...,
        description="Type of trip (RoundTrip / OneWay / CircleTrip)",
        examples=["RoundTrip"],
    )
    purchase_lead: int = Field(
        ..., ge=0, le=400,
        description="Days between the booking date and the travel date",
        examples=[60],
    )
    length_of_stay: int = Field(
        ..., ge=0, le=365,
        description="Number of nights at the destination",
        examples=[7],
    )
    flight_hour: int = Field(
        ..., ge=0, le=23,
        description="Scheduled departure hour (24-hour clock)",
        examples=[9],
    )
    flight_day: FlightDay = Field(
        ...,
        description="Day of the week of the departure flight",
        examples=["Mon"],
    )
    route: str = Field(
        ..., min_length=2, max_length=20,
        description="Origin–destination route code (e.g. LHRJFK)",
        examples=["LHRJFK"],
    )
    booking_origin: str = Field(
        ..., min_length=2, max_length=60,
        description="Country from which the booking was made",
        examples=["United Kingdom"],
    )
    wants_extra_baggage: bool = Field(
        ...,
        description="Customer selected extra baggage",
        examples=[True],
    )
    wants_preferred_seat: bool = Field(
        ...,
        description="Customer selected a preferred seat",
        examples=[False],
    )
    wants_in_flight_meals: bool = Field(
        ...,
        description="Customer selected in-flight meals",
        examples=[False],
    )
    flight_duration: float = Field(
        ..., ge=0.5, le=24.0,
        description="Total flight duration in hours",
        examples=[7.5],
    )

    @field_validator("route")
    @classmethod
    def route_uppercase(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("booking_origin")
    @classmethod
    def origin_stripped(cls, v: str) -> str:
        return v.strip().title()
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "num_passengers": 2,
                "sales_channel": "Internet",
                "trip_type": "RoundTrip",
                "purchase_lead": 90,
                "length_of_stay": 14,
                "flight_hour": 8,
                "flight_day": "Fri",
                "route": "LHRJFK",
                "booking_origin": "United Kingdom",
                "wants_extra_baggage": True,
                "wants_preferred_seat": False,
                "wants_in_flight_meals": True,
                "flight_duration": 7.5,
            }
        }
class PredictionResponse(BaseModel):
    """Single-booking prediction result."""

    will_complete: bool = Field(
        description="Whether the model predicts the customer will complete the booking"
    )
    confidence: float = Field(
        description="Model confidence score (0–1) that the booking will be completed"
    )
    risk_level: str = Field(
        description="Human-readable risk band: Low / Medium / High"
    )
    top_drivers: Dict[str, float] = Field(
        description="Top 5 features most influential on this prediction (name → importance)"
    )
    model_version: str = Field(
        description="Identifier of the model that produced this score"
    )

class BatchRequest(BaseModel):
    """Batch of up to 500 bookings for bulk scoring."""
    bookings: List[BookingRequest] = Field(..., min_length=1, max_length=500)


class BatchPredictionResponse(BaseModel):
    """Bulk scoring results."""
    total: int
    completed_count: int
    not_completed_count: int
    completion_rate: float
    predictions: List[PredictionResponse]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    training_samples: int
    features: int
    version: str