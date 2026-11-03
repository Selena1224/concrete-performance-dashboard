
# Import the libraries we need
import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from pathlib import Path

# Locate the project folder
BASE_DIR = Path(__file__).resolve().parents[2]

# Set up this dashboard page
st.set_page_config(
    page_title="Mix Simulator | Concrete Performance",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load our prepared data, management options, and trained model
df = pd.read_csv(BASE_DIR / "data" / "concrete_prepared.csv")
decisions = pd.read_csv(
    BASE_DIR / "data" / "concrete_management_decisions.csv"
)
package = joblib.load(
    BASE_DIR / "models" / "concrete_strength_model.joblib"
)

model = package["model"]
features = package["features"]
buffer = package["prediction_buffer_mpa"]

# Use R186 as our reference mixture
reference = decisions.set_index("recipe_id").loc["R186"]

# Apply the same colors used in our executive dashboard
# Keep the dashboard styling consistent across pages
# Apply consistent styling to every metric card on this page
# Keep all CSS inside one pair of <style> tags
st.markdown("""
<style>
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

/* Style each KPI card and measure text relative to that card's width */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
    min-width: 0;
    container-type: inline-size;
}

/* Wrap complete metric labels rather than cutting them off */
[data-testid="stMetricLabel"] {
    height: auto !important;
    min-height: 2.8em;
    min-width: 0 !important;
    overflow: visible !important;
}

[data-testid="stMetricLabel"] > div {
    min-width: 0 !important;
    max-width: 100% !important;
}

[data-testid="stMetricLabel"] p {
    white-space: normal !important;
    overflow: visible !important;
    overflow-wrap: break-word !important;
    text-overflow: clip !important;
    line-height: 1.4 !important;
}

/* Scale displayed numbers with the card width, including nested text */
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

/* Allow comparison text below the number to wrap too */
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] > div {
    min-width: 0 !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
}
</style>
""", unsafe_allow_html=True)



# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("Concrete Mix Decision Simulator")
st.write(
    "Adjust material quantities and curing time to evaluate "
    "potential concrete mixtures before laboratory testing."
)

st.info(
    "Reference mixture: R186 — our recommended starting point "
    "for laboratory validation."
)

# Reset all inputs to the original R186 mixture
def reset_to_reference():

    # Restore the seven ingredient quantities
    for ingredient in [
        "cement", "slag", "fly_ash", "water",
        "superplasticizer", "coarse_aggregate", "fine_aggregate"
    ]:
        st.session_state[f"mix_{ingredient}"] = float(reference[ingredient])

    # Restore the original curing age and strength target
    st.session_state["mix_age"] = 28
    st.session_state["mix_target"] = 40.0


# Add a button that restores the original settings
st.button(
    "↺ Reset to R186",
    on_click=reset_to_reference
)

# --------------------------------------------------
# INGREDIENT INPUTS
# --------------------------------------------------

st.subheader("01 | Configure Your Mixture")

# Ingredient quantities are measured in kg/m³
ingredients = [
    "cement",
    "slag",
    "fly_ash",
    "water",
    "superplasticizer",
    "coarse_aggregate",
    "fine_aggregate"
]

# Display two columns for a cleaner input layout
left, right = st.columns(2, gap="large")

# Store the values entered by management
inputs = {}

for i, ingredient in enumerate(ingredients):

    # Display the inputs in two columns
    container = left if i < 4 else right

    with container:

        # Keep individual ingredient values within observed ranges
        # This does not guarantee the combined mixture is practical
        inputs[ingredient] = st.number_input(
            ingredient.replace("_", " ").title() + " (kg/m³)",
            min_value=float(df[ingredient].min()),
            max_value=float(df[ingredient].max()),
            value=float(reference[ingredient]),
            step=1.0,
            format="%.2f",
            key=f"mix_{ingredient}"
        )

# Let management adjust curing time and required strength
# Select the curing age, starting at 28 days
age = st.slider(
    "Curing age (days)",
    min_value=1,
    max_value=365,
    value=28,
    key="mix_age"
)

# Set the required strength, starting at 40 MPa
target = st.number_input(
    "Required strength (MPa)",
    min_value=10.0,
    max_value=80.0,
    value=40.0,
    step=5.0,
    key="mix_target"
)

# Add curing age to the model inputs
inputs["age_days"] = age

# --------------------------------------------------
# CALCULATE MIXTURE CHARACTERISTICS
# --------------------------------------------------

# Calculate binder and water-to-binder ratio
binder = inputs["cement"] + inputs["slag"] + inputs["fly_ash"]
water_binder_ratio = inputs["water"] / binder

# Calculate cement replacement percentage
replacement_pct = (
    (inputs["slag"] + inputs["fly_ash"]) / binder
) * 100

# Predict strength using our saved model
# Use the same feature order as during training
scenario = pd.DataFrame([inputs], columns=features)

predicted_strength = float(model.predict(scenario)[0])

# Calculate the conservative screening estimate
# This is an empirical buffer, not a certified safety factor
conservative_estimate = predicted_strength - buffer

# Compare with R186 at the SAME curing age
reference_inputs = {
    feature: (
        age if feature == "age_days"
        else float(reference[feature])
    )
    for feature in features
}

reference_df = pd.DataFrame(
    [reference_inputs], columns=features
)

reference_prediction = float(model.predict(reference_df)[0])

# Calculate how much binder the reference mixture uses
reference_binder = float(reference["total_binder"])

# Check whether total material quantity is within observed limits
# This is only a basic plausibility check
total_material = sum(inputs[item] for item in ingredients)
historical_totals = df[ingredients].sum(axis=1)

within_observed_total = (
    historical_totals.min()
    <= total_material
    <= historical_totals.max()
)

# --------------------------------------------------
# SCENARIO RESULTS
# --------------------------------------------------

st.divider()
st.subheader("02 | Predicted Performance")
# Clarify why this prediction differs from the Executive Overview
# The Executive Overview uses a historical cross-validated prediction
# The simulator uses the final model fitted on the training dataset
st.caption(
    "Simulator estimates use the final fitted model. "
    f"R186's historical cross-validated prediction at 28 days was "
    f"{reference['predicted_strength_mpa']:.2f} MPa. "
    "The estimates differ because the cross-validated model "
    "did not train on R186, while the final model did."
)

m1, m2, m3 = st.columns(3)

# Calculate the difference from R186
# Round to prevent displaying +0.00 or -0.00
strength_change = round(
    predicted_strength - reference_prediction, 2
)

# Show the strength comparison without unnecessary zero values
with m1:
    st.metric(
        "Predicted Strength",
        f"{predicted_strength:.2f} MPa",
        delta=(
            f"{strength_change:+.2f} MPa vs R186"
            if strength_change != 0
            else "Same as R186"
        ),
        delta_color="off" if strength_change == 0 else "normal"
    )

# Calculate the binder difference from R186
# Round to avoid displaying -0.00 from floating-point calculations
binder_change = round(binder - reference_binder, 2)

# Display binder quantity with the unit in the label
# This prevents the value from being cut off in the KPI card
with m2:
    st.metric(
        "Total Binder (kg/m³)",
        f"{binder:,.2f}",
        delta=(
            f"{binder_change:+,.2f} vs R186"
            if binder_change != 0
            else "Same as R186"
        ),
        delta_color=(
            "off" if binder_change == 0 else "inverse"
        )
    )


with m3:
    st.metric(
        "Conservative Screening Estimate",
        f"{conservative_estimate:.2f} MPa"
    )

# Show additional properties of the selected formulation
a, b = st.columns(2)

with a:
    st.metric("Water-to-Binder Ratio", f"{water_binder_ratio:.3f}")

with b:
    st.metric("Cement Replacement", f"{replacement_pct:.1f}%")

# --------------------------------------------------
# MANAGEMENT SCREENING ASSESSMENT
# --------------------------------------------------

st.subheader("03 | Decision Assessment")


# Identify water-to-binder ratios outside the central 90%
# of the historical dataset. This is a screening rule,
# not a construction or engineering standard.
wb_lower = df["water_binder_ratio"].quantile(0.05)
wb_upper = df["water_binder_ratio"].quantile(0.95)

outside_typical_wb = not (
    wb_lower <= water_binder_ratio <= wb_upper
)

# Flag unusual mixtures before considering laboratory priority
if not within_observed_total:
    st.error(
        "OUTSIDE HISTORICAL MATERIAL RANGE — "
        "The combined material quantity falls outside the "
        "dataset's observed range. Do not shortlist without review."
    )

elif outside_typical_wb:
    st.warning(
        "UNUSUAL MIXTURE PROPORTIONS — "
        f"The water-to-binder ratio is {water_binder_ratio:.3f}, "
        f"outside the central 90% of historical values "
        f"({wb_lower:.3f}–{wb_upper:.3f}). "
        "Technical review is required before shortlisting."
    )

    # Still identify mixtures that fail the strength target
    if predicted_strength < target:
        st.error(
            "BELOW SCREENING REQUIREMENT — "
            "The predicted strength is below the selected target."
        )

# Prioritize mixtures that pass the conservative screening requirement
# Only mixtures with typical proportions reach this condition
elif conservative_estimate >= target:
    st.success(
        "PRIORITY FOR LABORATORY VALIDATION — "
        "The prediction exceeds the target after applying "
        "the empirical screening buffer."
    )
elif predicted_strength >= target:

    st.warning(
        "FURTHER REVIEW REQUIRED — "
        "The predicted strength meets the target, but the "
        "conservative screening estimate does not."
    )

else:

    st.error(
        "BELOW SCREENING REQUIREMENT — "
        "The predicted strength is below the selected target."
    )

# --------------------------------------------------
# STRENGTH COMPARISON CHART
# --------------------------------------------------

st.subheader("04 | Compare With R186")

# Compare the adjusted mixture with our reference
chart_data = pd.DataFrame({
    "Mix": ["R186 Reference", "Adjusted Mixture"],
    "Predicted Strength": [
        reference_prediction,
        predicted_strength
    ]
})

fig = px.bar(
    chart_data,
    x="Mix",
    y="Predicted Strength",
    color="Mix",
    text_auto=".2f",
    color_discrete_map={
        "R186 Reference": "#4178A9",
        "Adjusted Mixture": "#008F80"
    }
)

# Add the required strength and conservative screening threshold
fig.add_hline(
    y=target,
    line_dash="dot",
    line_color="#64748B",
    annotation_text="Required strength"
)

fig.add_hline(
    y=target + buffer,
    line_dash="dash",
    line_color="#008F80",
    annotation_text="Screening cutoff"
)

fig.update_layout(
    template="plotly_white",
    height=400,
    showlegend=False,
    yaxis_title="Predicted Strength (MPa)",
    xaxis_title="",
    font=dict(family="Arial", color="#334155"),
    margin=dict(l=20, r=20, t=35, b=30)
)

st.plotly_chart(fig, use_container_width=True)

# Explain what the model can and cannot establish
st.caption(
    "Both bars use the final fitted model at the selected curing age. "
    "These predictions may differ from historical cross-validation estimates. "
    "Individual ingredient ranges and total material checks do not establish "
    "mixture feasibility. Predictions cannot replace laboratory testing, "
    "engineering review, or verification of workability and durability."
)
