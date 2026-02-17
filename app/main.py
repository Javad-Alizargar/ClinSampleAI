# ==========================================
# ClinSample AI — Streamlit App (MVP v2)
# ==========================================

import sys
import os

# Fix import path for Streamlit Cloud
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import streamlit as st

# Continuous imports
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
st.markdown("Evidence-based, thesis-ready sample size planning.")

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

alpha = st.sidebar.number_input("Alpha", 0.001, 0.2, 0.05, 0.001)
power = st.sidebar.number_input("Power", 0.5, 0.99, 0.8, 0.01)
dropout_rate = st.sidebar.number_input("Dropout Rate (0–1)", 0.0, 0.9, 0.0, 0.01)
two_sided = st.sidebar.checkbox("Two-sided test", True)

# --------------------------------------------------
if study_type == "One-Sample Mean":

    sd = st.number_input("Standard Deviation (SD)", 0.0001, value=1.0)
    delta = st.number_input("Mean Difference (Δ)", 0.0001, value=0.5)

    if st.button("Calculate"):
        result = calculate_one_sample_mean(alpha, power, sd, delta, two_sided, dropout_rate)
        st.success(f"Required Sample Size: {result['n_required']}")
        paragraph = paragraph_one_sample_mean(alpha, power, sd, delta, two_sided, dropout_rate, result["n_required"])
        st.code(paragraph)

# --------------------------------------------------
elif study_type == "Two Independent Means":

    sd = st.number_input("Common SD", 0.0001, value=1.0)
    delta = st.number_input("Mean Difference (Δ)", 0.0001, value=0.5)
    ratio = st.number_input("Allocation Ratio (n2/n1)", 0.1, value=1.0)

    if st.button("Calculate"):
        result = calculate_two_independent_means(alpha, power, sd, delta, ratio, two_sided, dropout_rate)
        st.success(f"Group 1: {result['n_group1']} | Group 2: {result['n_group2']}")
        paragraph = paragraph_two_independent_means(alpha, power, sd, delta, ratio, two_sided, dropout_rate, result["n_group1"], result["n_group2"])
        st.code(paragraph)

# --------------------------------------------------
elif study_type == "Paired Mean":

    sd_diff = st.number_input("SD of Differences", 0.0001, value=1.0)
    delta = st.number_input("Mean Difference (Δ)", 0.0001, value=0.5)

    if st.button("Calculate"):
        result = calculate_paired_mean(alpha, power, sd_diff, delta, two_sided, dropout_rate)
        st.success(f"Required Sample Size: {result['n_required']}")
        paragraph = paragraph_paired_mean(alpha, power, sd_diff, delta, two_sided, dropout_rate, result["n_required"])
        st.code(paragraph)

# --------------------------------------------------
elif study_type == "One-Way ANOVA":

    effect_size = st.number_input("Cohen's f", 0.0001, value=0.25)
    k_groups = st.number_input("Number of Groups", 2, value=3)

    if st.button("Calculate"):
        result = calculate_anova_oneway(alpha, power, effect_size, k_groups, dropout_rate)
        st.success(f"Total Sample Size: {result['n_total']}")
        paragraph = paragraph_anova(alpha, power, effect_size, k_groups, dropout_rate, result["n_total"], result["n_per_group"])
        st.code(paragraph)
