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
import scipy.stats as stats

# Continuous calculators
from calculators.continuous.one_sample_mean import calculate_one_sample_mean
from calculators.continuous.two_independent_means import calculate_two_independent_means
from calculators.continuous.paired_mean import calculate_paired_mean
from calculators.continuous.anova_oneway import calculate_anova_oneway

# Binary calculators
from calculators.binary.one_proportion import calculate_one_proportion

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
        "One Proportion",
    ]
)

# Sidebar
st.sidebar.header("Statistical Parameters")

alpha = st.sidebar.number_input("Alpha (Type I error)", 0.001, 0.2, 0.05, 0.001)
power = st.sidebar.number_input("Power (1 - Beta)", 0.5, 0.99, 0.8, 0.01)
dropout_rate = st.sidebar.number_input("Dropout Rate (0–1)", 0.0, 0.9, 0.0, 0.01)
two_sided = st.sidebar.checkbox("Two-sided test", True)

# ==========================================================
# ONE PROPORTION
# ==========================================================
if study_type == "One Proportion":

    st.header("One Proportion (Single-Group Proportion Test)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when testing whether a single population proportion differs from a known reference value.

Examples:
• Is vaccine uptake different from 70%?
• Is complication rate different from historical 10%?
• Is smoking prevalence different from national 20%?

Design:
• One group
• Binary outcome (Yes/No)
• Compared to reference proportion p₀
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Normal Approximation)", expanded=True):

        st.latex(r"""
        n =
        \frac{
        \left(
        Z_{\alpha}\sqrt{p_0(1-p_0)}
        +
        Z_{\beta}\sqrt{p_1(1-p_1)}
        \right)^2
        }
        {(p_1 - p_0)^2}
        """)

        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")
        st.latex(r"\Delta = p_1 - p_0")

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    p0 = st.number_input("Reference Proportion (p₀)", 0.0001, 0.9999, 0.2)
    p1 = st.number_input("Expected Proportion (p₁)", 0.0001, 0.9999, 0.3)

    if st.button("Calculate Sample Size"):

        delta_used = abs(p1 - p0)

        result = calculate_one_proportion(
            alpha,
            power,
            p0,
            p1,
            two_sided,
            dropout_rate
        )

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")

        st.latex(rf"""
        n =
        \frac{{
        \left(
        {round(Z_alpha,4)}\sqrt{{{p0}(1-{p0})}}
        +
        {round(Z_beta,4)}\sqrt{{{p1}(1-{p1})}}
        \right)^2
        }}
        {{({round(delta_used,4)})^2}}
        """)

        st.success(f"Required Sample Size: {result['n_required']}")
        st.write("Before Dropout Adjustment:", result["n_before_dropout"])

        st.markdown("### 📄 Copy for Thesis / Manuscript")

        st.code(f"""
Sample size was calculated for a one-sample proportion test with α={alpha}
and power={power}. Assuming a reference proportion of {p0}
and an expected proportion of {p1}, the required sample size
was {result['n_required']} participants
(after adjusting for {dropout_rate*100:.1f}% anticipated dropout).
        """)
