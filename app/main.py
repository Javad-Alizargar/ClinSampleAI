
# ==========================================
# ClinSample AI — Streamlit App (MVP v1)
# ==========================================

import streamlit as st

from calculators.continuous.one_sample_mean import calculate_one_sample_mean
from calculators.continuous.two_independent_means import calculate_two_independent_means

from templates.paragraph_templates import (
    paragraph_one_sample_mean,
    paragraph_two_independent_means
)

st.set_page_config(page_title="ClinSample AI", layout="centered")

st.title("ClinSample AI — Sample Size Calculator")
st.markdown("Evidence-based, thesis-ready sample size planning.")

study_type = st.selectbox(
    "Select Study Type",
    [
        "One-Sample Mean",
        "Two Independent Means",
    ]
)

st.sidebar.header("Statistical Parameters")

alpha = st.sidebar.number_input("Alpha (Type I error)", value=0.05, min_value=0.001, max_value=0.2)
power = st.sidebar.number_input("Power (1 - Beta)", value=0.8, min_value=0.5, max_value=0.99)
dropout_rate = st.sidebar.number_input("Dropout Rate (0-1)", value=0.0, min_value=0.0, max_value=0.9)
two_sided = st.sidebar.checkbox("Two-sided test", value=True)

if study_type == "One-Sample Mean":

    st.header("One-Sample Mean")

    sd = st.number_input("Standard Deviation (SD)", value=1.0, min_value=0.0001)
    delta = st.number_input("Expected Mean Difference (Δ)", value=0.5, min_value=0.0001)

    if st.button("Calculate Sample Size"):

        result = calculate_one_sample_mean(
            alpha=alpha,
            power=power,
            sd=sd,
            delta=delta,
            two_sided=two_sided,
            dropout_rate=dropout_rate
        )

        st.success(f"Required Sample Size: {result['n_required']}")

        st.subheader("Details")
        st.write("Before Dropout Adjustment:", result["n_before_dropout"])
        st.write("Formula:", result["formula"])
        st.write("Assumptions:", result["assumptions"])

        paragraph = paragraph_one_sample_mean(
            alpha, power, sd, delta,
            two_sided, dropout_rate,
            result["n_required"]
        )

        st.subheader("Copy for Thesis")
        st.code(paragraph)


elif study_type == "Two Independent Means":

    st.header("Two Independent Means")

    sd = st.number_input("Common Standard Deviation (SD)", value=1.0, min_value=0.0001)
    delta = st.number_input("Expected Mean Difference (Δ)", value=0.5, min_value=0.0001)
    allocation_ratio = st.number_input("Allocation Ratio (n2 / n1)", value=1.0, min_value=0.1)

    if st.button("Calculate Sample Size"):

        result = calculate_two_independent_means(
            alpha=alpha,
            power=power,
            sd=sd,
            delta=delta,
            allocation_ratio=allocation_ratio,
            two_sided=two_sided,
            dropout_rate=dropout_rate
        )

        st.success(f"Group 1: {result['n_group1']} | Group 2: {result['n_group2']}")
        st.write("Total Sample Size:", result["n_total"])

        st.subheader("Details")
        st.write("Before Dropout Adjustment (Group 1):", result["n_before_dropout_group1"])
        st.write("Before Dropout Adjustment (Group 2):", result["n_before_dropout_group2"])
        st.write("Formula:", result["formula"])
        st.write("Assumptions:", result["assumptions"])

        paragraph = paragraph_two_independent_means(
            alpha, power, sd, delta,
            allocation_ratio, two_sided,
            dropout_rate,
            result["n_group1"],
            result["n_group2"]
        )

        st.subheader("Copy for Thesis")
        st.code(paragraph)
