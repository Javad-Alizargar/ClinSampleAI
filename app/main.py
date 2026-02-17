# ==========================================
# ClinSample AI — Streamlit App (Educational v3)
# ==========================================

import sys
import os

# --------------------------------------------------
# Fix import path for Streamlit Cloud
# --------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import streamlit as st

# Continuous calculators
from calculators.continuous.one_sample_mean import calculate_one_sample_mean
from calculators.continuous.two_independent_means import calculate_two_independent_means
from calculators.continuous.paired_mean import calculate_paired_mean
from calculators.continuous.anova_oneway import calculate_anova_oneway

# Templates
from templates.paragraph_templates import (
    paragraph_one_sample_mean,
    paragraph_two_independent_means,
    paragraph_paired_mean,
    paragraph_anova
)

# --------------------------------------------------
st.set_page_config(page_title="ClinSample AI", layout="centered")

st.title("ClinSample AI — Sample Size Calculator")
st.markdown("Evidence-based, thesis-ready sample size planning with educational guidance.")

# --------------------------------------------------
study_type = st.selectbox(
    "Select Study Type",
    [
        "One-Sample Mean",
        "Two Independent Means",
        "Paired Mean",
        "One-Way ANOVA",
    ]
)

# Sidebar global settings
st.sidebar.header("Statistical Parameters")

alpha = st.sidebar.number_input("Alpha (Type I error)", 0.001, 0.2, 0.05, 0.001)
power = st.sidebar.number_input("Power (1 - Beta)", 0.5, 0.99, 0.8, 0.01)
dropout_rate = st.sidebar.number_input("Dropout Rate (0–1)", 0.0, 0.9, 0.0, 0.01)
two_sided = st.sidebar.checkbox("Two-sided test", True)

# ==========================================================
# ONE SAMPLE MEAN
# ==========================================================
if study_type == "One-Sample Mean":

    st.header("One-Sample Mean")

    with st.expander("📘 When to Use This Design"):
        st.markdown("""
Used when comparing a sample mean to a known reference value.

**Example:**  
Testing whether the mean fasting glucose level in a clinic differs from 
the national average of 100 mg/dL.
        """)

    with st.expander("📊 Understanding the Parameters"):
        st.markdown("""
**Standard Deviation (SD):**
- Reflects variability of the outcome.
- Obtain from:
  - Published literature
  - Pilot study
  - Previous datasets
- If uncertain, use conservative (larger) estimate.

**Mean Difference (Δ):**
- Clinically meaningful difference.
- Should be justified based on:
  - Clinical relevance
  - Regulatory standards
  - Prior trials
        """)

    sd = st.number_input("Standard Deviation (SD)", 0.0001, value=1.0)
    delta = st.number_input("Clinically Meaningful Difference (Δ)", 0.0001, value=0.5)

    if st.button("Calculate Sample Size"):
        result = calculate_one_sample_mean(alpha, power, sd, delta, two_sided, dropout_rate)
        st.success(f"Required Sample Size: {result['n_required']}")
        st.write("Before Dropout:", result["n_before_dropout"])

        paragraph = paragraph_one_sample_mean(
            alpha, power, sd, delta, two_sided,
            dropout_rate, result["n_required"]
        )
        st.code(paragraph)


# ==========================================================
# TWO INDEPENDENT MEANS
# ==========================================================
elif study_type == "Two Independent Means":

    st.header("Two Independent Means")

    with st.expander("📘 When to Use This Design"):
        st.markdown("""
Used when comparing means between two independent groups.

**Example:**  
Comparing mean HbA1c between treatment and placebo groups.
        """)

    with st.expander("📊 Parameter Guidance"):
        st.markdown("""
**Common SD:**
- Estimate pooled SD from literature.
- If groups differ greatly, reconsider design.

**Mean Difference (Δ):**
- Define minimal clinically important difference.

**Allocation Ratio:**
- 1.0 = equal groups
- >1 = more participants in group 2
        """)

    sd = st.number_input("Common SD", 0.0001, value=1.0)
    delta = st.number_input("Expected Mean Difference (Δ)", 0.0001, value=0.5)
    ratio = st.number_input("Allocation Ratio (n2/n1)", 0.1, value=1.0)

    if st.button("Calculate Sample Size"):
        result = calculate_two_independent_means(alpha, power, sd, delta, ratio, two_sided, dropout_rate)

        st.success(f"Group 1: {result['n_group1']} | Group 2: {result['n_group2']}")
        st.write("Total Sample Size:", result["n_total"])

        paragraph = paragraph_two_independent_means(
            alpha, power, sd, delta, ratio,
            two_sided, dropout_rate,
            result["n_group1"], result["n_group2"]
        )
        st.code(paragraph)


# ==========================================================
# PAIRED MEAN
# ==========================================================
elif study_type == "Paired Mean":

    st.header("Paired Mean")

    with st.expander("📘 When to Use This Design"):
        st.markdown("""
Used when measurements are taken on the same participants twice.

**Example:**  
Blood pressure before and after intervention.
        """)

    with st.expander("📊 Parameter Guidance"):
        st.markdown("""
**SD of Differences (SDd):**
- NOT the raw SD.
- Must compute SD of within-subject differences.
- Often smaller than independent SD.
        """)

    sd_diff = st.number_input("SD of Differences", 0.0001, value=1.0)
    delta = st.number_input("Mean Difference (Δ)", 0.0001, value=0.5)

    if st.button("Calculate Sample Size"):
        result = calculate_paired_mean(alpha, power, sd_diff, delta, two_sided, dropout_rate)
        st.success(f"Required Sample Size: {result['n_required']}")

        paragraph = paragraph_paired_mean(
            alpha, power, sd_diff, delta,
            two_sided, dropout_rate,
            result["n_required"]
        )
        st.code(paragraph)


# ==========================================================
# ONE-WAY ANOVA
# ==========================================================
elif study_type == "One-Way ANOVA":

    import math

    st.header("One-Way ANOVA")

    # --------------------------------------------------
    with st.expander("📘 When to Use One-Way ANOVA"):
        st.markdown("""
Used when comparing means across three or more independent groups.

Example:
Comparing cholesterol levels across 3 dietary regimens.
        """)

    # --------------------------------------------------
    with st.expander("📐 What is Cohen’s f? (Effect Size)"):
        st.write("Cohen’s f measures standardized separation between group means.")

        st.write("Relationship with eta-squared:")
        st.latex(r"f = \sqrt{\frac{\eta^2}{1 - \eta^2}}")

        st.write("Interpretation guidelines:")
        st.write("• 0.10 = Small effect")
        st.write("• 0.25 = Medium effect")
        st.write("• 0.40 = Large effect")

    # --------------------------------------------------
    with st.expander("🧮 Compute Cohen’s f from Group Means and SD"):

        st.write("Assumptions:")
        st.write("• Equal group sizes")
        st.write("• Similar SD across groups")

        st.write("Formula used:")

        st.latex(r"\bar{\mu} = \frac{\sum \mu_i}{k}")
        st.latex(r"SS_{between} = \sum (\mu_i - \bar{\mu})^2")
        st.latex(r"f = \frac{\sqrt{SS_{between}/k}}{SD}")

        k_est = st.number_input("Number of Groups for f Estimation", min_value=2, value=3)

        means = []
        for i in range(int(k_est)):
            m = st.number_input(f"Mean of Group {i+1}", value=0.0, key=f"mean_{i}")
            means.append(m)

        sd_common = st.number_input("Common SD (or average SD)", min_value=0.0001, value=1.0)

        if st.button("Compute Cohen's f from Means"):

            grand_mean = sum(means) / len(means)
            ss_between = sum((m - grand_mean) ** 2 for m in means)
            variance_between = ss_between / len(means)
            f_calculated = math.sqrt(variance_between) / sd_common

            st.success(f"Estimated Cohen's f: {round(f_calculated, 4)}")

            st.write("Interpretation:")
            st.write("• < 0.10 = Very small")
            st.write("• ≈ 0.25 = Moderate")
            st.write("• > 0.40 = Large")

    # --------------------------------------------------
    st.markdown("### 🎯 Sample Size Planning")

    st.write("Log-rank planning formula uses F-test power method internally.")

    effect_size = st.number_input("Cohen's f for Sample Size", min_value=0.0001, value=0.25)
    k_groups = st.number_input("Number of Groups", min_value=2, value=3)

    if st.button("Calculate Sample Size"):

        result = calculate_anova_oneway(
            alpha, power, effect_size,
            k_groups, dropout_rate
        )

        st.success(f"Total Sample Size: {result['n_total']}")
        st.write("Participants per Group:", result["n_per_group"])

        st.write("Underlying power equation:")
        st.latex(r"N = \text{solve\_power}(f, \alpha, \text{power}, k)")

        paragraph = paragraph_anova(
            alpha, power, effect_size,
            k_groups, dropout_rate,
            result["n_total"], result["n_per_group"]
        )

        st.code(paragraph)
