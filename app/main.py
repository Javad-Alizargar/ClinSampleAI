# ==========================================
# ClinSample AI — Standardized Formula Edition
# ==========================================

import sys
import os
import math

# Fix Streamlit Cloud import path
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
st.markdown("Mathematically standardized, thesis-ready sample size planning.")

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

# Sidebar
st.sidebar.header("Statistical Parameters")

alpha = st.sidebar.number_input("Alpha (Type I error)", 0.001, 0.2, 0.05, 0.001)
power = st.sidebar.number_input("Power (1 - Beta)", 0.5, 0.99, 0.8, 0.01)
dropout_rate = st.sidebar.number_input("Dropout Rate (0–1)", 0.0, 0.9, 0.0, 0.01)
two_sided = st.sidebar.checkbox("Two-sided test", True)

# ==========================================================
# ONE SAMPLE MEAN
# ==========================================================
if study_type == "One-Sample Mean":

    import scipy.stats as stats
    import math

    st.header("One-Sample Mean")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when comparing a sample mean to a known or reference value.

Example:
Testing whether the mean fasting glucose level in diabetic patients differs from
the national reference value of 100 mg/dL.

Design assumptions:
• Single group
• Approximately normal outcome
• SD known or estimated from literature/pilot data
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula", expanded=True):

        st.write("Core sample size formula:")

        st.latex(r"""
        n = \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD}{\Delta} \right)^2
        """)

        st.write("Where:")

        st.latex(r"Z_{\alpha} = \Phi^{-1}(1 - \alpha/2) \quad \text{(two-sided)}")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")
        st.latex(r"SD = \text{standard deviation}")
        st.latex(r"\Delta = \text{clinically meaningful mean difference}")

        st.write("For one-sided test:")

        st.latex(r"Z_{\alpha} = \Phi^{-1}(1 - \alpha)")

    # --------------------------------------------------
    with st.expander("📊 Parameter Explanation and How to Obtain Them", expanded=False):

        st.markdown("""
**Standard Deviation (SD):**

Represents variability in the outcome.

How to obtain:
• From previous published studies  
• From pilot study  
• From meta-analysis  
• From registry data  

If unsure:
Use slightly larger SD for conservative planning.

---

**Mean Difference (Δ):**

This is the smallest clinically meaningful difference you want to detect.

Should NOT be chosen arbitrarily.

Sources:
• Clinical guidelines  
• Expert consensus  
• Prior RCTs  
• Regulatory thresholds  

Larger Δ → smaller sample size  
Smaller Δ → larger sample size
        """)

    # --------------------------------------------------
    with st.expander("🧮 Understanding Z-values", expanded=False):

        st.latex(r"Z_{\alpha} = \Phi^{-1}(1 - \alpha/2)")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")

        st.write("Example values:")

        st.write("• α = 0.05 (two-sided) → Zα ≈ 1.96")
        st.write("• Power = 0.80 → Zβ ≈ 0.84")
        st.write("• Power = 0.90 → Zβ ≈ 1.28")

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Sample Size Calculation")

    sd = st.number_input("Standard Deviation (SD)", min_value=0.0001, value=1.0)
    delta = st.number_input("Clinically Meaningful Difference (Δ)", min_value=0.0001, value=0.5)

    if st.button("Calculate Sample Size"):

        result = calculate_one_sample_mean(
            alpha,
            power,
            sd,
            delta,
            two_sided,
            dropout_rate
        )

        # Manual display of components
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")

        st.latex(rf"""
        n = \left( \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)}) \cdot {sd}}}{{{delta}}} \right)^2
        """)

        st.success(f"Required Sample Size: {result['n_required']}")
        st.write("Before Dropout Adjustment:", result["n_before_dropout"])

        st.markdown("### 📄 Copy for Thesis / Manuscript")

        paragraph = paragraph_one_sample_mean(
            alpha,
            power,
            sd,
            delta,
            two_sided,
            dropout_rate,
            result["n_required"]
        )

        st.code(paragraph)

# ==========================================================
# TWO INDEPENDENT MEANS
# ==========================================================
elif study_type == "Two Independent Means":

    st.header("Two Independent Means")

    st.subheader("Mathematical Formula")

    st.latex(r"""
    n_1 = (1 + \frac{1}{r})
    \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD}{\Delta} \right)^2
    """)

    st.latex(r"n_2 = r \cdot n_1")

    st.latex(r"r = \frac{n_2}{n_1}")

    sd = st.number_input("Common SD", 0.0001, value=1.0)
    delta = st.number_input("Mean Difference (Δ)", 0.0001, value=0.5)
    ratio = st.number_input("Allocation Ratio (n2/n1)", 0.1, value=1.0)

    if st.button("Calculate Sample Size"):

        result = calculate_two_independent_means(alpha, power, sd, delta, ratio, two_sided, dropout_rate)

        st.success(f"Group 1: {result['n_group1']} | Group 2: {result['n_group2']}")
        st.write("Total:", result["n_total"])

        paragraph = paragraph_two_independent_means(
            alpha, power, sd, delta,
            ratio, two_sided, dropout_rate,
            result["n_group1"], result["n_group2"]
        )

        st.code(paragraph)

# ==========================================================
# PAIRED MEAN
# ==========================================================
elif study_type == "Paired Mean":

    st.header("Paired Mean")

    st.subheader("Mathematical Formula")

    st.latex(r"""
    n = \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD_d}{\Delta} \right)^2
    """)

    st.latex(r"SD_d = \text{Standard deviation of paired differences}")

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

    st.header("One-Way ANOVA")

    st.subheader("Effect Size Definition")

    st.latex(r"""
    f = \sqrt{\frac{\eta^2}{1 - \eta^2}}
    """)

    st.subheader("Power Equation (F-test based)")

    st.latex(r"""
    N = \text{solve\_power}(f, \alpha, power, k)
    """)

    st.subheader("Compute Cohen’s f from Group Means")

    st.latex(r"\bar{\mu} = \frac{\sum \mu_i}{k}")
    st.latex(r"SS_{between} = \sum (\mu_i - \bar{\mu})^2")
    st.latex(r"f = \frac{\sqrt{SS_{between}/k}}{SD}")

    k_est = st.number_input("Groups for f Estimation", min_value=2, value=3)

    means = []
    for i in range(int(k_est)):
        m = st.number_input(f"Mean of Group {i+1}", value=0.0, key=f"mean_{i}")
        means.append(m)

    sd_common = st.number_input("Common SD", min_value=0.0001, value=1.0)

    if st.button("Compute Cohen's f"):

        grand_mean = sum(means) / len(means)
        ss_between = sum((m - grand_mean) ** 2 for m in means)
        variance_between = ss_between / len(means)
        f_calc = math.sqrt(variance_between) / sd_common

        st.success(f"Cohen's f = {round(f_calc,4)}")

    st.markdown("---")

    st.subheader("Sample Size Planning")

    effect_size = st.number_input("Cohen's f for Planning", min_value=0.0001, value=0.25)
    k_groups = st.number_input("Number of Groups", min_value=2, value=3)

    if st.button("Calculate Sample Size"):

        result = calculate_anova_oneway(alpha, power, effect_size, k_groups, dropout_rate)

        st.success(f"Total Sample Size: {result['n_total']}")
        st.write("Per Group:", result["n_per_group"])

        paragraph = paragraph_anova(
            alpha, power, effect_size,
            k_groups, dropout_rate,
            result["n_total"], result["n_per_group"]
        )

        st.code(paragraph)
