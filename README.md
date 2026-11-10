# Concrete Mix Performance | Decision Intelligence

**A machine-learning decision-support dashboard for evaluating concrete strength, material efficiency, and laboratory testing priorities.**

**[Explore the Live Dashboard](https://concretemixinsights2026.streamlit.app/)** | [View the Analytical Notebooks](notebooks/)

> ⏳ **Loading Note:** This dashboard may take about a minute to load after a period of inactivity while the server starts. Please keep the page open—it will load automatically.
## The Business Question

Concrete mix selection involves a trade-off: a formulation must meet a required compressive strength, but adding more binder or cement is not necessarily the most efficient choice.

**How can historical test results help identify promising formulations before committing resources to further laboratory trials?**

This project transforms the UCI Concrete Compressive Strength dataset into a management-oriented decision-support workflow. It combines data preparation, exploratory analysis, predictive modeling, conservative screening, and interactive scenario evaluation.

The illustrative business requirement is **40 MPa at 28 days**.

The objective is to prioritize mixtures for laboratory validation—not to certify production-ready designs or claim financial savings without cost data.

## Executive Recommendation

**Prioritize mixture R186 for replicate laboratory testing.**

R186 offers a promising balance between predicted strength and binder quantity. R133 provides a lower-material alternative, while R290 and R322 serve as higher-strength comparison points.

| Mixture | Preliminary decision role | Total binder (kg/m³) | Cross-validated strength (MPa) |
|---|---|---:|---:|
| **R186** | **Priority laboratory candidate** | **399.47** | **52.64** |
| R133 | Lower-material alternative | 390.59 | 49.02 |
| R290 | Higher-strength alternative | 468.80 | 59.64 |
| R322 | High-strength reference | 500.00 | 67.93 |

These strength figures are **out-of-fold cross-validated predictions**, not guaranteed strengths.

R186 recorded a measured 28-day strength of **63.14 MPa**, but one laboratory observation is insufficient for production approval.

Compared with R133, R186 uses approximately **2.3% more binder** while providing **3.62 MPa higher predicted strength**. Material prices and other engineering requirements were unavailable, so the analysis does not establish which formulation has the lowest cost.

## Analytical Workflow

### 1. Data Preparation and Exploratory Analysis

- Started with **1,030 observations** and removed **25 exact duplicate rows**, retaining **1,005 observations**.
- Distinguished unique mixture recipes from repeated measurements at different curing ages.
- Engineered total binder, water-to-binder ratio, and cement replacement percentage for analysis and decision support.
- Identified **417 unique recipes with 28-day measurements**. Of these, **139 (33.3%)** met the illustrative 40 MPa requirement based on recorded laboratory strength.
- Examined **115 identical recipes** tested at both 7 and 28 days. All 115 gained strength, with an average increase of **12.87 MPa**.

The 28-day analysis identified a strong negative Spearman association between **water-to-binder ratio and compressive strength (−0.793)**.

These findings describe historical associations rather than isolated causal effects of changing individual ingredients.

### 2. Predictive Modeling and Validation

Models were developed to estimate compressive strength using seven mixture ingredients and curing age.

To reduce data leakage, observations were separated into training and testing groups based on their **unique mixture formulations**. This prevented measurements of the same recipe from appearing in both sets.

A dummy baseline, linear regression, random forest, and histogram-based gradient boosting were compared using grouped cross-validation.

**Final model: Tuned HistGradientBoostingRegressor**

| Evaluation metric | Result |
|---|---:|
| Training observations | 799 |
| Held-out test observations | 206 |
| Shared recipes across train and test | 0 |
| Cross-validation MAE during tuning | **3.90 MPa** |
| Held-out test MAE | **4.12 MPa** |
| Held-out test RMSE | **6.18 MPa** |
| Held-out test R² | **0.881** |

The grouped testing approach evaluates generalization to previously unseen mixture formulations rather than repeated observations of recipes already encountered during training.

### 3. Conservative Screening and Decision Rules

Prediction accuracy alone is insufficient for selecting mixtures against a strength requirement. An overpredicted formulation could appear to meet the target when its actual strength falls short.

To address this risk, the dashboard uses an **8.02 MPa empirical overprediction buffer**, derived from training cross-validation errors.

For the illustrative 40 MPa requirement:

- **Required strength:** 40.00 MPa
- **Empirical screening buffer:** 8.02 MPa
- **Minimum predicted strength for conservative screening:** 48.02 MPa

On the held-out 28-day test subset, this rule selected **18 of 84 observations**, with **zero false passes among those 18**.

This is a limited historical result—not a guarantee of future performance, an engineering safety factor, or a replacement for independent laboratory validation.

The simulator additionally flags unusual water-to-binder ratios and total material quantities outside historical limits.

## Explore the Dashboard

### Executive Overview

Presents the leading laboratory candidate, key strength and binder measurements, material-efficiency comparisons, model reliability, and recommended management actions.

### Decision Simulator

Allows users to adjust ingredient quantities, curing age, and strength requirements, then evaluate predicted compressive strength and preliminary screening outcomes.

### Mix Comparison

Compares four shortlisted mixtures across binder quantities, cement requirements, and strength predictions to make material-performance trade-offs visible.

### Strength Analysis

Explores historical strength relationships, water-to-binder ratios, qualification rates, and curing-age development.

**Prediction-method distinction:** The Executive Overview displays R186's **52.64 MPa cross-validated prediction**. The Decision Simulator displays **60.79 MPa** for the same 28-day recipe using the final fitted model. The final model was trained on R186, whereas the cross-validation model generating R186's out-of-fold estimate was not.

## Technology Stack

**Python 3.13 · pandas · NumPy · scikit-learn · Plotly · Streamlit · joblib · Jupyter**

## Project Structure

- `dashboard/main.py` — Application entry point and page navigation
- `dashboard/app.py` — Executive Overview
- `dashboard/pages/` — Decision Simulator, Mix Comparison, and Strength Analysis
- `data/` — Source, cleaned, prepared, and decision-support datasets
- `models/` — Saved fitted model and prediction-screening metadata
- `notebooks/` — Data preparation, exploratory analysis, and predictive modeling
- `requirements.txt` — Pinned Python dependencies

### Run Locally

```bash
git clone https://github.com/Selena1224/concrete-performance-dashboard.git
cd concrete-performance-dashboard
py -m pip install -r requirements.txt
py -m streamlit run dashboard/main.py
```

On macOS or Linux, use `python3` instead of `py` if needed.

## Scope and Limitations

This dashboard supports **preliminary analytical decision-making**, not structural engineering certification or automated production approval.

The dataset does not contain material prices, workability, durability, site conditions, or project-specific engineering standards. Historical predictive performance does not guarantee accuracy for novel formulations, particularly when they differ substantially from the training data.

Any shortlisted mixture requires replicate laboratory testing and qualified engineering review before practical use.

## Data Source

[UCI Machine Learning Repository — Concrete Compressive Strength](https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength)

The underlying dataset is attributed to I-Cheng Yeh. The management scenario and screening thresholds are analytical examples, not requirements provided by the original dataset.

---

*Planned additions: dashboard screenshots, a technical methodology report, and a management presentation.*
