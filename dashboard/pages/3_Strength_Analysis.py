
# ============================================================
# CONCRETE STRENGTH ANALYSIS
# Historical performance and management decision support
# ============================================================

# Import libraries for data analysis and visualization
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Locate the main project folder
BASE_DIR = Path(__file__).resolve().parents[2]

# Load the prepared concrete dataset
df = pd.read_csv(
    BASE_DIR / "data" / "concrete_prepared.csv"
)

# Configure the dashboard page
st.set_page_config(
    page_title="Strength Analysis | Concrete Performance",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #14263D;
}

/* Style KPI cards and enable responsive font sizing */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px;
    min-width: 0;
    container-type: inline-size;
}

/* Wrap all KPI labels without truncation */
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

/* Adjust KPI number sizes to the available card width */
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

/* Allow metric comparison indicators to wrap */
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] > div {
    min-width: 0 !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
}

</style>
""", unsafe_allow_html=True)



# ============================================================
# PAGE HEADER
# ============================================================

st.title("Concrete Strength Analysis")

st.write(
    "Examine how material composition and curing age relate "
    "to compressive strength and identify opportunities "
    "for better mixture selection."
)

# List the seven ingredients that define each concrete recipe
ingredients = [
    "cement",
    "slag",
    "fly_ash",
    "water",
    "superplasticizer",
    "coarse_aggregate",
    "fine_aggregate"
]


# ============================================================
# SECTION 1 — WHAT DRIVES 28-DAY STRENGTH?
# ============================================================

st.divider()
st.subheader("01 | What Drives 28-Day Strength?")

# Focus on recipes tested at 28 days
# Keeping curing age constant makes ingredient comparisons clearer
df_28 = df[df["age_days"] == 28].copy()

# Average repeated measurements of the same recipe
# Each unique recipe appears once in this analysis
df_28 = (
    df_28.groupby(ingredients, as_index=False)
    .agg(strength_mpa=("strength_mpa", "mean"))
)

# Calculate the total binder content
df_28["total_binder"] = (
    df_28["cement"]
    + df_28["slag"]
    + df_28["fly_ash"]
)

# Calculate water-to-binder ratio
df_28["water_binder_ratio"] = (
    df_28["water"] / df_28["total_binder"]
)

# Calculate Spearman correlations with concrete strength
# These describe associations, not cause-and-effect relationships
wb_corr = df_28["water_binder_ratio"].corr(
    df_28["strength_mpa"],
    method="spearman"
)

binder_corr = df_28["total_binder"].corr(
    df_28["strength_mpa"],
    method="spearman"
)

# Display the key statistical findings
c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "28-Day Recipes",
        f"{len(df_28):,}"
    )

with c2:
    st.metric(
        "Water-to-Binder Correlation",
        f"{wb_corr:.3f}"
    )

with c3:
    st.metric(
        "Total Binder Correlation",
        f"{binder_corr:+.3f}"
    )

st.write(
    "Water-to-binder ratio shows a strong negative relationship "
    "with 28-day strength. Higher binder content is also associated "
    "with higher strength, although these relationships do not "
    "establish causation."
)


# ============================================================
# INTERACTIVE STRENGTH REQUIREMENT
# ============================================================

st.markdown("#### Evaluate a Strength Requirement")

# Allow management to change the required concrete strength
# All target-related figures below update automatically
target = st.slider(
    "Strength requirement for comparison (MPa)",
    min_value=20,
    max_value=70,
    value=40,
    step=5
)

# Identify which historical 28-day recipes meet the target
# True means the measured strength is at least the selected target
df_28["meets_target"] = (
    df_28["strength_mpa"] >= target
)

# Count the number of qualifying recipes
qualifying_recipes = int(df_28["meets_target"].sum())

# Calculate the proportion of recipes meeting the requirement
qualification_rate = (
    qualifying_recipes / len(df_28)
) * 100

# Display the business impact of changing the target
k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        "Selected Strength Target",
        f"{target} MPa"
    )

with k2:
    st.metric(
        "Recipes Meeting Target",
        f"{qualifying_recipes:,} / {len(df_28):,}"
    )

with k3:
    st.metric(
        "Qualification Rate",
        f"{qualification_rate:.1f}%"
    )

st.caption(
    "Qualification is based on historical 28-day laboratory "
    "measurements. These percentages do not represent "
    "guaranteed future production performance."
)


# ============================================================
# CHART 1 — WATER-TO-BINDER RATIO VS. STRENGTH
# ============================================================

st.write("")
st.subheader("Water-to-Binder Ratio vs. Strength")

# Plot the relationship between water-to-binder ratio and strength
# Color indicates how much total binder each recipe contains
fig = px.scatter(
    df_28,
    x="water_binder_ratio",
    y="strength_mpa",
    color="total_binder",
    color_continuous_scale="Tealgrn",
    hover_data={
        "cement": ":.2f",
        "slag": ":.2f",
        "fly_ash": ":.2f",
        "water": ":.2f",
        "water_binder_ratio": ":.3f",
        "total_binder": ":.2f",
        "strength_mpa": ":.2f"
    },
    labels={
        "water_binder_ratio": "Water-to-Binder Ratio",
        "strength_mpa": "Measured Strength (MPa)",
        "total_binder": "Binder (kg/m³)"
    }
)

# Add a horizontal line for the selected strength requirement
# The line moves automatically when management changes the slider
fig.add_hline(
    y=target,
    line_dash="dash",
    line_color="#D97706",
    annotation_text=f"{target} MPa requirement"
)

# Improve the appearance of the scatter plot
fig.update_traces(
    marker=dict(
        size=9,
        opacity=0.75
    )
)

fig.update_layout(
    template="plotly_white",
    height=480,
    margin=dict(l=20, r=20, t=35, b=30),
    font=dict(color="#334155")
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Each point represents one unique concrete recipe tested "
    "at 28 days. The relationship is observational and does "
    "not isolate the effect of changing water alone."
)


# ============================================================
# SECTION 2 — COMPARE MIXTURE PERFORMANCE
# ============================================================

st.divider()
st.subheader("02 | Compare Mixture Performance")

# Divide recipes into three groups based on water-to-binder ratio
# Each group contains approximately one-third of the recipes
df_28["wb_group"] = pd.qcut(
    df_28["water_binder_ratio"],
    q=3,
    labels=["Low", "Medium", "High"]
)

# Calculate the strength and target achievement of each group
# The target rate changes when the strength requirement changes
group_summary = (
    df_28.groupby("wb_group", observed=True)
    .agg(
        recipe_count=("strength_mpa", "count"),
        median_strength=("strength_mpa", "median"),
        target_rate=("meets_target", "mean"),
        min_ratio=("water_binder_ratio", "min"),
        max_ratio=("water_binder_ratio", "max")
    )
    .reset_index()
)

# Convert target achievement to a percentage
group_summary["target_rate"] *= 100

# Compare median strength across the three ratio groups
fig_group = px.bar(
    group_summary,
    x="wb_group",
    y="median_strength",
    color="wb_group",
    text_auto=".1f",
    color_discrete_map={
        "Low": "#008F80",
        "Medium": "#4178A9",
        "High": "#E6A23C"
    },
    labels={
        "wb_group": "Water-to-Binder Group",
        "median_strength": "Median Strength (MPa)"
    }
)

# Show the selected requirement on the bar chart
fig_group.add_hline(
    y=target,
    line_dash="dot",
    line_color="#64748B",
    annotation_text=f"{target} MPa"
)

fig_group.update_layout(
    template="plotly_white",
    height=390,
    showlegend=False,
    margin=dict(l=20, r=20, t=35, b=25)
)

st.plotly_chart(fig_group, use_container_width=True)

# Show the sample sizes and qualification percentages
# This table updates when the target changes
group_table = group_summary.rename(columns={
    "wb_group": "Ratio Group",
    "recipe_count": "Recipes",
    "median_strength": "Median Strength (MPa)",
    "target_rate": "Meeting Target (%)",
    "min_ratio": "Minimum Ratio",
    "max_ratio": "Maximum Ratio"
})

st.dataframe(
    group_table.round(2),
    hide_index=True,
    use_container_width=True
)

st.caption(
    "The bar chart shows historical median strength for each "
    "group. The qualification percentages in the table change "
    "with the selected target; the historical median values do not."
)


# ============================================================
# SECTION 3 — CURING AGE AND STRENGTH DEVELOPMENT
# ============================================================

st.divider()
st.subheader("03 | How Does Strength Develop Over Time?")

# Calculate average strength for each recipe at each curing age
# Repeated tests of an identical recipe at the same age are averaged
mix_age_strength = (
    df.groupby(
        ingredients + ["age_days"],
        as_index=False
    )
    .agg(strength_mpa=("strength_mpa", "mean"))
)

# Reshape the data so curing ages become separate columns
strength_by_age = mix_age_strength.pivot(
    index=ingredients,
    columns="age_days",
    values="strength_mpa"
)

# Select recipes tested at both 7 and 28 days
# This makes the comparison more meaningful than using unrelated recipes
paired = strength_by_age[[7, 28]].dropna().copy()

paired.columns = [
    "strength_7d",
    "strength_28d"
]

# Calculate strength gain between the two curing ages
paired["strength_gain"] = (
    paired["strength_28d"] - paired["strength_7d"]
)

# Summarize strength development
avg_gain = paired["strength_gain"].mean()
median_gain = paired["strength_gain"].median()
increased = int((paired["strength_gain"] > 0).sum())

# Display the most important curing-age findings
a1, a2, a3 = st.columns(3)

with a1:
    st.metric(
        "Paired Recipes",
        len(paired)
    )

with a2:
    st.metric(
        "Average Strength Gain",
        f"+{avg_gain:.2f} MPa"
    )

with a3:
    st.metric(
        "Recipes With Increased Strength",
        f"{increased} / {len(paired)}"
    )

# Calculate the average strength at each curing age
# Only recipes with measurements at BOTH ages are included
paired_chart = pd.DataFrame({
    "Curing Age": ["7 days", "28 days"],
    "Average Strength": [
        paired["strength_7d"].mean(),
        paired["strength_28d"].mean()
    ]
})

# Compare strength development visually
fig_age = px.bar(
    paired_chart,
    x="Curing Age",
    y="Average Strength",
    color="Curing Age",
    text_auto=".2f",
    color_discrete_map={
        "7 days": "#4178A9",
        "28 days": "#008F80"
    },
    labels={
        "Average Strength": "Average Strength (MPa)"
    }
)

fig_age.update_layout(
    template="plotly_white",
    height=390,
    showlegend=False,
    margin=dict(l=20, r=20, t=35, b=25)
)

st.plotly_chart(fig_age, use_container_width=True)

st.caption(
    f"Based on {len(paired)} identical recorded recipes "
    f"tested at both 7 and 28 days. "
    f"Median strength gain: {median_gain:.2f} MPa. "
    "These results do not establish when a mixture "
    "can safely be released for construction."
)


# ============================================================
# SECTION 4 — MANAGEMENT IMPLICATIONS
# ============================================================

st.divider()
st.subheader("04 | Implications for Management")

# Recommendation 1 — Material composition
st.markdown(
    "**Prioritize mixture composition.** "
    "Water-to-binder ratio has a strong relationship with "
    "28-day strength. Evaluate the complete formulation "
    "rather than adjusting water or cement independently."
)

# Recommendation 2 — Material efficiency
st.markdown(
    "**Evaluate material efficiency.** "
    "Some historical recipes achieved the required strength "
    "with different binder quantities. Compare promising "
    "formulations through controlled laboratory testing."
)

# Recommendation 3 — Curing decisions
st.markdown(
    "**Validate curing decisions.** "
    "Strength increased between 7 and 28 days for all "
    "115 paired recipes. Any change to production or "
    "release schedules requires project-specific testing "
    "and engineering review."
)

st.divider()

# Identify the source and limitations
st.caption(
    "Source: UCI Concrete Compressive Strength Dataset. "
    "Historical associations are not causal estimates. "
    "This dashboard supports preliminary mixture evaluation, "
    "not engineering certification or production approval."
)
