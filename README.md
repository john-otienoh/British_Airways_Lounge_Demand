```markdown
# British Airways Customer Analytics & Holiday Purchase Prediction System

## Project Overview

This project demonstrates a full end-to-end airline analytics workflow, beginning with lounge demand modeling and progressing to a production-grade predictive system for identifying customers likely to purchase holiday packages.

The system includes:

- Exploratory data analysis and feature engineering
- Predictive modeling using RandomForest and XGBoost
- Hyperparameter tuning and cross-validation
- Lift and commercial performance evaluation
- Production API using FastAPI
- Business-facing frontend using Streamlit
- Docker-ready deployment structure

The objective is to allow non-technical commercial teams to proactively target high-intent customers before departure.

---

## Business Context

> *"If you're hoping that a customer purchases your flights as they come into the airport, you've already lost."*

Modern airline customers are highly empowered — they research, compare, and decide long before arriving at the airport. British Airways must shift from a **reactive** to a **proactive** acquisition model by:

- Identifying high-intent customers **before** they travel
- Triggering personalised campaigns at the optimal moment in the booking window
- Prioritising commercial team resources on the customers most likely to convert

Using predictive modeling, we identify customers with high probability of purchasing holiday packages, enabling:

- Targeted marketing campaigns
- Budget optimization
- Improved conversion rates
- Higher revenue per passenger

---

## Project Structure

```

```bash
lounge-demand-forecast/
│
├── README.md
├── requirements.txt
├── LICENSE
│
├── data/
│   ├── raw/
│   │   └── BA_Summer_Schedule.xlsx
│   ├── processed/
│   │   ├── flights_clean.csv
│   │   ├── lounge_lookup.csv
│   │   └── eligibility_results.csv
│   └── assumptions/
│       └── eligibility_assumptions.xlsx
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_create_lookup_table.ipynb
│   ├── 03_apply_lookup_to_schedule.ipynb
│   └── 04_capacity_forecast.ipynb
│
├── sql/
│   ├── schema.sql
│   ├── etl.sql
│   └── kpi_queries.sql
│
├── models/
│   ├── grouping_logic.py
│   ├── eligibility_model.py
│   └── forecast_model.py
│
├── dashboards/
│   ├── Lounge_Demand.pbix
│   └── screenshots/
│
├── reports/
│   ├── lounge_lookup_table.xlsx
│   ├── methodology.pdf
│   └── presentation.pptx
│
└── docs/
    ├── data_dictionary.md
    ├── assumptions.md
    └── project_plan.md
```
## Technical Architecture

Hybrid deployment model:

Frontend (Streamlit)
        ↓
FastAPI Backend
        ↓
Serialized ML Pipeline (pickle)

The backend handles all inference logic. The frontend provides a clean commercial interface for business users.

---

## Tasks Covered

### Task One: Lounge Demand Modeling
- Data grouping strategy design
- Lookup table creation
- Forecast logic using flight attributes
- Commercial capacity interpretation

### Task Two: Holiday Purchase Prediction
- Data cleaning and preparation
- Feature engineering
- Model training (RandomForest, XGBoost)
- Hyperparameter tuning
- Cross-validation
- Lift analysis
- Business interpretation

---

## Model Features

Examples of engineered features:

- Lead time buckets
- Weekend travel flag
- Party size categories
- Add-on purchase intensity
- Long-haul indicator
- Seasonal indicators
- Interaction terms

---

## Performance Metrics

Model evaluation includes:

- ROC-AUC
- Accuracy
- Precision
- Recall
- F1 Score
- Lift in top decile
- Cross-validation stability

Commercial lift is emphasized over raw accuracy.

---

## Dataset Description

| Column | Type | Description |
|---|---|---|
| `num_passengers` | int | Number of passengers travelling |
| `sales_channel` | str | Channel booking was made on (`Internet`, `Mobile`) |
| `trip_type` | str | Trip type (`RoundTrip`, `OneWay`, `CircleTrip`) |
| `purchase_lead` | int | Days between travel date and booking date |
| `length_of_stay` | int | Days spent at destination |
| `flight_hour` | int | Hour of flight departure (0–23) |
| `flight_day` | str | Day of week of departure (`Mon`–`Sun`) |
| `route` | str | Origin → destination route code |
| `booking_origin` | str | Country from which booking was made |
| `wants_extra_baggage` | int | 1 if customer selected extra baggage |
| `wants_preferred_seat` | int | 1 if customer selected preferred seat |
| `wants_in_flight_meals` | int | 1 if customer selected in-flight meals |
| `flight_duration` | float | Total flight duration in hours |
| `booking_complete` | int | **Target** — 1 if customer completed booking |

**Dataset stats:**
- 50,000 records · 14 columns · 0 null values
- Class imbalance: ~14.3% completed bookings (class 1), ~85.7% not completed (class 0)

---

## Setup Instructions

### 1. Clone Repository

```

git clone https://github.com/john-otienoh/British_Airways_Lounge_Demand
cd British_Airways_Lounge_Demand

```

### 2. Create Virtual Environment

```

python -m venv venv
source venv/bin/activate

```

On Windows:
```

venv\Scripts\activate

```

### 3. Install Dependencies

```

pip install -r requirements.txt

```

---

## Training the Model

To retrain the model run the notebook:

```


```bash
jupyter notebook notebooks/BA_Customer_Booking_Model.ipynb

```

The trained model will be saved to:

```

models/british_Airways_Booking_Model.pkl

```

---

## Running the Backend (FastAPI)

Navigate to backend directory:

```

cd backend

```

Start server:

```

uvicorn app.main:app --reload

```

API will run at:

```

[http://127.0.0.1:8000](http://127.0.0.1:8000)

```

Available endpoints:

- GET /health
- POST /predict
- POST /batch

Swagger documentation:

```

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

```

---

## Running the Frontend (Streamlit)

In a separate terminal:

```

cd frontend
streamlit run app.py

```

Frontend will run at:

```

[http://localhost:8501](http://localhost:8501)

```

---
## Quickstart

### Make a Prediction (curl)

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "num_passengers": 2,
    "purchase_lead": 45,
    "length_of_stay": 7,
    "flight_hour": 10,
    "flight_duration": 11.5,
    "wants_extra_baggage": 1,
    "wants_preferred_seat": 0,
    "wants_in_flight_meals": 1,
    "sales_channel": "Mobile",
    "trip_type": "RoundTrip",
    "flight_day": "Fri"
  }'
```

**Response:**
```json
{
  "probability": 0.71,
  "will_book": true,
  "confidence_tier": "High",
  "top_drivers": ["purchase_lead", "wants_extra_baggage", "flight_duration"]
}
```

---

## Data Preparation Pipeline

The feature engineering pipeline (defined in `api/pipeline.py` and mirrored exactly in the notebook) performs the following transformations:

### Encoding

| Raw Column | Transformation | Output Column |
|---|---|---|
| `flight_day` | Ordinal map Mon=0 … Sun=6 | `flight_day_num` |
| `sales_channel` | Label encoding | `sales_channel_enc` |
| `trip_type` | Label encoding | `trip_type_enc` |
| `route` | Label encoding | `route_enc` |
| `booking_origin` | Label encoding | `booking_origin_enc` |

### Engineered Features

| Feature | Logic | Rationale |
|---|---|---|
| `total_add_ons` | Sum of 3 add-on flags | Single intent signal |
| `is_weekend_flight` | `flight_day` ∈ {Sat, Sun} → 1 | Leisure vs business pattern |
| `is_long_haul` | `flight_duration` > 6 hrs → 1 | Higher commitment proxy |
| `lead_bucket` | Bin `purchase_lead` into 4 buckets | Captures non-linear booking window effects |
| `lead_bucket_enc` | Label encode `lead_bucket` | Model-compatible format |

### Final Feature Set (17 features)

```python
FEATURES = [
    "num_passengers", "purchase_lead", "length_of_stay", "flight_hour",
    "flight_day_num", "wants_extra_baggage", "wants_preferred_seat",
    "wants_in_flight_meals", "flight_duration", "sales_channel_enc",
    "trip_type_enc", "route_enc", "booking_origin_enc",
    "total_add_ons", "is_weekend_flight", "is_long_haul", "lead_bucket_enc"
]
```

> **Critical:** The feature list and order must be **identical** between training and inference. The saved pickle stores the `FEATURES` list to guarantee this.

---

## Machine Learning Model

### Algorithm: Random Forest Classifier

Random Forest was selected because it:
- Handles mixed feature types without normalisation
- Is robust to outliers and irrelevant features
- Natively outputs interpretable **feature importance scores**
- Scales well with `n_jobs=-1` parallelism
- The `class_weight='balanced'` parameter compensates for the ~14% class imbalance

### Hyperparameters

```python
RandomForestClassifier(
    n_estimators=200,        # 200 decision trees
    max_depth=10,            # Prevent overfitting
    min_samples_leaf=30,     # Minimum samples per leaf node
    class_weight="balanced", # Corrects for 14% positive class rate
    random_state=42,         # Reproducibility
    n_jobs=-1                # Parallelise across all CPU cores
)
```

### Training

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

clf.fit(X_train, y_train)
```

---

##  Model Evaluation

### 5-Fold Stratified Cross-Validation Results

| Metric | Mean | Std Dev |
|---|---|---|
| **Accuracy** | 71.2% | ±0.3% |
| **ROC-AUC** | 0.652 | ±0.004 |
| **Precision** | 23.6% | ±0.6% |
| **Recall** | 45.7% | ±1.7% |
| **F1 Score** | 0.311 | ±0.009 |

### Interpretation

- The **ROC-AUC of 0.652** is meaningfully above the 0.5 random baseline, confirming real predictive signal in the data.
- **Recall of 45.7%** means the model identifies nearly half of all customers who will complete a booking — suitable for proactive campaign targeting.
- **Low precision (23.6%)** is expected given the severe class imbalance and is acceptable for a marketing use case where the cost of targeting a non-converter is low.
- The **low standard deviation** across folds confirms the model is stable and not overfitting.

---

## Feature Importance

Top predictors ranked by mean decrease in impurity (Random Forest):

| Rank | Feature | Importance | Interpretation |
|---|---|---|---|
| 1 | `purchase_lead` | 0.280 | Early planners convert at significantly higher rates |
| 2 | `flight_duration` | 0.130 | Long-haul passengers show stronger booking commitment |
| 3 | `lead_bucket_enc` | 0.123 | Non-linear booking window effects captured |
| 4 | `total_add_ons` | 0.063 | Add-on selection is a strong intent signal |
| 5 | `length_of_stay` | 0.063 | Longer trips indicate higher holiday intent |
| 6 | `route_enc` | 0.058 | Some routes have systematically higher conversion |
| 7 | `flight_hour` | 0.056 | Flight timing correlates with customer type |
| 8 | `booking_origin_enc` | 0.053 | Origin market predicts booking behaviour |

---

## Saving & Loading the Model

### Save

The model is saved as a pickle payload containing both the model and all metadata required for inference:

```python
import pickle

model_payload = {
    "model":               clf,
    "features":            FEATURES,       # Ordered feature list — critical for inference
    "target":              "booking_complete",
    "n_estimators":        clf.n_estimators,
    "max_depth":           clf.max_depth,
    "class_weight":        clf.class_weight,
    "training_samples":    len(X),
    "class_distribution":  y.value_counts().to_dict(),
    "feature_importances": dict(zip(FEATURES, clf.feature_importances_)),
}

with open("model/ba_booking_model.pkl", "wb") as f:
    pickle.dump(model_payload, f)
```

### Load

```python
import pickle

with open("model/ba_booking_model.pkl", "rb") as f:
    payload = pickle.load(f)

model    = payload["model"]
FEATURES = payload["features"]   # Always load features from pickle — never hardcode

# Predict
probability = model.predict_proba(df[FEATURES])[0, 1]
```

> **File size:** ~11.2 MB  |  **Python:** 3.11+  |  **scikit-learn:** 1.4.2+

---
## Using the Application

### Single Customer Prediction

1. Enter customer attributes
2. Click Predict
3. Receive:
   - Probability of purchase
   - Intent segment
   - Commercial recommendation

### Batch Upload

1. Upload CSV file
2. Model scores each row
3. Download enriched CSV with:
   - Probability
   - Intent segment

---

## Governance & Model Management

- Model version stored in models/model_metadata.json
- Feature list stored in models/feature_list.json
- Structured preprocessing pipeline prevents training-serving skew
- Class imbalance handled via scale_pos_weight

---

## Future Enhancements

- SHAP explainability integration
- Model drift detection
- CRM integration
- Cloud deployment (AWS / Azure)
- CI/CD automation
- Authentication layer

---

## Author

Analytics and Machine Learning Implementation Project  
Airline Commercial Analytics Simulation


## Contributing

1. Fork the repository and create a feature branch: `git checkout -b feature/your-feature`
2. Follow the existing code style — run `flake8` before committing
3. Add or update tests in `tests/` for any new logic
4. Ensure all tests pass: `pytest tests/ -v`
5. Open a pull request with a clear description of changes and business justification

---

## Acknowledgements

- **British Airways Data Science Team** — project sponsor and domain experts
- **[Forage / British Airways Virtual Experience](https://www.theforage.com/simulations/british-airways)** — original task brief and dataset
- **scikit-learn** — machine learning library
- **FastAPI** — API framework
- **Streamlit** — internal UI framework

---

*British Airways Data Science · Customer Acquisition Strategy · 2024*
*Model Version: 1.0 · Training Dataset: 50,000 bookings · Algorithm: Random Forest*