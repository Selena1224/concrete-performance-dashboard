
# Import the libraries for the comparison dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from pathlib import Path

# Locate the project folder and load our files
BASE_DIR = Path(__file__).resolve().parents[2]

st.set_page_config(
    page_title="Mix Comparison | Concrete Performance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the management decisions and trained prediction model
df = pd.read_csv(
    BASE_DIR / "data" / "concrete_management_decisions.csv"
)

package = joblib.load(
    BASE_DIR / "models" / "concrete_strength_model.joblib"
)

# Keep our four management options in a consistent order
mix_order = ["R186", "R133", "R290", "R322"]

df = df.set_index("recipe_id").loc[mix_order].reset_index()


# Apply consistent, responsive styling across the dashboard
st.markdown("""
<style>

/* Overall dashboard appearance */
.stApp {
    background-color: #F5F7FB;
}

.block-container {
    max-width: 1350px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #14263D;
}

/* Style KPI cards and enable container-based font sizing */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px;
    min-width: 0;
    container-type: inline-size;
}

/* Allow KPI labels to wrap without truncation */
[data-testid="stMetricLabel"] {
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

/* Scale KPI numbers according to the available card width */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div,
[data-testid="stMetricValue"] > div > div {
    font-size: clamp(1rem, 11cqi, 2.25rem) !important;
    min-width: 0 !important;
    max-width: 100% !important;
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
    font-variant-numeric: tabular-nums;
}

/* Allow comparison indicators to wrap */
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] > div {
    min-width: 0 !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER AND COMPARISON SETTINGS
# --------------------------------------------------

st.title("Concrete Mix Comparison")

st.write(
    "Compare material requirements and predicted strength "
    "to evaluate which mixtures deserve further testing."
)

# Allow management to choose an alternative to R186
alternative = st.selectbox(
    "Compare R186 against",
    ["R133", "R290", "R322"],
    format_func=lambda x: {
        "R133": "R133 — Lower material use",
        "R290": "R290 — Higher-strength alternative",
        "R322": "R322 — High-strength reference"
    }[x]
)

# Let management distinguish two different prediction methods
prediction_method = st.radio(
    "Strength estimate",
    ["Cross-validated", "Final fitted model"],
    horizontal=True
)

# Use historical out-of-fold predictions or calculate
# predictions with the final fitted model
if prediction_method == "Cross-validated":
    df["display_strength"] = df["predicted_strength_mpa"]

else:
    # All four mixtures were evaluated at 28 days
    model_inputs = df.reindex(columns=package["features"]).copy()
    model_inputs["age_days"] = 28

    # Match the exact feature order used during training
    model_inputs = model_inputs[package["features"]]

    df["display_strength"] = package["model"].predict(model_inputs)

# Explain the difference between the two estimates
if prediction_method == "Cross-validated":
    st.caption(
        "These are historical out-of-fold predictions. "
        "Each recipe was predicted by a model that had not "
        "trained on that recipe."
    )
else:
    st.caption(
        "These predictions use the final fitted model, "
        "which also powers the Decision Simulator. "
        "The four historical mixtures were included "
        "in its training data."
    )

# Select the two mixtures for the detailed comparison
reference = df.set_index("recipe_id").loc["R186"]
selected = df.set_index("recipe_id").loc[alternative]

# --------------------------------------------------
# KEY BUSINESS METRICS
# --------------------------------------------------

st.divider()
st.subheader(f"01 | R186 vs. {alternative}")

# Calculate the differences relative to R186
binder_diff = selected["total_binder"] - reference["total_binder"]
cement_diff = selected["cement"] - reference["cement"]

strength_diff = (
    selected["display_strength"] - reference["display_strength"]
)

binder_pct = (
    binder_diff / reference["total_binder"]
) * 100

# Present the trade-offs as management metrics
c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Binder Difference",
        f"{binder_diff:+.2f} kg/m³",
        delta=f"{binder_pct:+.1f}% vs R186",
        delta_color="inverse"
    )

with c2:
    st.metric(
        "Cement Difference",
        f"{cement_diff:+.2f} kg/m³",
        delta_color="off"
    )

with c3:
    st.metric(
        "Predicted Strength Difference",
        f"{strength_diff:+.2f} MPa",
        delta_color="off"
    )

# --------------------------------------------------
# CHART 1: MATERIAL USE VS. STRENGTH
# --------------------------------------------------

st.divider()
st.subheader("02 | Material Use vs. Predicted Strength")

# Give each mixture a consistent color
mix_colors = {
    "R186": "#008F80",
    "R133": "#4178A9",
    "R290": "#E6A23C",
    "R322": "#8B78B7"
}

# Compare all four mixtures on the same chart
fig = px.scatter(
    df,
    x="total_binder",
    y="display_strength",
    color="recipe_id",
    text="recipe_id",
    color_discrete_map=mix_colors,
    hover_data=[
        "cement",
        "slag",
        "fly_ash",
        "replacement_pct"
    ],
    labels={
        "total_binder": "Total Binder (kg/m³)",
        "display_strength": "Predicted Strength (MPa)",
        "recipe_id": "Mixture"
    }
)

fig.update_traces(
    marker=dict(
        size=19,
        line=dict(color="white", width=2)
    ),
    textposition="top center"
)

# Add the example business requirement
fig.add_hline(
    y=40,
    line_dash="dot",
    line_color="#64748B",
    annotation_text="40 MPa target"
)

# Add the empirical conservative screening cutoff
fig.add_hline(
    y=40 + package["prediction_buffer_mpa"],
    line_dash="dash",
    line_color="#008F80",
    annotation_text="Screening cutoff"
)

fig.update_layout(
    template="plotly_white",
    height=440,
    legend=dict(orientation="h", y=-0.2),
    margin=dict(l=20, r=20, t=40, b=30)
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "The screening cutoff is based on training cross-validation "
    "errors and is intended for preliminary prioritization, "
    "not engineering approval."
)

# --------------------------------------------------
# CHART 2: BINDER COMPOSITION
# --------------------------------------------------

st.divider()
st.subheader("03 | Binder Composition")

# Reshape the ingredient data for a stacked bar chart
binder_data = df.melt(
    id_vars=["recipe_id"],
    value_vars=["cement", "slag", "fly_ash"],
    var_name="Ingredient",
    value_name="Quantity"
)

# Make ingredient names easier to read
binder_data["Ingredient"] = binder_data["Ingredient"].replace({
    "cement": "Cement",
    "slag": "Blast Furnace Slag",
    "fly_ash": "Fly Ash"
})

# Show how much of each binder ingredient the recipes use
fig_binder = px.bar(
    binder_data,
    x="recipe_id",
    y="Quantity",
    color="Ingredient",
    barmode="stack",
    category_orders={"recipe_id": mix_order},
    color_discrete_map={
        "Cement": "#193652",
        "Blast Furnace Slag": "#008F80",
        "Fly Ash": "#E6A23C"
    },
    labels={
        "recipe_id": "Concrete Mixture",
        "Quantity": "Ingredient Quantity (kg/m³)"
    }
)

fig_binder.update_layout(
    template="plotly_white",
    height=420,
    legend=dict(orientation="h", y=-0.2),
    margin=dict(l=20, r=20, t=30, b=30)
)

st.plotly_chart(fig_binder, use_container_width=True)

st.caption(
    "This chart shows binder composition only. "
    "Aggregates, water, and superplasticizer are excluded. "
    "Lower cement or binder content does not automatically "
    "mean lower material cost."
)

# --------------------------------------------------
# FULL MIXTURE COMPARISON TABLE
# --------------------------------------------------

st.divider()
st.subheader("04 | Complete Mixture Comparison")

# Present the key measurements in one table
comparison_table = df[
    [
        "recipe_id",
        "cement",
        "slag",
        "fly_ash",
        "water",
        "superplasticizer",
        "coarse_aggregate",
        "fine_aggregate",
        "total_binder",
        "replacement_pct",
        "display_strength",
        "actual_strength_mpa"
    ]
].copy()

# Rename the columns for business users
comparison_table.columns = [
    "Mix",
    "Cement",
    "Slag",
    "Fly Ash",
    "Water",
    "Superplasticizer",
    "Coarse Aggregate",
    "Fine Aggregate",
    "Total Binder",
    "Replacement %",
    "Predicted MPa",
    "Observed MPa"
]

st.dataframe(
    comparison_table.round(2),
    hide_index=True,
    use_container_width=True
)

# --------------------------------------------------
# MANAGEMENT RECOMMENDATION
# --------------------------------------------------

st.divider()
st.subheader("05 | Management Recommendation")

st.success(
    "PRIORITY — R186: Advance to replicate laboratory testing "
    "as the preliminary balanced candidate."
)

st.write(
    "**R133:** Investigate as the lower-material alternative. "
    "It uses slightly less binder and considerably less cement "
    "than R186, but has a lower cross-validated strength estimate."
)

st.write(
    "**R290:** Retain as a higher-strength alternative "
    "if additional strength margin becomes a priority."
)

st.write(
    "**R322:** Use as a high-strength reference. "
    "Its additional cement content is not currently justified "
    "by the illustrative 40 MPa requirement alone."
)

st.caption(
    "The recommendations prioritize laboratory testing, "
    "not production approval. Each mixture has only one "
    "recorded 28-day strength measurement. Material prices, "
    "durability, workability, and project specifications "
    "are not available in this dataset."
)
