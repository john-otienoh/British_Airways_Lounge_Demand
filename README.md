# ✈️ British Airways — Customer Analytics & Holiday Purchase Prediction System

> **Proactive customer acquisition using machine learning.**
> A production-grade predictive system that identifies customers likely to purchase holiday packages, enabling British Airways' commercial teams to target high-intent customers *before* they travel.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.2-orange?style=flat-square&logo=scikit-learn)](https://scikit-learn.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=flat-square&logo=streamlit)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-Internal-lightgrey?style=flat-square)]()

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Business Context](#2-business-context)
3. [Project Structure](#3-project-structure)
4. [Technical Architecture](#4-technical-architecture)
5. [Tasks Covered](#5-tasks-covered)
6. [Dataset Description](#6-dataset-description)
7. [Setup Instructions](#7-setup-instructions)
8. [Training the Model](#8-training-the-model)
9. [Running the Backend (FastAPI)](#9-running-the-backend-fastapi)
10. [Running the Frontend (Streamlit)](#10-running-the-frontend-streamlit)
11. [Quickstart](#11-quickstart)
12. [Data Preparation Pipeline](#12-data-preparation-pipeline)
13. [Machine Learning Model](#13-machine-learning-model)
14. [Model Evaluation](#14-model-evaluation)
15. [Feature Importance](#15-feature-importance)
16. [Model Features](#16-model-features)
17. [Saving & Loading the Model](#17-saving--loading-the-model)
18. [Using the Application](#18-using-the-application)
19. [Governance & Model Management](#19-governance--model-management)
20. [Future Enhancements](#20-future-enhancements)
21. [Contributing](#21-contributing)
22. [Acknowledgements](#22-acknowledgements)

---

## 1. Project Overview

This project demonstrates a full end-to-end airline analytics workflow, beginning with lounge demand modelling and progressing to a production-grade predictive system for identifying customers likely to purchase holiday packages.

The system includes:

- Exploratory data analysis and feature engineering
- Predictive modelling using RandomForest and XGBoost
- Hyperparameter tuning and cross-validation
- Lift and commercial performance evaluation
- Production API using FastAPI
- Business-facing frontend using Streamlit
- Docker-ready deployment structure

The objective is to allow non-technical commercial teams to proactively target high-intent customers before departure.

---

## 2. Business Context

> *"If you're hoping that a customer purchases your flights as they come into the airport, you've already lost."*

Modern airline customers are highly empowered — they research, compare, and decide long before arriving at the airport. British Airways must shift from a **reactive** to a **proactive** acquisition model by:

- Identifying high-intent customers **before** they travel
- Triggering personalised campaigns at the optimal moment in the booking window
- Prioritising commercial team resources on the customers most likely to convert

Using predictive modelling, we identify customers with high probability of purchasing holiday packages, enabling:

- Targeted marketing campaigns
- Budget optimisation
- Improved conversion rates
- Higher revenue per passenger

---

## 3. Project Structure

```
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
│   ├── forecast_model.py
│   ├── model_metadata.json
│   └── feature_list.json
│
├── backend/
│   └── app/
│       └── main.py
│
├── frontend/
│   └── app.py
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

---

## 4. Technical Architecture

Hybrid deployment model — the backend handles all inference logic; the frontend provides a clean commercial interface for business users.

```
Frontend (Streamlit)
        ↓
FastAPI Backend
        ↓
Serialised ML Pipeline (pickle)
```

---

## 5. Tasks Covered

### Task One — Lounge Demand Modelling

- Data grouping strategy design
- Lookup table creation
- Forecast logic using flight attributes
- Commercial capacity interpretation

### Task Two — Holiday Purchase Prediction

- Data cleaning and preparation
- Feature engineering
- Model training (RandomForest, XGBoost)
- Hyperparameter tuning
- Cross-validation
- Lift analysis
- Business interpretation

---

## 6. Dataset Description

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

## 7. Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/john-otienoh/British_Airways_Lounge_Demand
cd British_Airways_Lounge_Demand
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 8. Training the Model

Run the analysis notebook to train and serialise the model:

```bash
jupyter notebook notebooks/BA_Customer_Booking_Model.ipynb
```

The trained model will be saved to:

```
models/british_Airways_Booking_Model.pkl
```

---

## 9. Running the Backend (FastAPI)

Navigate to the backend directory and start the server:

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

Available endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `POST` | `/predict` | Single customer prediction |
| `POST` | `/batch` | Batch CSV scoring |

Interactive Swagger documentation: `http://127.0.0.1:8000/docs`

---

## 10. Running the Frontend (Streamlit)

In a separate terminal:

```bash
cd frontend
streamlit run app.py
```

The frontend will be available at `http://localhost:8501`

---

## 11. Quickstart

### Make a Single Prediction (curl)

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

## 12. Data Preparation Pipeline

The feature engineering pipeline (`api/pipeline.py`, mirrored exactly in the notebook) performs the following transformations:

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

> ⚠️ **Critical:** The feature list and order must be **identical** between training and inference. The saved pickle stores the `FEATURES` list to guarantee this.

---

## 13. Machine Learning Model

### Algorithm — Random Forest Classifier

Random Forest was selected because it:

- Handles mixed feature types without normalisation
- Is robust to outliers and irrelevant features
- Natively outputs interpretable **feature importance scores**
- Scales well with `n_jobs=-1` parallelism
- `class_weight='balanced'` compensates for the ~14% class imbalance

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

## 14. Model Evaluation

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

> Commercial lift is emphasised over raw accuracy.

---

## 15. Feature Importance

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

## 16. Model Features

Examples of engineered features used across the full pipeline:

- Lead time buckets
- Weekend travel flag
- Party size categories
- Add-on purchase intensity
- Long-haul indicator
- Seasonal indicators
- Interaction terms

---

## 17. Saving & Loading the Model

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

> **File size:** ~11.2 MB &nbsp;|&nbsp; **Python:** 3.11+ &nbsp;|&nbsp; **scikit-learn:** 1.4.2+

---

## 18. Using the Application

### Single Customer Prediction

1. Enter customer attributes in the Streamlit form
2. Click **Predict**
3. Receive:
   - Probability of purchase
   - Intent segment (High / Medium / Low)
   - Commercial recommendation

### Batch Upload

1. Upload a CSV file via the Streamlit interface
2. The model scores each row automatically
3. Download the enriched CSV containing:
   - Booking probability per customer
   - Intent segment label

---

## 19. Governance & Model Management

- Model version stored in `models/model_metadata.json`
- Feature list stored in `models/feature_list.json`
- Structured preprocessing pipeline prevents training-serving skew
- Class imbalance handled via `class_weight="balanced"` (Random Forest) / `scale_pos_weight` (XGBoost)

---

## 20. Future Enhancements

| Priority | Enhancement | Expected Impact |
|---|---|---|
| High | SHAP explainability integration | Per-prediction driver transparency |
| High | Model drift detection | Catch performance degradation early |
| Medium | CRM integration | Push scores directly to marketing tools |
| Medium | Cloud deployment (AWS / Azure) | Scale to production workloads |
| Medium | CI/CD automation | Automate retraining on new data |
| Low | Authentication layer | Restrict API to authorised users only |

---

## 21. Contributing

1. Fork the repository and create a feature branch: `git checkout -b feature/your-feature`
2. Follow the existing code style — run `flake8` before committing
3. Add or update tests in `tests/` for any new logic
4. Ensure all tests pass: `pytest tests/ -v`
5. Open a pull request with a clear description of changes and business justification

---

## 22. Acknowledgements

- **British Airways Data Science Team** — project sponsor and domain experts
- **[Forage / British Airways Virtual Experience](https://www.theforage.com/simulations/british-airways)** — original task brief and dataset
- **scikit-learn** — machine learning library
- **FastAPI** — API framework
- **Streamlit** — internal UI framework

---

*British Airways Data Science · Customer Acquisition Strategy · 2024*
*Model Version: 1.0 · Training Dataset: 50,000 bookings · Algorithm: Random Forest*