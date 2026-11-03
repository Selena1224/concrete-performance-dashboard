# Import the libraries needed for the dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from pathlib import Path

# Locate the project folder and load our files
BASE_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="Executive Overview",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

df = pd.read_csv(BASE_DIR / "data" / "concrete_prepared.csv")

decisions = pd.read_csv(
    BASE_DIR / "data" / "concrete_management_decisions.csv"
)

model_package = joblib.load(
    BASE_DIR / "models" / "concrete_strength_model.joblib"
)

# Load our business assumptions and model screening threshold
target = float(model_package["example_target_mpa"])
buffer = float(model_package["prediction_buffer_mpa"])
cutoff = target + buffer

# Retrieve our recommended concrete mixture
priority_mix = decisions.loc[
    decisions["recipe_id"] == "R186"
].iloc[0]


# -------------------------------------------------------
# DASHBOARD DESIGN
# -------------------------------------------------------


# Apply consistent styling to the executive dashboard
st.markdown("""
<style>

/* Overall dashboard appearance */
.stApp {
    background-color: #F5F7FB;
}

.block-container {
    max-width: 1350px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #14263D;
    letter-spacing: -0.025em;
}

/* Style KPI cards and enable responsive font sizing */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.035);
    min-width: 0;
    container-type: inline-size;
}

/* Wrap all KPI labels without truncation */
[data-testid="stMetricLabel"] {
    color: #64748B;
    height: auto !important;
    min-height: 2.8em;
    min-width: 0 !important;
    overflow: visible !important;
}

[data-testid="stMetricLabel"] > div {
    width: 100% !important;
    min-width: 0 !important;
}

[data-testid="stMetricLabel"] p {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: break-word !important;
    line-height: 1.4 !important;
}

/* Adjust KPI number sizes to each card's width */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div,
[data-testid="stMetricValue"] > div > div {
    color: #14263D;
    font-size: clamp(1rem, 11cqi, 2.25rem) !important;
    min-width: 0 !important;
    max-width: 100% !important;
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
    font-variant-numeric: tabular-nums;
}

/* Allow metric comparison indicators to wrap */
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] > div {
    min-width: 0 !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
}

/* Executive header banner */
.executive-header {
    background: linear-gradient(115deg, #14263D, #254861);
    padding: 35px;
    border-radius: 15px;
    margin-bottom: 28px;
    color: white;
}

.executive-header h1 {
    color: white;
    font-size: 2.25rem;
    margin: 8px 0 12px;
}

.executive-header p {
    color: #D7E4ED;
    margin: 0;
    font-size: 1.03rem;
}

.eyebrow {
    color: #80E1CD;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.14em;
}

/* Management recommendation card */
.recommendation-card {
    background: white;
    border-left: 5px solid #008F80;
    border-radius: 10px;
    padding: 24px;
    margin-top: 10px;
    color: #334155;
}

.recommendation-card h3 {
    margin-top: 0;
}

.recommendation-card p {
    line-height: 1.75;
}

.section-label {
    color: #64748B;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)



# -------------------------------------------------------
# EXECUTIVE HEADER
# -------------------------------------------------------

st.markdown("""
<div class="executive-header">
    <div class="eyebrow">
        OPERATIONS INTELLIGENCE | MANAGEMENT REVIEW
    </div>
    <h1>Concrete Mix Performance</h1>
    <p>
        Data-driven mixture selection, strength forecasting,
        and material efficiency analysis.
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# KEY PERFORMANCE INDICATORS
# -------------------------------------------------------

st.markdown("### Executive Overview")

# Four KPIs give management a quick view of our recommendation
k1, k2, k3, k4 = st.columns(4)

# Keep KPI values short so they fit on smaller screens
# Show measurement units in the labels instead of the values

with k1:
    st.metric(
        "Priority Mix",
        "R186"
    )

with k2:
    st.metric(
        "CV Strength (MPa)",
        f"{priority_mix['predicted_strength_mpa']:.2f}",
        help="Cross-validated strength prediction at 28 days"
    )

with k3:
    st.metric(
        "Binder (kg/m³)",
        f"{priority_mix['total_binder']:.2f}"
    )

with k4:
    st.metric(
        "Screening Margin (MPa)",
        f"+{priority_mix['screening_margin_mpa']:.2f}",
        help="Predicted strength above the conservative screening cutoff"
    )

st.write("")


# -------------------------------------------------------
# RECOMMENDATION AND BUSINESS RATIONALE
# -------------------------------------------------------

st.markdown("### Recommended Decision")

st.markdown(f"""
<div class="recommendation-card">
    <div class="eyebrow" style="color:#008F80;">
        PRIORITY 01 — LABORATORY VALIDATION
    </div>
    <h3>Prioritize Mix R186 for further testing</h3>
    <p>
        R186 provides a promising balance between material use
        and predicted compressive strength.
        It requires <b>399.47 kg/m³ of binder</b> and has a
        cross-validated strength prediction of <b>52.64 MPa</b>
        at 28 days.
    </p>
    <p>
        Compared with R133, R186 uses approximately
        <b>2.3% more binder</b> while providing
        <b>3.62 MPa higher predicted strength</b>.
        It also requires less binder than the higher-strength
        alternatives R290 and R322.
    </p>
    <p style="font-size:0.88rem;color:#64748B;">
        Recommendation: Conduct replicate laboratory tests
        before considering production use. Predictions are
        screening estimates, not engineering certification.
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# MATERIAL USE VS PREDICTED STRENGTH
# -------------------------------------------------------

st.write("")
st.markdown("### Material Efficiency vs. Predicted Strength")

# Give each shortlisted mixture a distinct color
mix_colors = {
    "R186": "#008F80",
    "R133": "#4178A9",
    "R290": "#E6A23C",
    "R322": "#8B78B7"
}

# Plot binder content against predicted strength
# This helps management evaluate the material-strength trade-off
fig = px.scatter(
    decisions,
    x="total_binder",
    y="predicted_strength_mpa",
    color="recipe_id",
    text="recipe_id",
    color_discrete_map=mix_colors,
    hover_data={
        "cement": ":.2f",
        "actual_strength_mpa": ":.2f",
        "total_binder": ":.2f",
        "predicted_strength_mpa": ":.2f"
    },
    labels={
        "total_binder": "Total Binder (kg/m³)",
        "predicted_strength_mpa": "Predicted Strength (MPa)",
        "recipe_id": "Concrete Mix"
    }
)

# Make the points easier to identify
fig.update_traces(
    marker=dict(size=18, line=dict(width=2, color="white")),
    textposition="top center"
)

# Add the business strength target
fig.add_hline(
    y=target,
    line_dash="dot",
    line_color="#64748B",
    annotation_text="40 MPa requirement"
)

# Show our conservative model screening cutoff
fig.add_hline(
    y=cutoff,
    line_dash="dash",
    line_color="#008F80",
    annotation_text="Conservative screening cutoff",
    annotation_position="bottom right"
)

# Format the chart for an executive presentation
fig.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(l=20, r=20, t=35, b=30),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2
    ),
    font=dict(
        family="Arial",
        size=12,
        color="#334155"
    ),
    plot_bgcolor="white",
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Each point represents a historical concrete mixture. "
    "Strength values are out-of-fold predictions used for screening. "
    "Lower binder quantities do not necessarily mean lower cost."
)


# -------------------------------------------------------
# MANAGEMENT COMPARISON TABLE
# -------------------------------------------------------

st.write("")
st.markdown("### Management Options")

# Select the columns most relevant to the business decision
management_table = decisions[
    [
        "recipe_id",
        "recommendation",
        "total_binder",
        "cement",
        "predicted_strength_mpa",
        "screening_margin_mpa"
    ]
].copy()

# Use readable names instead of Python variable names
management_table.columns = [
    "Mix",
    "Recommended Role",
    "Binder (kg/m³)",
    "Cement (kg/m³)",
    "Predicted Strength (MPa)",
    "Screening Margin (MPa)"
]

st.dataframe(
    management_table.round(2),
    hide_index=True,
    use_container_width=True
)


# -------------------------------------------------------
# MODEL RELIABILITY AND NEXT ACTIONS
# -------------------------------------------------------

st.write("")
st.markdown("### Decision Confidence & Next Actions")

left, right = st.columns(2, gap="large")

with left:
    st.markdown("**Model reliability**")

    st.write(
        "The final model achieved a test MAE of 4.12 MPa "
        "and an R² of 0.881 on unseen concrete recipes."
    )

    st.write(
        "The conservative screening rule selected 18 of 84 "
        "28-day test observations, with no false passes "
        "among those 18. This does not guarantee future performance."
    )

with right:
    st.markdown("**Recommended next steps**")

    st.write(
        "**1.** Conduct repeat laboratory tests of R186."
    )

    st.write(
        "**2.** Compare R133 as a lower-material alternative."
    )

    st.write(
        "**3.** Validate strength, workability, durability, "
        "and project-specific requirements before production."
    )

st.divider()

st.caption(
    "Source: UCI Concrete Compressive Strength Dataset. "
    "Illustrative business requirement: 40 MPa at 28 days. "
    "Decision support only; engineering approval is required."
)
