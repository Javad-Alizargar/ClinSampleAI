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

    st.header("One-Way ANOVA")

    # --------------------------------------------------
    with st.expander("📘 When to Use One-Way ANOVA"):
        st.markdown("""
Used when comparing means across **three or more independent groups**.

Typical examples:

• Comparing LDL cholesterol across 3 diet types  
• Comparing pain scores across 4 treatment arms  
• Comparing blood pressure across different drug doses  

Assumes:
- Independent groups
- Approximately normal outcome
- Homogeneity of variance (similar SD across groups)
        """)

    # --------------------------------------------------
    with st.expander("📐 What is Cohen’s f? (Effect Size Explanation)"):
        st.markdown(r"""
Cohen’s f is the standardized effect size used for ANOVA.

Mathematically:

f = √(η² / (1 − η²))

Where:

η² (eta squared) = proportion of variance explained by group differences.

Interpretation (Cohen, 1988):

- f = 0.10 → Small effect  
- f = 0.25 → Medium effect  
- f = 0.40 → Large effect  

Important:
f does NOT measure raw mean difference.  
It measures how separated the group means are relative to within-group variability.
        """)

    # --------------------------------------------------
    with st.expander("📊 How to Obtain Cohen’s f from Published Studies"):
        st.markdown("""
If a paper reports:

1️⃣ Eta squared (η²):
   Use:
   f = √(η² / (1 − η²))

Example:
If η² = 0.06

f = √(0.06 / 0.94)
f ≈ 0.25 (medium effect)

---

2️⃣ Partial eta squared (ηp²):
   You can use the same formula approximately for planning.

---

3️⃣ Means and Standard Deviations:
   If study reports group means and SD:

Step 1: Compute variance between groups  
Step 2: Compute pooled within-group variance  
Step 3: Compute η²  
Step 4: Convert to f

This is more advanced but possible from published tables.
        """)

    # --------------------------------------------------
    with st.expander("🧪 How to Estimate f from Pilot Data"):
        st.markdown("""
If you have pilot data:

Step 1:
Run one-way ANOVA in statistical software (R/SPSS/Python).

Step 2:
Extract η² or partial η².

Step 3:
Convert to Cohen’s f using:

f = √(η² / (1 − η²))

If pilot sample is small, consider slightly reducing f (conservative planning).
        """)

    # --------------------------------------------------
    with st.expander("🔢 Worked Numerical Example"):
        st.markdown("""
Suppose 3 diet groups have:

Mean LDL:
Group A: 120  
Group B: 130  
Group C: 145  

Common SD ≈ 20  

These means are separated moderately relative to SD.  
This often produces η² ≈ 0.06–0.08  

Converted to:

f ≈ 0.25 (medium effect)

Thus using f = 0.25 is reasonable.
        """)

    # --------------------------------------------------
    with st.expander("⚠️ Choosing a Conservative Value"):
        st.markdown("""
If uncertain:

• Use f = 0.25 (medium) if literature suggests moderate difference.
• Use f = 0.20 for conservative planning.
• Avoid using f = 0.40 unless strong separation is expected.

Remember:
Overestimating effect size → Underpowered study.
        """)

    # --------------------------------------------------
    effect_size = st.number_input("Cohen's f", min_value=0.0001, value=0.25)
    k_groups = st.number_input("Number of Groups", min_value=2, value=3)

    if st.button("Calculate Sample Size"):

        result = calculate_anova_oneway(
            alpha, power, effect_size,
            k_groups, dropout_rate
        )

        st.success(f"Total Sample Size: {result['n_total']}")
        st.write("Participants per Group:", result["n_per_group"])

        st.markdown("### 📄 Copy for Thesis / Manuscript")

        paragraph = paragraph_anova(
            alpha, power, effect_size,
            k_groups, dropout_rate,
            result["n_total"], result["n_per_group"]
        )

        st.code(paragraph)
