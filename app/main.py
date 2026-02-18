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
# Binary calculators
from calculators.binary.one_proportion import calculate_one_proportion
from calculators.binary.two_proportions import calculate_two_proportions

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
# --------------------------------------------------
study_type = st.selectbox(
    "Select Study Type",
    [
        # Continuous
        "One-Sample Mean",
        "Two Independent Means",
        "Paired Mean",
        "One-Way ANOVA",

        # Binary
        "One Proportion",
        "Two Proportions",
        "Case-Control (Odds Ratio)",
        "Cohort (Risk Ratio)",

        # Association
        "Correlation",
        "Linear Regression",
        "Logistic Regression",

        # Survival
        "Survival (Log-Rank)"
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

    import scipy.stats as stats
    import math

    st.header("Two Independent Means")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when comparing the means of two independent groups.

Examples:
• Treatment vs placebo  
• Male vs female comparison  
• Two different therapies  

Assumptions:
• Independent groups  
• Approximately normal distribution  
• Similar variance in both groups  
• Independent observations  
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula", expanded=True):

        st.write("Primary sample size formula:")

        st.latex(r"""
        n_1 =
        \left(1 + \frac{1}{r}\right)
        \left(
        \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD_{pooled}}
        {\Delta}
        \right)^2
        """)

        st.latex(r"n_2 = r \cdot n_1")

        st.write("Pooled SD formula:")

        st.latex(r"""
        SD_{pooled} =
        \sqrt{
        \frac{(n_1 - 1)SD_1^2 + (n_2 - 1)SD_2^2}
        {n_1 + n_2 - 2}
        }
        """)

        st.write("Z definitions:")

        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")

    # --------------------------------------------------
    with st.expander("🧮 Compute Pooled SD from Pilot or Literature", expanded=False):

        st.write("Enter pilot or literature values:")

        n1_pilot = st.number_input("Pilot n1", min_value=2, value=20)
        sd1 = st.number_input("SD Group 1", min_value=0.0001, value=1.0)

        n2_pilot = st.number_input("Pilot n2", min_value=2, value=20)
        sd2 = st.number_input("SD Group 2", min_value=0.0001, value=1.0)

        if st.button("Compute Pooled SD"):

            pooled_sd = math.sqrt(
                ((n1_pilot - 1)*sd1**2 + (n2_pilot - 1)*sd2**2) /
                (n1_pilot + n2_pilot - 2)
            )

            st.success(f"Pooled SD = {round(pooled_sd,4)}")

    # --------------------------------------------------
    with st.expander("🧮 Compute Mean Difference (Δ) from Group Means", expanded=False):

        mean1 = st.number_input("Mean Group 1", value=0.0)
        mean2 = st.number_input("Mean Group 2", value=0.0)

        if st.button("Compute Δ"):

            delta_raw = mean2 - mean1
            delta_abs = abs(delta_raw)

            st.write(f"Raw Δ (Mean2 - Mean1) = {round(delta_raw,4)}")
            st.write(f"Absolute Δ used in calculation = {round(delta_abs,4)}")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance", expanded=False):

        st.markdown("""
**SD_pooled**

Represents within-group variability.

Sources:
• Randomized controlled trials  
• Observational studies  
• Pilot data  
• Meta-analyses  

If unsure:
Use conservative (slightly larger) SD.

---

**Δ (Mean Difference)**

Should be clinically meaningful.

Sources:
• Guidelines  
• Previous trials  
• Regulatory thresholds  

Smaller Δ → Larger required sample size.

---

**Allocation Ratio (r)**

r = n2 / n1

• r = 1 → equal allocation  
• r > 1 → more participants in group 2  
• r < 1 → more participants in group 1  

Unequal allocation increases total sample size.
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    sd_planning = st.number_input("SD for Planning", min_value=0.0001, value=1.0)
    delta = st.number_input("Mean Difference (Δ) for Planning", min_value=0.0001, value=0.5)
    ratio = st.number_input("Allocation Ratio (n2 / n1)", min_value=0.1, value=1.0)

    if st.button("Calculate Sample Size"):

        delta_used = abs(delta)

        result = calculate_two_independent_means(
            alpha,
            power,
            sd_planning,
            delta_used,
            ratio,
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
        n_1 =
        \left(1 + \frac{{1}}{{{ratio}}}\right)
        \left(
        \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)}) \cdot {sd_planning}}}
        {{{delta_used}}}
        \right)^2
        """)

        st.success(f"Group 1 Required: {result['n_group1']}")
        st.success(f"Group 2 Required: {result['n_group2']}")
        st.write("Total Sample Size:", result["n_total"])

        st.markdown("### 📄 Copy for Thesis")

        paragraph = paragraph_two_independent_means(
            alpha,
            power,
            sd_planning,
            delta_used,
            ratio,
            two_sided,
            dropout_rate,
            result["n_group1"],
            result["n_group2"]
        )

        st.code(paragraph)

# ==========================================================
# PAIRED MEAN (Before–After / Matched Pairs)
# ==========================================================
elif study_type == "Paired Mean":

    import scipy.stats as stats
    import math

    st.header("Paired Mean (Before–After / Matched Pairs)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when the **same participants** are measured twice (or matched pairs are compared).

Common examples:
• Blood pressure before vs after an intervention  
• Pain score pre-treatment vs post-treatment  
• Lab marker measured at baseline and follow-up in the same subjects  

Key idea:
Because measurements are paired, variability is based on the **within-subject differences**,
not the raw SD of each timepoint.
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula", expanded=True):

        st.write("Core sample size formula for paired mean difference:")

        st.latex(r"""
        n = \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD_d}{\Delta} \right)^2
        """)

        st.write("Where:")

        st.latex(r"SD_d = \text{SD of within-subject differences } (d_i = X_{post,i}-X_{pre,i})")
        st.latex(r"\Delta = \text{clinically meaningful mean difference in paired change}")
        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)\ \text{(two-sided)}")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")

        st.write("For one-sided test:")

        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha)")

    # --------------------------------------------------
    with st.expander("🧮 Compute SD of Differences (SDd) from Simple Inputs", expanded=False):

        st.markdown("""
Most users do **not** directly know SD of differences.
You can estimate it from common values available in literature/pilot studies.

### Method 1 — If you have SD of paired differences directly:
Use that value as **SDd**.

### Method 2 — If you only have SD at baseline and follow-up + correlation (ρ):
Use:

SDd = √(SD_pre² + SD_post² − 2ρ·SD_pre·SD_post)

This is the most common practical approach.
        """)

        st.write("Formula:")

        st.latex(r"""
        SD_d =
        \sqrt{
        SD_{pre}^2 + SD_{post}^2 - 2\rho \cdot SD_{pre} \cdot SD_{post}
        }
        """)

        sd_pre = st.number_input("SD at Baseline (SD_pre)", min_value=0.0001, value=1.0)
        sd_post = st.number_input("SD at Follow-up (SD_post)", min_value=0.0001, value=1.0)
        rho = st.number_input("Correlation between measurements (ρ)", min_value=0.0, max_value=0.99, value=0.5)

        if st.button("Compute SDd"):

            sdd = math.sqrt(sd_pre**2 + sd_post**2 - 2*rho*sd_pre*sd_post)
            st.success(f"Estimated SD of Differences (SDd) = {round(sdd,4)}")

            st.markdown("Interpretation notes:")
            st.write("• Higher correlation (ρ) → smaller SDd → smaller required sample size")
            st.write("• If correlation is unknown, ρ=0.5 is a common planning default")

    # --------------------------------------------------
    with st.expander("🧮 Compute Mean Difference (Δ) from Two Means", expanded=False):

        st.markdown("""
If you have means for baseline and follow-up (or paired conditions), compute:

Δ = Mean_post − Mean_pre

Use absolute value for planning (magnitude of change).
        """)

        mean_pre = st.number_input("Mean at Baseline (Mean_pre)", value=0.0)
        mean_post = st.number_input("Mean at Follow-up (Mean_post)", value=0.0)

        if st.button("Compute Δ (paired change)"):

            delta_raw = mean_post - mean_pre
            delta_abs = abs(delta_raw)

            st.write(f"Raw Δ (post - pre) = {round(delta_raw,4)}")
            st.write(f"Absolute Δ used in calculation = {round(delta_abs,4)}")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance (How to Choose SDd and Δ)", expanded=False):

        st.markdown("""
**SDd (SD of differences)**  
Preferred sources:
• Pilot study: compute differences per subject and take SD  
• Prior paired studies reporting SD of change  
• If only SD_pre and SD_post available: use correlation-based formula above  

**Correlation (ρ)**  
Sources:
• Pilot study correlation  
• Similar published studies  
If unknown, ρ=0.3–0.7 is typical; 0.5 is a practical default.

**Δ (paired mean difference)**  
Should be clinically meaningful change (e.g., minimal clinically important difference, MCID)
or expected change from literature.

Smaller Δ → larger sample size.
        """)

    # --------------------------------------------------
    with st.expander("🧮 Understanding Z-values", expanded=False):

        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")

        st.write("Common reference values:")
        st.write("• α = 0.05 (two-sided) → Zα ≈ 1.96")
        st.write("• Power = 0.80 → Zβ ≈ 0.84")
        st.write("• Power = 0.90 → Zβ ≈ 1.28")

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    sd_diff = st.number_input("SD of Differences (SDd) for Planning", min_value=0.0001, value=1.0)
    delta = st.number_input("Mean Difference (Δ) for Planning", min_value=0.0001, value=0.5)

    if st.button("Calculate Sample Size"):

        delta_used = abs(delta)

        result = calculate_paired_mean(
            alpha,
            power,
            sd_diff,
            delta_used,
            two_sided,
            dropout_rate
        )

        # Intermediate Z-values
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
        \left(
        \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)}) \cdot {sd_diff}}}
        {{{delta_used}}}
        \right)^2
        """)

        st.success(f"Required Sample Size: {result['n_required']}")
        st.write("Before Dropout Adjustment:", result["n_before_dropout"])

        st.markdown("### 📄 Copy for Thesis / Manuscript")

        paragraph = paragraph_paired_mean(
            alpha,
            power,
            sd_diff,
            delta_used,
            two_sided,
            dropout_rate,
            result["n_required"]
        )

        st.code(paragraph)


# ==========================================================
# ONE-WAY ANOVA (k groups)
# ==========================================================
elif study_type == "One-Way ANOVA":

    import math

    st.header("One-Way ANOVA (k Independent Groups)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when comparing a continuous outcome across 3 or more independent groups.

Examples:
• LDL cholesterol across 3 diet regimens  
• Pain score across 4 treatment arms  

Assumptions:
• Independent groups  
• Approximate normal distribution  
• Similar variance across groups  
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Foundations", expanded=True):

        st.write("Cohen’s f (effect size for ANOVA):")

        st.latex(r"f = \sqrt{\frac{\eta^2}{1-\eta^2}}")

        st.write("Power model solved using F-test framework:")

        st.latex(r"N = \text{solve\_power}(f,\ \alpha,\ \text{power},\ k)")

    # --------------------------------------------------
    with st.expander("🧮 Compute Common SD from Group SDs", expanded=False):

        st.markdown("""
If literature reports SD separately for each group,
you can compute pooled (common) SD.

Formula:
        """)

        st.latex(r"""
        SD_{pooled} =
        \sqrt{
        \frac{\sum (n_i - 1)SD_i^2}
        {\sum (n_i - 1)}
        }
        """)

        k_sd = st.number_input("Number of Groups (for SD pooling)", min_value=2, value=3)

        ns = []
        sds = []

        for i in range(int(k_sd)):
            ns.append(st.number_input(f"Group {i+1} sample size (n{i+1})", min_value=2, value=20, key=f"anova_n_{i}"))
            sds.append(st.number_input(f"Group {i+1} SD (SD{i+1})", min_value=0.0001, value=1.0, key=f"anova_sd_{i}"))

        if st.button("Compute Common SD"):

            numerator = sum((ns[i]-1)*(sds[i]**2) for i in range(len(ns)))
            denominator = sum((ns[i]-1) for i in range(len(ns)))

            pooled_sd = math.sqrt(numerator / denominator)

            st.success(f"Common (Pooled) SD = {round(pooled_sd,4)}")

            st.write("Interpretation:")
            st.write("• Use this SD for Cohen's f estimation")
            st.write("• Conservative approach: slightly inflate SD")

    # --------------------------------------------------
    with st.expander("🧮 Compute Cohen’s f from Group Means + Common SD", expanded=False):

        st.markdown("""
Given group means and common SD:

1) Compute grand mean  
2) Compute between-group variance  
3) f = √(Variance_between) / SD
        """)

        st.latex(r"\bar{\mu} = \frac{\sum \mu_i}{k}")
        st.latex(r"V = \frac{\sum (\mu_i-\bar{\mu})^2}{k}")
        st.latex(r"f = \frac{\sqrt{V}}{SD}")

        k_est = st.number_input("Number of Groups (for f estimation)", min_value=2, value=3)

        means = []

        for i in range(int(k_est)):
            means.append(st.number_input(f"Mean Group {i+1}", value=0.0, key=f"anova_mean_{i}"))

        sd_common = st.number_input("Common SD for f estimation", min_value=0.0001, value=1.0)

        if st.button("Compute Cohen's f"):

            grand_mean = sum(means) / len(means)
            ss_between = sum((m - grand_mean)**2 for m in means)
            variance_between = ss_between / len(means)

            f_calc = math.sqrt(variance_between) / sd_common

            st.success(f"Cohen's f = {round(f_calc,4)}")

            st.write("Guidelines:")
            st.write("• 0.10 = small")
            st.write("• 0.25 = medium")
            st.write("• 0.40 = large")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance", expanded=False):

        st.markdown("""
**Common SD**

Sources:
• Published group SDs (pooled)  
• Pilot study SDs  
• Meta-analysis pooled SD  

Avoid:
Using smallest SD (inflates effect).

---

**Cohen’s f**

Derived from:
• Means + SD  
• η² from literature  
• Pilot study effect  

Avoid overestimating f.
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    effect_size = st.number_input("Cohen's f for Planning", min_value=0.0001, value=0.25)
    k_groups = st.number_input("Number of Groups (k)", min_value=2, value=3)

    if st.button("Calculate Sample Size"):

        result = calculate_anova_oneway(
            alpha,
            power,
            effect_size,
            k_groups,
            dropout_rate
        )

        st.success(f"Total Sample Size: {result['n_total']}")
        st.write("Participants per Group:", result["n_per_group"])

        st.markdown("### 📄 Copy for Thesis")

        paragraph = paragraph_anova(
            alpha,
            power,
            effect_size,
            k_groups,
            dropout_rate,
            result["n_total"],
            result["n_per_group"]
        )

        st.code(paragraph)
# ==========================================================
# ONE PROPORTION (Single-Group Proportion Test)
# ==========================================================
elif study_type == "One Proportion":

    import scipy.stats as stats
    import math

    st.header("One Proportion (Single-Group Proportion Test)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when testing whether a single population proportion differs from a known or reference value.

Examples:
• Is vaccine uptake different from 70% target?
• Is smoking prevalence different from national 20%?
• Is complication rate different from historical benchmark?

Design:
• One group
• Binary outcome (yes/no)
• Compared to reference proportion p₀
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Normal Approximation)", expanded=True):

        st.latex(r"""
        n =
        \frac{
        \left(
        Z_{\alpha} \sqrt{p_0(1-p_0)}
        +
        Z_{\beta} \sqrt{p_1(1-p_1)}
        \right)^2
        }
        {(p_1 - p_0)^2}
        """)

        st.write("Where:")

        st.latex(r"p_0 = \text{reference proportion}")
        st.latex(r"p_1 = \text{expected true proportion}")
        st.latex(r"\Delta = p_1 - p_0")

        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")

        st.write("For one-sided test:")
        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha)")

    # --------------------------------------------------
    with st.expander("🧮 Compute Risk Difference (Δ) from Two Proportions", expanded=False):

        st.markdown("""
If you know:

• Historical/reference proportion (p₀)
• Expected proportion in your study (p₁)

Then:

Δ = p₁ − p₀
        """)

        p0_calc = st.number_input(
            "Reference Proportion (p₀)",
            min_value=0.0001,
            max_value=0.9999,
            value=0.2,
            key="oneprop_p0_calc"
        )

        p1_calc = st.number_input(
            "Expected Proportion (p₁)",
            min_value=0.0001,
            max_value=0.9999,
            value=0.3,
            key="oneprop_p1_calc"
        )

        if st.button("Compute Δ (Risk Difference)", key="oneprop_delta_btn"):

            delta_raw = p1_calc - p0_calc
            delta_abs = abs(delta_raw)

            st.write(f"Raw Δ = {round(delta_raw,4)}")
            st.write(f"Absolute Δ used in planning = {round(delta_abs,4)}")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance (How to Choose p₀ and p₁)", expanded=False):

        st.markdown("""
**p₀ (Reference proportion)**

Sources:
• National registry  
• Historical control data  
• Published prevalence  
• Clinical target benchmark  

---

**p₁ (Expected proportion)**

Should be:
• Clinically meaningful improvement or change  
• Supported by literature or pilot  
• Realistic  

Smaller difference between p₁ and p₀ → larger required sample size.

---

Avoid:
Choosing p₁ unrealistically far from p₀.
        """)

    # --------------------------------------------------
    with st.expander("🧮 Understanding Z-values", expanded=False):

        st.write("Common values:")
        st.write("• α = 0.05 (two-sided) → Zα ≈ 1.96")
        st.write("• Power = 0.80 → Zβ ≈ 0.84")
        st.write("• Power = 0.90 → Zβ ≈ 1.28")

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    p0 = st.number_input(
        "Reference Proportion (p₀)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.2,
        key="oneprop_p0_final"
    )

    p1 = st.number_input(
        "Expected Proportion (p₁)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.3,
        key="oneprop_p1_final"
    )

    if st.button("Calculate Sample Size", key="oneprop_calc_btn"):

        delta_used = abs(p1 - p0)

        result = calculate_one_proportion(
            alpha,
            power,
            p0,
            p1,
            two_sided,
            dropout_rate
        )

        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")

        latex_formula = f"""
        n =
        \\frac{{
        \\left(
        {round(Z_alpha,4)}\\sqrt{{{p0}(1-{p0})}}
        +
        {round(Z_beta,4)}\\sqrt{{{p1}(1-{p1})}}
        \\right)^2
        }}
        {{({round(delta_used,4)})^2}}
        """

        st.latex(latex_formula)

        st.success(f"Required Sample Size: {result['n_required']}")
        st.write("Before Dropout Adjustment:", result["n_before_dropout"])

        st.markdown("### 📄 Copy for Thesis / Manuscript")

        st.code(f"""
Sample size was calculated for a one-sample proportion test with α={alpha} and power={power}.
Assuming a reference proportion of {p0} and an expected proportion of {p1},
the required sample size was {result['n_required']} participants
(after adjusting for {dropout_rate*100:.1f}% anticipated dropout).
        """)
# ==========================================================
# TWO PROPORTIONS (Two Independent Groups)
# ==========================================================
elif study_type == "Two Proportions":

    import scipy.stats as stats
    import math

    st.header("Two Independent Proportions")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when comparing proportions between two independent groups.

Examples:
• Treatment vs control event rate  
• Smoking rate in men vs women  
• Complication rate between two techniques  

Design:
• Two independent groups  
• Binary outcome  
• Comparing p₁ vs p₂  
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Pooled Normal Approximation)", expanded=True):

        st.latex(r"""
        n_1 =
        \left(1 + \frac{1}{r}\right)
        \frac{
        \left(
        Z_{\alpha}\sqrt{2\bar{p}(1-\bar{p})}
        +
        Z_{\beta}\sqrt{p_1(1-p_1)+p_2(1-p_2)}
        \right)^2
        }
        {(p_1 - p_2)^2}
        """)

        st.latex(r"n_2 = r \cdot n_1")
        st.latex(r"\bar{p} = \frac{p_1 + p_2}{2}")

        st.write("Where:")
        st.latex(r"r = \frac{n_2}{n_1}")
        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")

    # --------------------------------------------------
    with st.expander("🧮 Compute Risk Difference (Δ)", expanded=False):

        p1_calc = st.number_input(
            "Proportion Group 1 (p₁)",
            min_value=0.0001,
            max_value=0.9999,
            value=0.30,
            key="twoprop_p1_calc"
        )

        p2_calc = st.number_input(
            "Proportion Group 2 (p₂)",
            min_value=0.0001,
            max_value=0.9999,
            value=0.20,
            key="twoprop_p2_calc"
        )

        if st.button("Compute Risk Difference", key="twoprop_delta_btn"):

            delta_raw = p1_calc - p2_calc
            delta_abs = abs(delta_raw)

            st.write(f"Raw Risk Difference = {round(delta_raw,4)}")
            st.write(f"Absolute Δ used in planning = {round(delta_abs,4)}")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance", expanded=False):

        st.markdown("""
**p₁ and p₂**

Sources:
• RCTs  
• Cohort studies  
• Registry data  
• Pilot study  

Avoid unrealistic effect sizes.

---

**Allocation Ratio (r)**

r = n₂ / n₁

• r = 1 → equal allocation  
• r > 1 → more participants in group 2  
• r < 1 → more participants in group 1  

Unequal allocation increases total sample size.
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    p1 = st.number_input(
        "Proportion Group 1 (p₁)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.30,
        key="twoprop_p1_final"
    )

    p2 = st.number_input(
        "Proportion Group 2 (p₂)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        key="twoprop_p2_final"
    )

    ratio = st.number_input(
        "Allocation Ratio (n₂ / n₁)",
        min_value=0.1,
        value=1.0,
        key="twoprop_ratio"
    )

    if st.button("Calculate Sample Size", key="twoprop_calc_btn"):

        delta_used = abs(p1 - p2)
        p_bar = (p1 + p2) / 2

        result = calculate_two_proportions(
            alpha,
            power,
            p1,
            p2,
            ratio,
            two_sided,
            dropout_rate
        )

        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"Pooled proportion (p̄) = {round(p_bar,4)}")

        # Safe LaTeX
        latex_formula = f"""
        n_1 =
        \\left(1 + \\frac{{1}}{{{ratio}}}\\right)
        \\frac{{
        \\left(
        {round(Z_alpha,4)}\\sqrt{{2\\cdot{round(p_bar,4)}(1-{round(p_bar,4)})}}
        +
        {round(Z_beta,4)}\\sqrt{{{p1}(1-{p1})+{p2}(1-{p2})}}
        \\right)^2
        }}
        {{({round(delta_used,4)})^2}}
        """

        st.latex(latex_formula)

        st.success(f"Group 1 Required: {result['n_group1']}")
        st.success(f"Group 2 Required: {result['n_group2']}")
        st.write("Total Sample Size:", result["n_total"])

        st.markdown("### 📄 Copy for Thesis / Manuscript")

        st.code(f"""
Sample size was calculated for comparison of two independent proportions with α={alpha} and power={power}.
Assuming event rates of {p1} and {p2} in the two groups and allocation ratio {ratio},
the required sample size was {result['n_group1']} in group 1 and {result['n_group2']} in group 2
(after adjusting for {dropout_rate*100:.1f}% anticipated dropout).
        """)
# ==========================================================
# CASE–CONTROL (Odds Ratio)
# ==========================================================
elif study_type == "Case-Control (Odds Ratio)":

    import scipy.stats as stats
    import math

    st.header("Case–Control Study (Odds Ratio Based Sample Size)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used for unmatched case–control studies.

Examples:
• Association between smoking and lung cancer  
• Genetic variant and disease risk  
• Exposure vs outcome (retrospective design)

Design:
• Binary exposure
• Binary outcome
• Comparison based on Odds Ratio (OR)
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Log Odds Ratio Method)", expanded=True):

        st.latex(r"""
        p_1 = \frac{OR \cdot p_0}{1 - p_0 + OR \cdot p_0}
        """)

        st.latex(r"""
        n_1 =
        \frac{
        (Z_{\alpha} + Z_{\beta})^2
        \left(
        \frac{1}{p_0(1-p_0)} +
        \frac{1}{r \cdot p_1(1-p_1)}
        \right)
        }
        {(\ln OR)^2}
        """)

        st.latex(r"n_2 = r \cdot n_1")

        st.write("Where:")
        st.write("• p₀ = exposure prevalence in controls")
        st.write("• p₁ = exposure prevalence in cases (derived from OR)")
        st.write("• r = control-to-case ratio")
        st.write("• OR = target odds ratio")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance", expanded=False):

        st.markdown("""
**p₀ (Exposure prevalence in controls)**  
Sources:
• Registry data  
• Published literature  
• Pilot data  

**Odds Ratio (OR)**  
Should be:
• Clinically meaningful  
• Supported by literature  

Small OR (e.g., 1.2–1.5) → very large sample size  
Large OR (e.g., 2–3) → smaller sample size  

**Control-to-case ratio (r)**  
r = n_controls / n_cases  

• r = 1 → equal numbers  
• r > 1 → more controls (efficient when cases are rare)  
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    p0 = st.number_input(
        "Exposure Prevalence in Controls (p₀)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.30,
        key="cc_p0"
    )

    OR = st.number_input(
        "Target Odds Ratio (OR)",
        min_value=0.1,
        value=2.0,
        key="cc_or"
    )

    ratio = st.number_input(
        "Control-to-Case Ratio (r)",
        min_value=0.1,
        value=1.0,
        key="cc_ratio"
    )

    if st.button("Calculate Sample Size (Case-Control)", key="cc_calc"):

        # Derive p1
        p1 = (OR * p0) / (1 - p0 + OR * p0)

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        ln_or = math.log(OR)

        # Core formula
        numerator = (Z_alpha + Z_beta)**2 * (
            (1 / (p0*(1-p0))) +
            (1 / (ratio * p1*(1-p1)))
        )

        n1 = numerator / (ln_or**2)
        n2 = ratio * n1

        # Dropout adjustment
        n1_adj = math.ceil(n1 / (1 - dropout_rate))
        n2_adj = math.ceil(n2 / (1 - dropout_rate))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"Estimated p₁ (cases) = {round(p1,4)}")
        st.write(f"log(OR) = {round(ln_or,4)}")

        # Safe LaTeX block
        st.latex(rf"""
        n_1 =
        \frac{{
        ({round(Z_alpha,4)} + {round(Z_beta,4)})^2
        \left(
        \frac{{1}}{{{round(p0,4)}(1-{round(p0,4)})}} +
        \frac{{1}}{{{round(ratio,4)} \cdot {round(p1,4)}(1-{round(p1,4)})}}
        \right)
        }}
        {{({round(ln_or,4)})^2}}
        """)

        # --------------------------------------------------
        st.success(f"Required Cases (n₁): {n1_adj}")
        st.success(f"Required Controls (n₂): {n2_adj}")
        st.write(f"Total Sample Size: {n1_adj + n2_adj}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        st.code(f"""
Sample size was calculated for an unmatched case–control study using the log odds ratio method.
Assuming an exposure prevalence among controls of {p0},
a target odds ratio of {OR},
and a control-to-case ratio of {ratio},
the required sample size was {n1_adj} cases and {n2_adj} controls
(total {n1_adj + n2_adj}),
after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
        """)
# ==========================================================
# COHORT (Risk Ratio)
# ==========================================================
elif study_type == "Cohort (Risk Ratio)":

    import scipy.stats as stats
    import math

    st.header("Cohort Study (Risk Ratio Based Sample Size)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used for cohort studies or randomized trials
when comparing two independent proportions using Risk Ratio (RR).

Examples:
• Drug vs placebo event risk  
• Vaccinated vs unvaccinated infection risk  
• Exposed vs unexposed disease incidence  

Design:
• Binary outcome
• Independent groups
• Risk Ratio as primary effect measure
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Log Risk Ratio Method)", expanded=True):

        st.latex(r"""
        p_1 = RR \cdot p_0
        """)

        st.latex(r"""
        n_1 =
        \frac{
        (Z_{\alpha} + Z_{\beta})^2
        \left(
        \frac{1-p_0}{p_0} +
        \frac{1-p_1}{r \cdot p_1}
        \right)
        }
        {(\ln RR)^2}
        """)

        st.latex(r"n_2 = r \cdot n_1")

        st.write("Where:")
        st.write("• p₀ = baseline risk in control group")
        st.write("• p₁ = risk in exposed group")
        st.write("• RR = target risk ratio")
        st.write("• r = allocation ratio (n₂ / n₁)")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance", expanded=False):

        st.markdown("""
**Baseline Risk (p₀)**  
Sources:
• Registry data  
• Prior cohort studies  
• RCT control arm  
• Pilot study  

**Risk Ratio (RR)**  
Should be:
• Clinically meaningful  
• Supported by literature  

RR close to 1 → very large sample size  
Large RR (e.g., 2–3) → smaller sample size  

**Allocation Ratio (r)**  
r = n₂ / n₁  

• r = 1 → equal groups  
• Unequal allocation increases total sample size
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    p0 = st.number_input(
        "Baseline Risk in Control Group (p₀)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        key="cohort_p0"
    )

    RR = st.number_input(
        "Target Risk Ratio (RR)",
        min_value=0.1,
        value=1.5,
        key="cohort_rr"
    )

    ratio = st.number_input(
        "Allocation Ratio (n₂ / n₁)",
        min_value=0.1,
        value=1.0,
        key="cohort_ratio"
    )

    if st.button("Calculate Sample Size (Cohort)", key="cohort_calc"):

        p1 = p0 * RR

        if p1 >= 1:
            st.error("RR too large for given baseline risk (p₁ ≥ 1).")
            st.stop()

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        ln_rr = math.log(RR)

        # Core formula
        numerator = (Z_alpha + Z_beta)**2 * (
            ((1 - p0) / p0) +
            ((1 - p1) / (ratio * p1))
        )

        n1 = numerator / (ln_rr**2)
        n2 = ratio * n1

        # Dropout adjustment
        n1_adj = math.ceil(n1 / (1 - dropout_rate))
        n2_adj = math.ceil(n2 / (1 - dropout_rate))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"Derived p₁ (exposed risk) = {round(p1,4)}")
        st.write(f"log(RR) = {round(ln_rr,4)}")

        # Safe LaTeX
        st.latex(rf"""
        n_1 =
        \frac{{
        ({round(Z_alpha,4)} + {round(Z_beta,4)})^2
        \left(
        \frac{{1-{round(p0,4)}}}{{{round(p0,4)}}} +
        \frac{{1-{round(p1,4)}}}{{{round(ratio,4)} \cdot {round(p1,4)}}}
        \right)
        }}
        {{({round(ln_rr,4)})^2}}
        """)

        # --------------------------------------------------
        st.success(f"Required Control Group (n₁): {n1_adj}")
        st.success(f"Required Exposed Group (n₂): {n2_adj}")
        st.write(f"Total Sample Size: {n1_adj + n2_adj}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        st.code(f"""
Sample size was calculated for a cohort study using the log risk ratio method.
Assuming a baseline risk of {p0} in the control group,
a target risk ratio of {RR},
and an allocation ratio of {ratio},
the required sample size was {n1_adj} participants in the control group
and {n2_adj} in the exposed group
(total {n1_adj + n2_adj}),
after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
        """)
# ==========================================================
# CORRELATION (Fisher z)
# ==========================================================
elif study_type == "Correlation":

    import scipy.stats as stats
    import math

    st.header("Correlation (Pearson r) — Sample Size via Fisher z-transform")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when your primary question is whether the **correlation** between two continuous variables
differs from 0 (or from a reference correlation).

Examples:
• Correlation between TyG index and HOMA-IR  
• Correlation between CRP and systolic blood pressure  
• Correlation between biomarker level and symptom score  

Assumptions (typical Pearson correlation planning):
• Independent observations  
• Approximately bivariate normality (or large enough sample for robustness)  
• Linear association is meaningful  
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Fisher z)", expanded=True):

        st.markdown("Fisher z-transform of correlation:")

        st.latex(r"""
        z = \frac{1}{2}\ln\left(\frac{1+r}{1-r}\right)
        """)

        st.markdown("Sample size formula (testing r against 0):")

        st.latex(r"""
        n =
        \frac{(Z_{\alpha} + Z_{\beta})^2}{z^2} + 3
        """)

        st.write("Where:")
        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)\ \text{(two-sided)}")
        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha)\ \text{(one-sided)}")
        st.latex(r"Z_{\beta} = \Phi^{-1}(\text{power})")
        st.latex(r"r = \text{target correlation (planning effect)}")

    # --------------------------------------------------
    with st.expander("📊 Choosing r (Effect Size) — Practical Guidance", expanded=False):
        st.markdown("""
**Target correlation (r)** is your expected or minimally meaningful correlation.

How to obtain r:
• From previous published studies reporting correlation  
• From pilot study correlation  
• From meta-analysis / systematic review  
• From domain knowledge (minimal meaningful association)

Interpretation heuristics (context-dependent):
• |r| ≈ 0.10 → small  
• |r| ≈ 0.30 → moderate  
• |r| ≈ 0.50 → large  

Notes:
• Smaller |r| → much larger n  
• Planning should use a **conservative (smaller)** |r| if unsure  
        """)

    # --------------------------------------------------
    with st.expander("🧮 Convert r ↔ Fisher z (for intuition)", expanded=False):

        r_demo = st.number_input(
            "Enter a correlation r to see Fisher z",
            min_value=-0.95,
            max_value=0.95,
            value=0.30,
            step=0.01,
            key="corr_demo_r"
        )

        z_demo = 0.5 * math.log((1 + r_demo) / (1 - r_demo))
        st.write(f"Fisher z = {round(z_demo,4)}")

        st.markdown("Inverse transform (z → r):")
        st.latex(r"""
        r = \frac{e^{2z}-1}{e^{2z}+1}
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    r_target = st.number_input(
        "Target Correlation (r)",
        min_value=-0.95,
        max_value=0.95,
        value=0.30,
        step=0.01,
        key="corr_r_target"
    )

    if st.button("Calculate Sample Size (Correlation)", key="corr_calc"):

        if abs(r_target) < 1e-6:
            st.error("r cannot be 0 for sample size planning. Choose a non-zero target correlation.")
            st.stop()

        if r_target <= -0.99 or r_target >= 0.99:
            st.error("r must be between -0.99 and 0.99.")
            st.stop()

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        # Fisher z
        z = 0.5 * math.log((1 + r_target) / (1 - r_target))

        # Sample size
        n_raw = ((Z_alpha + Z_beta) ** 2) / (z ** 2) + 3
        n = math.ceil(n_raw)

        # Dropout adjustment
        n_adj = math.ceil(n / (1 - dropout_rate))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"Fisher z = {round(z,4)}")
        st.write(f"n (before dropout) = {n}")

        st.latex(rf"""
        z = \frac{{1}}{{2}}\ln\left(\frac{{1+({round(r_target,4)})}}{{1-({round(r_target,4)})}}\right)
        """)

        st.latex(rf"""
        n =
        \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)})^2}}{{({round(z,4)})^2}} + 3
        """)

        st.success(f"Required Sample Size (adjusted): {n_adj}")
        st.write(f"Before Dropout Adjustment: {n}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        sided_txt = "two-sided" if two_sided else "one-sided"

        st.code(f"""
Sample size was calculated for detecting a Pearson correlation using Fisher’s z-transformation ({sided_txt}).
With α={alpha} and power={power}, and assuming a target correlation of r={r_target},
the required sample size was {n_adj} participants after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
        """)
# ==========================================================
# LINEAR REGRESSION (Cohen's f²)
# ==========================================================
elif study_type == "Linear Regression":

    import scipy.stats as stats
    import math

    st.header("Multiple Linear Regression — Sample Size via Cohen’s f²")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when your primary analysis is **multiple linear regression** (continuous outcome)
and you want adequate power to detect an overall model effect or a set of predictors.

Examples:
• Predicting HbA1c from TyG, BMI, age, sex  
• Predicting blood pressure from waist circumference, smoking, lipids  
• Predicting depression score from biomarkers + covariates  

Typical assumptions:
• Independent observations  
• Linear relationship is a reasonable approximation  
• Residuals approximately normal (or sample sufficiently large)  
• Predictors not perfectly collinear  
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Cohen’s f²)", expanded=True):

        st.markdown("Cohen’s f² definition (from R²):")
        st.latex(r"""
        f^2 = \frac{R^2}{1 - R^2}
        """)

        st.markdown("Sample size planning (large-sample z-approximation):")
        st.latex(r"""
        n =
        \frac{(Z_{\alpha} + Z_{\beta})^2}{f^2} + p + 1
        """)

        st.write("Where:")
        st.write("• R² = expected proportion of variance explained by predictors")
        st.write("• f² = Cohen’s effect size for regression")
        st.write("• p = number of predictors (planned predictors in the model)")
        st.write("• Zα depends on one/two-sided α; Zβ depends on desired power")

        st.markdown("Optional: partial effect (incremental R²) for a block of predictors:")
        st.latex(r"""
        f^2_{\text{partial}} = \frac{\Delta R^2}{1 - R^2_{\text{full}}}
        """)

    # --------------------------------------------------
    with st.expander("🧮 Compute Cohen’s f² from R² (and from ΔR²)", expanded=False):

        st.markdown("""
Most users do not directly know f², but they often have an estimate of **R²** from literature or pilot models.

You can compute:
• **Overall f²** from overall R²  
• **Partial f²** from incremental ΔR² (e.g., effect of a predictor block)  
        """)

        tab1, tab2 = st.tabs(["Compute f² from R²", "Compute partial f² from ΔR²"])

        with tab1:
            r2 = st.number_input(
                "Overall R² (0–0.95 recommended)",
                min_value=0.0,
                max_value=0.99,
                value=0.20,
                step=0.01,
                key="linreg_r2_overall"
            )

            if st.button("Compute f² (overall)", key="linreg_calc_f2_overall"):
                if r2 >= 0.999:
                    st.error("R² is too close to 1. Use a realistic value (e.g., < 0.90).")
                else:
                    f2_overall = r2 / (1 - r2) if r2 < 1 else float("inf")
                    st.success(f"Cohen’s f² (overall) = {round(f2_overall,4)}")

                    st.markdown("Interpretation heuristics (context dependent):")
                    st.write("• f² ≈ 0.02 small")
                    st.write("• f² ≈ 0.15 medium")
                    st.write("• f² ≈ 0.35 large")

                    st.latex(rf"""
                    f^2 = \frac{{{round(r2,4)}}}{{1-{round(r2,4)}}}
                    """)

        with tab2:
            r2_full = st.number_input(
                "Full model R² (R²_full)",
                min_value=0.0,
                max_value=0.99,
                value=0.30,
                step=0.01,
                key="linreg_r2_full"
            )
            delta_r2 = st.number_input(
                "Incremental ΔR² (added block contribution)",
                min_value=0.0,
                max_value=0.50,
                value=0.05,
                step=0.01,
                key="linreg_delta_r2"
            )

            if st.button("Compute partial f²", key="linreg_calc_f2_partial"):
                if r2_full >= 0.999:
                    st.error("R²_full is too close to 1. Use a realistic value.")
                elif delta_r2 <= 0:
                    st.error("ΔR² must be > 0 to represent an added effect.")
                elif delta_r2 > r2_full:
                    st.error("ΔR² cannot exceed R²_full.")
                else:
                    f2_partial = delta_r2 / (1 - r2_full)
                    st.success(f"Partial Cohen’s f² = {round(f2_partial,4)}")

                    st.markdown("Interpretation heuristics (often used):")
                    st.write("• 0.02 small")
                    st.write("• 0.15 medium")
                    st.write("• 0.35 large")

                    st.latex(rf"""
                    f^2_{{partial}} = \frac{{{round(delta_r2,4)}}}{{1-{round(r2_full,4)}}}
                    """)

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance (Evidence-Based Choices)", expanded=False):
        st.markdown("""
**R² source hierarchy (best → acceptable):**
1) Pilot regression model on similar population  
2) Published regression model (same outcome + similar predictors)  
3) Meta-analysis / pooled models  
4) Conservative planning (smaller R² → larger sample)

**Predictor count (p):**
Include the predictors you plan to interpret or keep in the final model (not temporary screeners).

**Practical note:**
If you plan model selection / many candidate predictors, you often need more sample size than the basic formula suggests.
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    f2 = st.number_input(
        "Cohen’s f² for Planning",
        min_value=0.0001,
        value=0.15,
        step=0.01,
        key="linreg_f2_plan"
    )

    p = st.number_input(
        "Number of Predictors (p)",
        min_value=1,
        value=5,
        step=1,
        key="linreg_p"
    )

    if st.button("Calculate Sample Size (Linear Regression)", key="linreg_calc_n"):

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        # Sample size formula
        n_raw = ((Z_alpha + Z_beta) ** 2) / f2 + p + 1
        n = math.ceil(n_raw)

        # Dropout adjustment
        n_adj = math.ceil(n / (1 - dropout_rate))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"f² = {round(f2,4)}")
        st.write(f"p = {int(p)}")
        st.write(f"n (before dropout) = {n}")

        st.latex(rf"""
        n =
        \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)})^2}}{{{round(f2,4)}}}
        + {int(p)} + 1
        """)

        st.success(f"Required Sample Size (adjusted): {n_adj}")
        st.write(f"Before Dropout Adjustment: {n}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        sided_txt = "two-sided" if two_sided else "one-sided"

        st.code(f"""
Sample size was calculated for multiple linear regression ({sided_txt}) using Cohen’s f² method.
With α={alpha} and power={power}, assuming an effect size of f²={f2} and {int(p)} predictors,
the required sample size was {n_adj} participants after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
        """)
# ==========================================================
# LOGISTIC REGRESSION (Advanced Wald Method + EPV Check)
# ==========================================================
elif study_type == "Logistic Regression":

    import scipy.stats as stats
    import math

    st.header("Logistic Regression — Advanced Sample Size Planning")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when outcome is binary (0/1) and analysis will be logistic regression.

Examples:
• CKD (yes/no) predicted by SII, age, BMI
• Mortality predicted by biomarkers
• Disease presence predicted by risk factors

This module estimates sample size based on:
• Target Odds Ratio (OR)
• Baseline event probability
• Wald test approximation
• Number of predictors
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Foundation (Wald Approximation)", expanded=True):

        st.markdown("Effect size in logistic regression is based on log odds ratio:")

        st.latex(r"""
        \beta = \ln(OR)
        """)

        st.markdown("Variance of coefficient:")

        st.latex(r"""
        Var(\beta) \approx \frac{1}{n \cdot p(1-p) \cdot x^2}
        """)

        st.markdown("Sample size formula (Wald test):")

        st.latex(r"""
        n =
        \frac{
        (Z_{\alpha} + Z_{\beta})^2
        }
        {
        p(1-p) \cdot (\ln(OR))^2
        }
        """)

        st.write("Where:")
        st.write("• p = event probability")
        st.write("• OR = target odds ratio")
        st.write("• ln(OR) = log effect size")
        st.write("• Zα and Zβ as usual")

    # --------------------------------------------------
    with st.expander("🧮 Compute Event Probability from Baseline + OR", expanded=False):

        st.markdown("""
If you know baseline risk (p₀) and OR,
you can compute exposed group probability (p₁):

p₁ = (OR × p₀) / (1 - p₀ + OR × p₀)
        """)

        st.latex(r"""
        p_1 =
        \frac{OR \cdot p_0}
        {1 - p_0 + OR \cdot p_0}
        """)

        p0_calc = st.number_input(
            "Baseline Event Probability (p₀)",
            min_value=0.0001,
            max_value=0.9999,
            value=0.20,
            key="logreg_p0_calc"
        )

        OR_calc = st.number_input(
            "Target Odds Ratio",
            min_value=0.01,
            value=1.50,
            key="logreg_or_calc"
        )

        if st.button("Compute p₁", key="logreg_compute_p1"):

            p1_calc = (OR_calc * p0_calc) / (1 - p0_calc + OR_calc * p0_calc)
            st.success(f"Estimated p₁ = {round(p1_calc,4)}")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance", expanded=False):
        st.markdown("""
**Event Rate (p)**

Sources:
• Registry
• Published prevalence
• Pilot study

Avoid unrealistically small p unless justified.

---

**Odds Ratio**

Should be clinically meaningful.
OR near 1.1 requires very large sample size.

---

**Number of Predictors**

Include variables you will retain in final model.
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    p_event = st.number_input(
        "Overall Event Probability (p)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        key="logreg_p_event"
    )

    OR = st.number_input(
        "Target Odds Ratio (OR)",
        min_value=0.01,
        value=1.50,
        key="logreg_or_plan"
    )

    n_predictors = st.number_input(
        "Number of Predictors",
        min_value=1,
        value=5,
        key="logreg_predictors"
    )

    if st.button("Calculate Sample Size (Logistic Regression)", key="logreg_calc_n"):

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        ln_or = math.log(OR)

        if ln_or == 0:
            st.error("OR cannot equal 1 (no effect).")
        else:

            # Wald formula
            n_raw = ((Z_alpha + Z_beta) ** 2) / (
                p_event * (1 - p_event) * (ln_or ** 2)
            )

            n = math.ceil(n_raw)

            # Dropout adjustment
            n_adj = math.ceil(n / (1 - dropout_rate))

            # EPV check
            required_events = 10 * n_predictors
            total_events = n_adj * p_event

            st.markdown("### 🔎 Intermediate Values")

            st.write(f"Zα = {round(Z_alpha,4)}")
            st.write(f"Zβ = {round(Z_beta,4)}")
            st.write(f"ln(OR) = {round(ln_or,4)}")
            st.write(f"p(1-p) = {round(p_event*(1-p_event),4)}")

            st.latex(rf"""
            n =
            \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)})^2}}
            {{{round(p_event*(1-p_event),4)} \cdot ({round(ln_or,4)})^2}}
            """)

            st.success(f"Required Sample Size (adjusted): {n_adj}")
            st.write(f"Before Dropout Adjustment: {n}")

            # EPV safety check
            st.markdown("### 🔎 EPV Stability Check")

            st.write(f"Required events (10×predictors): {required_events}")
            st.write(f"Expected events: {round(total_events,1)}")

            if total_events < required_events:
                st.warning(
                    "⚠ EPV rule not satisfied (events < 10 per predictor). "
                    "Model may be unstable."
                )
            else:
                st.success("✔ EPV rule satisfied.")

            # Thesis paragraph
            sided_txt = "two-sided" if two_sided else "one-sided"

            st.markdown("### 📄 Copy for Thesis / Manuscript")

            st.code(f"""
Sample size for logistic regression ({sided_txt}) was calculated using
Wald approximation based on a target odds ratio of {OR}
and an event probability of {p_event}.
With α={alpha} and power={power},
the required sample size was {n_adj} participants
(after adjusting for {dropout_rate*100:.1f}% anticipated dropout).
An EPV stability check was performed based on {n_predictors} predictors.
            """)
