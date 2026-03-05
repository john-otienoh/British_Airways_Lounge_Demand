"""
app.py  —  British Airways  |  Customer Booking Predictor  |  Streamlit Frontend
================================================================================
Run:
    streamlit run app.py

Requires the FastAPI backend to be running on http://localhost:8000
"""

from __future__ import annotations
from typing import Any, Dict, Optional

import requests
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="BA Booking Predictor",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ─────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

ROUTES = [
    "LHR to JFK", "LHR to DXB", "LHR to SYD", "LHR to BKK", "LHR to NRT", "LHR to HKG",
    "LHR to SIN", "LHR to LAX", "LHR to ORD", "LHR to MIA", "LHR to DEL", "LHR to MAA",
    "LHR to MEL", "LHR to AUH", "LHR to DOH", "LHR to BOM", "LHR to CPT", "LHR to YYZ",
    "LHR to GRU", "LHR to SCL", "LHR to NBO", "LHR to JNB", "LHR to CDG", "LHR to FRA",
    "LHR to AMM", "LHR to CAI", "LHR to CUN", "LHR to PVR", "LHR to MNL",
]

BOOKING_ORIGINS = [
    "United Kingdom", "United States", "Australia", "Germany", "France",
    "Japan", "India", "UAE", "Singapore", "Canada", "Brazil",
    "South Africa", "China", "Malaysia", "Thailand", "Netherlands",
    "Spain", "Italy", "Sweden", "South Korea",
]

# ── BA brand colours as CSS variables ─────────────────────────────────────────
BA_CSS = """
<style>
/* ── Google Font ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@300;400;600&display=swap');

/* ── Root palette ───────────────────────────── */
:root {
    --ba-navy:   #0B1F78;
    --ba-red:    #CC0000;
    --ba-gold:   #D4A017;
    --ba-light:  #E8EAF6;
    --ba-silver: #F5F6FA;
    --ba-grey:   #6B7280;
    --ba-white:  #FFFFFF;
    --radius:    10px;
}

/* ── Global resets ───────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif !important;
    background-color: var(--ba-silver) !important;
}

/* ── Header bar ──────────────────────────────── */
.ba-header {
    background: var(--ba-navy);
    padding: 1.2rem 2rem;
    border-radius: var(--radius);
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}
.ba-header .logo {
    background: var(--ba-gold);
    color: var(--ba-navy);
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    width: 52px; height: 52px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    border: 2px solid white;
}
.ba-header .title-block h1 {
    font-family: 'Playfair Display', serif !important;
    color: var(--ba-white) !important;
    font-size: 1.55rem !important;
    margin: 0 !important; padding: 0 !important;
}
.ba-header .title-block p {
    color: var(--ba-gold) !important;
    font-size: 0.85rem !important;
    margin: 0 !important;
    font-style: italic;
}

/* ── Section cards ───────────────────────────── */
.card {
    background: var(--ba-white);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(11,31,120,0.07);
    border-left: 4px solid var(--ba-navy);
}
.card.red  { border-left-color: var(--ba-red); }
.card.gold { border-left-color: var(--ba-gold); }

.card h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--ba-navy) !important;
    font-size: 1rem !important;
    margin-bottom: 0.8rem !important;
    letter-spacing: 0.3px;
}

/* ── Result banner ───────────────────────────── */
.result-banner {
    border-radius: var(--radius);
    padding: 1.8rem 2rem;
    text-align: center;
    margin: 1rem 0;
}
.result-banner.complete {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
    border: 2px solid #10b981;
}
.result-banner.incomplete {
    background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
    border: 2px solid var(--ba-red);
}
.result-banner h2 {
    font-family: 'Playfair Display', serif !important;
    color: white !important;
    font-size: 1.6rem !important;
    margin: 0 0 0.3rem !important;
}
.result-banner p {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
}

/* ── Metric tiles ────────────────────────────── */
.metric-row { display: flex; gap: 0.8rem; margin: 1rem 0; flex-wrap: wrap; }
.metric-tile {
    flex: 1; min-width: 110px;
    background: var(--ba-light);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.metric-tile .val {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: var(--ba-navy);
    font-weight: 700;
    line-height: 1;
}
.metric-tile .lbl {
    font-size: 0.72rem;
    color: var(--ba-grey);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 4px;
}

/* ── Driver bars ─────────────────────────────── */
.driver-row { margin: 0.4rem 0; }
.driver-label { font-size: 0.82rem; color: var(--ba-grey); margin-bottom: 2px; }
.driver-bar-bg {
    background: var(--ba-light);
    border-radius: 4px;
    height: 10px;
    overflow: hidden;
}
.driver-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--ba-navy), var(--ba-red));
    border-radius: 4px;
    transition: width 0.6s ease;
}

/* ── Risk badge ──────────────────────────────── */
.risk-badge {
    display: inline-block;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.4px;
}
.risk-high   { background: #dcfce7; color: #166534; }
.risk-medium { background: #fef9c3; color: #854d0e; }
.risk-low    { background: #fee2e2; color: #991b1b; }

/* ── Confidence gauge ───────────────────────── */
.gauge-wrap { text-align: center; margin: 0.5rem 0; }
.gauge-num  {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    color: var(--ba-navy);
    line-height: 1;
}
.gauge-sub { font-size: 0.78rem; color: var(--ba-grey); text-transform: uppercase; letter-spacing: 0.8px; }

/* ── Sidebar overrides ───────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--ba-navy) !important;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stNumberInput label,
section[data-testid="stSidebar"] .stRadio label {
    color: var(--ba-gold) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: white !important;
}

/* ── Primary button ──────────────────────────── */
.stButton > button[kind="primary"] {
    background: var(--ba-red) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 0.6rem 2rem !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.5px !important;
    transition: opacity 0.2s !important;
    width: 100% !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }

/* ── Divider ─────────────────────────────────── */
hr { border-color: rgba(11,31,120,0.12) !important; }

/* ── Status pill ─────────────────────────────── */
.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.status-pill.ok  { background: #dcfce7; color: #166534; }
.status-pill.err { background: #fee2e2; color: #991b1b; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.green { background: #16a34a; }
.dot.red   { background: #dc2626; }

.gauge-wrap{
    text-align:center;
    margin-bottom:1rem;
}

.gauge-num{
    font-size:42px;
    font-weight:700;
}

.gauge-sub{
    font-size:14px;
    color:gray;
}

.risk-badge{
    padding:6px 16px;
    border-radius:20px;
    font-weight:600;
    font-size:14px;
}

.risk-high{
    background:#dcfce7;
    color:#166534;
}

.risk-medium{
    background:#fef3c7;
    color:#92400e;
}

.risk-low{
    background:#fee2e2;
    color:#991b1b;
}
</style>
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _api_health() -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _predict(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        r = requests.post(f"{API_BASE}/predict", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as exc:
        try:
            detail = exc.response.json().get("detail", str(exc))
        except Exception:
            detail = str(exc)
        st.error(f"API error: {detail}")
        return None
    except requests.ConnectionError:
        st.error("Cannot reach the prediction API. Is the backend running on port 8000?")
        return None
    except Exception as exc:
        st.error(f"Unexpected error: {exc}")
        return None


def _confidence_bar_html(confidence: float) -> str:
    pct = confidence * 100
    color = "#16a34a" if confidence >= 0.5 else ("#d97706" if confidence >= 0.25 else "#dc2626")
    return f"""
    <div style="background:#e5e7eb;border-radius:6px;height:14px;overflow:hidden;margin:6px 0 12px">
        <div style="height:100%;width:{pct:.1f}%;background:{color};border-radius:6px;
                    transition:width 0.6s ease"></div>
    </div>
    """


def _driver_bars_html(drivers: Dict[str, float]) -> str:
    if not drivers:
        return ""
    max_val = max(drivers.values()) or 1
    rows = ""
    for name, val in drivers.items():
        pct = (val / max_val) * 100
        rows += f"""
        <div class="driver-row">
            <div class="driver-label">{name}</div>
            <div class="driver-bar-bg">
                <div class="driver-bar-fill" style="width:{pct:.1f}%"></div>
            </div>
        </div>
        """
    return rows


def _risk_html(level: str) -> str:
    cls_map = {"High": "risk-high", "Medium": "risk-medium", "Low": "risk-low"}
    icon_map = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
    css = cls_map.get(level, "risk-low")
    icon = icon_map.get(level, "")
    return f'<span class="risk-badge {css}">{icon} {level} Intent</span>'


# ── Main UI ───────────────────────────────────────────────────────────────────

def main():
    st.markdown(BA_CSS, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    health = _api_health()
    status_html = (
        '<span class="status-pill ok"><span class="dot green"></span>API Online</span>'
        if health
        else '<span class="status-pill err"><span class="dot red"></span>API Offline</span>'
    )
    st.markdown(f"""
    <div class="ba-header">
        <div class="logo">BA</div>
        <div class="title-block">
            <h1>Customer Booking Predictor</h1>
            <p>Powered by Random Forest · British Airways Data Science · {status_html}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar — Input form ───────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## Booking Details")
        st.markdown("---")

        st.markdown("**FLIGHT**")
        route          = st.selectbox("Route", ROUTES, index=0)
        flight_day     = st.selectbox("Departure Day", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
        flight_hour    = st.slider("Departure Hour", 0, 23, 8)
        flight_duration = st.slider("Flight Duration (hrs)", 0.5, 20.0, 7.5, 0.5)

        st.markdown("---")
        st.markdown("**PASSENGER & BOOKING**")
        num_passengers  = st.number_input("Number of Passengers", 1, 9, 2)
        booking_origin  = st.selectbox("Booking Country", BOOKING_ORIGINS)
        sales_channel   = st.radio("Sales Channel", ["Internet", "Mobile"], horizontal=True)
        trip_type       = st.selectbox("Trip Type", ["RoundTrip", "OneWay", "CircleTrip"])
        purchase_lead   = st.slider("Booking Lead Time (days)", 0, 400, 60)
        length_of_stay  = st.slider("Length of Stay (nights)", 0, 30, 7)

        st.markdown("---")
        st.markdown("**ADD-ONS**")
        extra_baggage   = st.checkbox("Extra Baggage")
        preferred_seat  = st.checkbox("Preferred Seat")
        inflight_meals  = st.checkbox("In-Flight Meals")

        st.markdown("---")
        predict_btn = st.button("Predict Booking Outcome", type="primary")

    # ── Main panel ────────────────────────────────────────────────────────────
    col_result, col_detail = st.columns([1.1, 1], gap="large")

    with col_result:
        st.markdown('<div class="card"><h3>Prediction Result</h3>', unsafe_allow_html=True)

        if "last_result" not in st.session_state:
            st.info("Fill in the booking details in the sidebar and press **Predict** to score the customer.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            res = st.session_state.last_result
            will_complete = res["will_complete"]
            confidence    = res["confidence"]
            risk          = res["risk_level"]

            if will_complete:
                st.markdown(f"""
                <div class="result-banner complete">
                    <h2>Likely to Complete</h2>
                    <p>The model predicts this customer <strong>will complete</strong> their booking.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-banner incomplete">
                    <h2>At Risk of Abandonment</h2>
                    <p>The model predicts this customer <strong>may not complete</strong> their booking.</p>
                </div>
                """, unsafe_allow_html=True)

            # Confidence + risk
            st.markdown(f"""
            <div class="gauge-wrap">
                <div class="gauge-num">{confidence*100:.1f}%</div>
                <div class="gauge-sub">Completion Probability</div>
            </div>
            {_confidence_bar_html(confidence)}
            <div style="text-align:center;margin-bottom:1rem">{_risk_html(risk)}</div>
            """, unsafe_allow_html=True)
            # st.markdown("</div>", unsafe_allow_html=True)

            # Action recommendation
            if will_complete:
                st.success("**Recommended Action:** Confirm the booking and send a personalised confirmation email.")
            elif confidence >= 0.25:
                st.warning("**Recommended Action:** Trigger a targeted re-engagement campaign within 24 hours.")
            else:
                st.error("**Recommended Action:** Escalate to commercial team for a proactive outreach call.")

    with col_detail:
        # Top predictive drivers
        st.markdown('<div class="card gold"><h3>Top Predictive Drivers</h3>', unsafe_allow_html=True)
        if "last_result" in st.session_state:
            drivers = st.session_state.last_result.get("top_drivers", {})
            st.markdown(
                _driver_bars_html(drivers) or "<p style='color:#6B7280'>No driver data available.</p>",
                unsafe_allow_html=True,
            )
            st.caption(
                "Feature importance scores from the trained Random Forest model. "
                "Higher bars indicate greater predictive power for this outcome."
            )
        else:
            st.markdown("<p style='color:#6B7280;font-size:0.9rem'>Run a prediction to see the key drivers.</p>",
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Booking summary
        if "last_input" in st.session_state:
            inp = st.session_state.last_input
            st.markdown('<div class="card red"><h3>Booking Summary</h3>', unsafe_allow_html=True)
            cols = st.columns(2)
            summary = {
                "Route": inp["route"],
                "Channel": inp["sales_channel"],
                "Trip Type": inp["trip_type"],
                "Lead Time": f"{inp['purchase_lead']} days",
                "Passengers": inp["num_passengers"],
                "Stay": f"{inp['length_of_stay']} nights",
                "Duration": f"{inp['flight_duration']} hrs",
                "Add-ons": sum([
                    inp["wants_extra_baggage"],
                    inp["wants_preferred_seat"],
                    inp["wants_in_flight_meals"],
                ]),
            }
            items = list(summary.items())
            for i, (k, v) in enumerate(items):
                with cols[i % 2]:
                    st.metric(label=k, value=v)
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Model info (expander) ──────────────────────────────────────────────────
    with st.expander("About this Model"):
        if health:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Algorithm", "Random Forest")
            c2.metric("Training Samples", f"{health['training_samples']:,}")
            c3.metric("Features", health["features"])
            c4.metric("Model Version", health["version"])
        st.markdown("""
        **How it works:** This tool uses a machine learning model trained on historical
        British Airways booking data to predict whether a customer will complete a booking.
        The model analyses booking characteristics such as lead time, route, add-on selections,
        and sales channel to estimate completion probability.

        **Risk bands:**
        - **High** — ≥ 50% probability of completion
        - **Medium** — 25–49% probability (recommend re-targeting)
        - **Low** — < 25% probability (recommend proactive outreach)

        *Results are indicative and should be used alongside commercial judgment.*
        """)

    # ── History table ──────────────────────────────────────────────────────────
    if st.session_state.get("history"):
        with st.expander(f"Prediction History ({len(st.session_state.history)} runs)"):
            import pandas as pd
            st.dataframe(
                pd.DataFrame(st.session_state.history),
                width="stretch",
                hide_index=True,
            )

    # ── Prediction trigger ────────────────────────────────────────────────────
    if predict_btn:
        payload = {
            "num_passengers":       int(num_passengers),
            "sales_channel":        sales_channel,
            "trip_type":            trip_type,
            "purchase_lead":        int(purchase_lead),
            "length_of_stay":       int(length_of_stay),
            "flight_hour":          int(flight_hour),
            "flight_day":           flight_day,
            "route":                route,
            "booking_origin":       booking_origin,
            "wants_extra_baggage":  extra_baggage,
            "wants_preferred_seat": preferred_seat,
            "wants_in_flight_meals":inflight_meals,
            "flight_duration":      float(flight_duration),
        }

        with st.spinner("Scoring booking …"):
            result = _predict(payload)

        if result:
            st.session_state.last_result = result
            st.session_state.last_input  = payload

            # Append to history
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "Route":       route,
                "Channel":     sales_channel,
                "Lead (days)": purchase_lead,
                "Duration":    flight_duration,
                "Confidence":  f"{result['confidence']*100:.1f}%",
                "Risk":        result["risk_level"],
                "Outcome":     "Complete" if result["will_complete"] else "At Risk",
            })

            st.rerun()


if __name__ == "__main__":
    main()