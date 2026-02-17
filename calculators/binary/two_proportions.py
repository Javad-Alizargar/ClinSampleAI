
# ==========================================
# Two Proportions — Sample Size
# ==========================================

import math

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_proportion,
    validate_positive
)


def calculate_two_proportions(
    alpha: float,
    power: float,
    p1: float,
    p2: float,
    allocation_ratio: float = 1.0,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for comparing two independent proportions.

    allocation_ratio = n2 / n1

    Uses pooled normal approximation.
    """

    p1 = validate_proportion(p1)
    p2 = validate_proportion(p2)
    validate_positive(allocation_ratio, "Allocation ratio")

    if p1 == p2:
        raise ValueError("p1 must differ from p2.")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    r = allocation_ratio
    p = (p1 + p2) / 2

    numerator = (
        Z_alpha * math.sqrt(2 * p * (1 - p)) +
        Z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2

    denominator = (p1 - p2) ** 2

    n1_raw = (1 + 1/r) * (numerator / denominator)
    n2_raw = r * n1_raw

    n1 = ceil_int(n1_raw)
    n2 = ceil_int(n2_raw)

    n1_final = adjust_for_dropout(n1, dropout_rate)
    n2_final = adjust_for_dropout(n2, dropout_rate)

    return {
        "n_group1": n1_final,
        "n_group2": n2_final,
        "n_total": n1_final + n2_final,
        "n_before_dropout_group1": n1,
        "n_before_dropout_group2": n2,
        "formula": "Pooled normal approximation for two proportions",
        "assumptions": [
            "Independent groups",
            "Large sample approximation",
            "Allocation ratio specified"
        ]
    }
