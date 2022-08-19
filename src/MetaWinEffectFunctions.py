"""
Functions for calculation of effect sizes and their variances
"""

import math
from typing import Optional, Tuple


class MetaWinEffectFunction:
    def __init__(self):
        self.name = ""
        self.citations = []
        self.calculate = None
        self.log_transformed = False
        self.z_transformed = False


# Hedges' d
def calculate_hedges_d(data, row, options) -> Tuple[Optional[float], Optional[float]]:
    try:
        control_mean = data.value(row, data.col_number(options.control_means)).value
        treatment_mean = data.value(row, data.col_number(options.treatment_means)).value
        control_sd = data.value(row, data.col_number(options.control_sd)).value
        treatment_sd = data.value(row, data.col_number(options.treatment_sd)).value
        control_n = data.value(row, data.col_number(options.control_n)).value
        treatment_n = data.value(row, data.col_number(options.treatment_n)).value
        j = 1 - (3 / (4*(control_n + treatment_n - 2) - 1))
        s = math.sqrt(((treatment_n - 1)*treatment_sd**2 + (control_n - 1)*control_sd**2) /
                      (treatment_n + control_n - 2))
        e = (treatment_mean - control_mean) * j / s
        v = (treatment_n + control_n)/(treatment_n * control_n) + e**2 / (2 * (treatment_n + control_n))
        e = check_polarity(e, data, row, options)
    except:
        e = None
        v = None
    return e, v


def hedges_d_function() -> MetaWinEffectFunction:
    f = MetaWinEffectFunction()
    f.name = "Hedges\' d"
    f.citations.append("Hedges_Olkin_1985")
    f.calculate = calculate_hedges_d
    return f


# ln Response Ratio
def calculate_ln_rr(data, row, options) -> Tuple[Optional[float], Optional[float]]:
    try:
        control_mean = data.value(row, data.col_number(options.control_means)).value
        treatment_mean = data.value(row, data.col_number(options.treatment_means)).value
        control_sd = data.value(row, data.col_number(options.control_sd)).value
        treatment_sd = data.value(row, data.col_number(options.treatment_sd)).value
        control_n = data.value(row, data.col_number(options.control_n)).value
        treatment_n = data.value(row, data.col_number(options.treatment_n)).value
        e = math.log(treatment_mean / control_mean)
        v = treatment_sd**2 / (treatment_n * treatment_mean**2) + control_sd**2 / (control_n * control_mean**2)
        e = check_polarity(e, data, row, options)
    except:
        e = None
        v = None
    return e, v


def ln_rr_function() -> MetaWinEffectFunction:
    f = MetaWinEffectFunction()
    f.name = "ln Response Ratio"
    f.citations.append("Hedges_et_1999")
    f.calculate = calculate_ln_rr
    f.log_transformed = True
    return f


# ln Odds Ratio
def calculate_odds_ratio(data, row, options) -> Tuple[Optional[float], Optional[float]]:
    try:
        control_response = data.value(row, data.col_number(options.control_response)).value
        control_no_response = data.value(row, data.col_number(options.control_no_response)).value
        treatment_response = data.value(row, data.col_number(options.treatment_response)).value
        treatment_no_response = data.value(row, data.col_number(options.treatment_no_response)).value
        control_n = control_response + control_no_response
        treatment_n = treatment_response + treatment_no_response
        total_n = control_n + treatment_n
        observed = treatment_response
        expected = (control_response + treatment_response) * treatment_n / total_n
        v = expected * (treatment_n / total_n) * ((control_no_response + treatment_no_response)/(total_n - 1))
        e = (observed - expected) / v
        v = 1 / v
        e = check_polarity(e, data, row, options)
    except:
        e = None
        v = None
    return e, v


def odds_ratio_function() -> MetaWinEffectFunction:
    f = MetaWinEffectFunction()
    f.name = "ln Odds Ratio"
    f.citations.extend(["Berlin_et_1989", "LAbbe_et_1987", "Mantel_and_Haenszel_1959", "Normand_1999"])
    f.calculate = calculate_odds_ratio
    f.log_transformed = True
    return f


# Rate Difference
def calculate_rate_difference(data, row, options) -> Tuple[Optional[float], Optional[float]]:
    try:
        control_response = data.value(row, data.col_number(options.control_response)).value
        control_no_response = data.value(row, data.col_number(options.control_no_response)).value
        treatment_response = data.value(row, data.col_number(options.treatment_response)).value
        treatment_no_response = data.value(row, data.col_number(options.treatment_no_response)).value
        control_n = control_response + control_no_response
        treatment_n = treatment_response + treatment_no_response
        control_rate = control_response / control_n
        treatment_rate = treatment_response / treatment_n
        e = treatment_rate - control_rate
        v = treatment_rate*(1 - treatment_rate)/treatment_n + control_rate*(1 - control_rate)/control_n
        e = check_polarity(e, data, row, options)
    except:
        e = None
        v = None
    return e, v


def rate_difference_function() -> MetaWinEffectFunction:
    f = MetaWinEffectFunction()
    f.name = "Rate Difference"
    f.citations.extend(["Berlin_et_1989", "DerSimonian_Laird_1986", "LAbbe_et_1987", "Normand_1999"])
    f.calculate = calculate_rate_difference
    return f


# ln Relative Rate
def calculate_relative_rate(data, row, options) -> Tuple[Optional[float], Optional[float]]:
    try:
        control_response = data.value(row, data.col_number(options.control_response)).value
        control_no_response = data.value(row, data.col_number(options.control_no_response)).value
        treatment_response = data.value(row, data.col_number(options.treatment_response)).value
        treatment_no_response = data.value(row, data.col_number(options.treatment_no_response)).value
        control_n = control_response + control_no_response
        treatment_n = treatment_response + treatment_no_response
        control_rate = control_response / control_n
        treatment_rate = treatment_response / treatment_n
        if treatment_rate == 0:
            raise ValueError
        e = math.log(treatment_rate / control_rate)
        v = (1 - treatment_rate)/(treatment_n*treatment_rate) + (1 - control_rate)/(control_n*control_rate)
        e = check_polarity(e, data, row, options)
    except:
        e = None
        v = None
    return e, v


def relative_rate_function() -> MetaWinEffectFunction:
    f = MetaWinEffectFunction()
    f.name = "ln Relative Rate"
    f.citations.extend(["Greenland_1987", "LAbbe_et_1987", "Normand_1999"])
    f.calculate = calculate_relative_rate
    f.log_transformed = True
    return f


# Fisher's Z-transform
def calculate_fishers_z(data, row, options) -> Tuple[Optional[float], Optional[float]]:
    try:
        r = data.value(row, data.col_number(options.correlation)).value
        n = data.value(row, data.col_number(options.correlation_n)).value
        e = math.log((1 + r)/(1 - r)) / 2
        v = 1 / (n - 3)
        if v < 0:
            raise ValueError
        e = check_polarity(e, data, row, options)
    except:
        e = None
        v = None
    return e, v


def fishers_z_function() -> MetaWinEffectFunction:
    f = MetaWinEffectFunction()
    f.name = "Fisher\'s Z-transform"
    f.citations.extend(["Cooper_1998", "Fisher_1928", "Rosenthal_1991"])
    f.calculate = calculate_fishers_z
    f.z_transformed = True
    return f


# Logit
def calculate_logit(data, row, options) -> Tuple[Optional[float], Optional[float]]:
    try:
        p = data.value(row, data.col_number(options.probability)).value
        n = data.value(row, data.col_number(options.probability_n)).value
        e = math.log(p/(1 - p))
        v = math.sqrt(1/(n*p) + 1/(n*(1-p)))
        e = check_polarity(e, data, row, options)
    except:
        e = None
        v = None
    return e, v


def logit_function() -> MetaWinEffectFunction:
    f = MetaWinEffectFunction()
    f.name = "Logit"
    f.citations.append("Mengerson_Gurevitch_2013")
    f.calculate = calculate_logit
    return f


def check_polarity(e: float, data, row, options) -> float:
    """
    determine polarity for effect size

    if the polarity determining value is a number, reverse polarity if this number is negative
    if the polarity determining value is a string, reverse polarity if this string is a negative sign "-"
    """
    if options.polarity is not None:
        p = data.value(row, data.col_number(options.polarity))
        if p is not None:
            p = p.value
            try:  # is the indicator a number
                p = float(p)
                if p < 0:
                    return -e
            except ValueError:  # or a string
                if p == "-":
                    return -e
    return e
