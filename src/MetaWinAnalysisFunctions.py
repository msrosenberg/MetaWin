"""
Primary analysis module

This module contains the major mathematical analyses in the program
"""

import math
from typing import Tuple, Optional
from collections import namedtuple

import numpy
import scipy.stats

import MetaWinConstants
from MetaWinConstants import mean_data_tuple
from MetaWinUtils import create_output_table, inline_float, interval_to_str, get_citation, exponential_label, \
    prob_z_score
import MetaWinCharts
import MetaWinWidgets
from MetaWinLanguage import get_text


heterogeneity_test_tuple = namedtuple("heterogeneity_test_tuple", ["source", "q", "df", "p_chi", "p_rand"])

predictor_test_tuple = namedtuple("predictor_test_tuple", ["predictor", "value", "se", "p_norm"])

simple_ma_values = namedtuple("simple_ma_values", ["mean_data", "pooled_var", "qt", "df", "p", "i2"])

group_ma_values = namedtuple("group_ma_values", ["global_values", "group_mean_values", "group_het_values",
                                                 "model_het_values", "error_het_values"])

reg_ma_values = namedtuple("reg_ma_values", ["global_values", "model_het_values", "error_het_values",
                                             "predictors"])

i2_values = namedtuple("i2_values", ["source", "i2", "i2_lower", "i2_upper"])


# --- failsafe numbers ---
def failsafe_numbers(options, output_blocks: list, n: int, e_data, v_data, mean_e, pooled_var,  sum_w, sum_ew,
                     decimal_places: int = 4) -> list:
    citations = []
    if options.rosenberg_failsafe is not None:
        if options.random_effects:
            output, rosenberg_n, citation = rosenberg_failsafe_random(e_data, v_data, options.rosenberg_failsafe,
                                                                      decimal_places)
        else:
            output, rosenberg_n, citation = rosenberg_failsafe_fixed(n, sum_ew, sum_w, options.rosenberg_failsafe,
                                                                     decimal_places)
        output_blocks.extend(output)
        citations.append(citation)

    if options.rosenthal_failsafe is not None:
        if options.random_effects:
            tmp_v = v_data + pooled_var
        else:
            tmp_v = v_data
        output, rosenthal_n, citation = rosenthal_failsafe(e_data, tmp_v, options.rosenthal_failsafe, decimal_places)
        output_blocks.extend(output)
        citations.append(citation)

    if options.orwin_failsafe is not None:
        output, orwin_n, citation = orwin_failsafe(n, mean_e, options.orwin_failsafe, decimal_places)
        output_blocks.extend(output)
        citations.append(citation)

    return citations


def rosenberg_failsafe_fixed(n: int, sum_ew: float, sum_w: float, alpha: float = 0.05,
                             decimal_places: int = 4) -> Tuple[list, float, str]:
    citation = "Rosenberg_2005"
    # assume normal distribution
    z = scipy.stats.norm.ppf(alpha/2)
    k_norm = (n / sum_w) * (sum_ew**2 / z**2 - sum_w)
    if k_norm < 0:
        k_norm = 0

    # assume adding a single study of weight k
    t_score = scipy.stats.t.ppf(alpha/2, n)
    k_1 = (n / sum_w) * (sum_ew**2 / t_score**2 - sum_w)
    if k_1 < 0:
        k_1 = 0

    # assume adding k studies of mean weight
    k_star = 1
    iters = 0
    df = n - 1
    while (iters < 1000) and (round(k_star) != round(df + 1 - n)):
        df = n + k_star - 1
        t_score = scipy.stats.t.ppf(alpha / 2, df)
        k_star = (n / sum_w) * (sum_ew**2 / t_score**2 - sum_w)
        iters += 1
    if k_star < 0:
        k_star = 0

    rosenberg_output = [["<h3>Rosenberg's Fail-safe Number</h3>"],
                        ["→ {}: ".format(get_text("Citation")) + get_citation(citation),
                         "→ alpha: " + format(alpha, inline_float(decimal_places))],
                        ["Fail-safe n (normal distribution) = " + format(k_norm, inline_float(decimal_places)),
                         "Fail-safe n (t distribution, 1 study of n × avg weight) = " +
                         format(k_1, inline_float(decimal_places)),
                         "Fail-safe n (t distribution, n studies of avg weight) = " +
                         format(k_star, inline_float(decimal_places))]]
    return rosenberg_output, k_norm, citation


def rosenberg_failsafe_random(effects, variances, alpha: float = 0.05,
                              decimal_places: int = 4) -> Tuple[list, float, str]:
    citation = "Rosenberg_2005"
    n = len(effects)
    weights = numpy.reciprocal(variances)
    _, _, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(effects, weights)
    df = n - 1
    pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
    rosenberg_output = [["<h3>Rosenberg's Fail-safe Number</h3>"],
                        ["→ {}: ".format(get_text("Citation")) + get_citation(citation),
                         "→ alpha: " + format(alpha, inline_float(decimal_places))]]
    output = []
    if pooled_var > 0:
        # assume adding a single study of weight k
        rw = numpy.reciprocal(variances + pooled_var)
        sum_erw = numpy.sum(effects * rw)
        sum_rw = numpy.sum(rw)

        t_score = scipy.stats.t.ppf(alpha / 2, n)
        k = sum_erw ** 2 / t_score ** 2 - sum_rw
        if k < 0:
            k = 0
        iters = 0
        pooled_new = 0
        quit_loop = False
        while (iters < 1000) and not quit_loop:
            iters += 1
            r_mean = sum_ew / (sum_w + k)
            qtr = numpy.sum(weights * numpy.square(effects - r_mean))
            qtr += k * r_mean**2  # add additional study of zero effect and k weight to Qt
            # recalculate pooled var
            pooled_new = (qtr - n) / (sum_w + k - (sum_w2 + k**2) / (sum_w + k))
            if pooled_new > 0:
                rw = numpy.reciprocal(variances + pooled_new)
                sum_erw = numpy.sum(effects * rw)
                sum_rw = numpy.sum(rw)
                tmp_k = sum_erw**2 / t_score**2 - sum_rw
                if round(k) == round(tmp_k):
                    quit_loop = True
                else:
                    k = tmp_k
            else:
                quit_loop = True
        k_1 = k * n / sum_w
        if k_1 < 0:
            k_1 = 0
        if pooled_new > 0:
            output.append("Fail-safe n (t distribution, 1 study of n × avg weight) = " +
                          format(k_1, inline_float(decimal_places)))
        else:
            output.append("Fail-safe n (t distribution, 1 study of n × avg weight) = " + get_text("rosenberg_fs_error"))

        # assume adding k studies of mean weight
        rw = numpy.reciprocal(variances + pooled_var)
        sum_erw = numpy.sum(effects * rw)
        t_score = scipy.stats.t.ppf(alpha / 2, n)
        k = sum_erw**2 / t_score**2 - sum_rw
        if k < 0:
            k = 0
        quit_loop = False
        iters = 0
        while (iters < 1000) and not quit_loop:
            iters += 1
            r_mean = sum_ew / (sum_w + k)
            qtr = numpy.sum(weights * numpy.square(effects - r_mean))
            # add extra studies to Qt estimate
            j = round(k * n / sum_w)
            extra_w2 = 0
            for i in range(j):
                qtr += (sum_w / n) * r_mean**2
                extra_w2 += (sum_w / n)**2
            # recalculate pooled var
            pooled_new = (qtr - n - 1 + j) / (sum_w + k - (sum_w2 + extra_w2) / (sum_w + k))
            if pooled_new > 0:
                rw = numpy.reciprocal(variances + pooled_new)
                sum_erw = numpy.sum(effects * rw)
                sum_rw = numpy.sum(rw)
                t_score = scipy.stats.t.ppf(alpha / 2, n - 1 + j)
                tmp_k = sum_erw**2 / t_score**2 - sum_rw
                if j == round(tmp_k*n/sum_w):
                    quit_loop = True
                else:
                    k = tmp_k
            else:
                quit_loop = True
        k_star = k * n / sum_w
        if k_star < 0:
            k_star = 0
        if pooled_new > 0:
            output.append("Fail-safe n (t distribution, n studies of avg weight) = " +
                          format(k_star, inline_float(decimal_places)))
        else:
            output.append("Fail-safe n (t distribution, n studies of avg weight) = " + get_text("rosenberg_fs_error"))

    else:
        output.append(get_text("rosenberg_fs_rand"))
    rosenberg_output.append(output)

    return rosenberg_output, 0, citation


def rosenthal_failsafe(effects, variances, alpha: float = 0.05, decimal_places: int = 4) -> Tuple[list, float, str]:
    citation = "Rosenthal_1979"
    sum_z = numpy.sum(effects / numpy.sqrt(variances))
    k = sum_z**2 / scipy.stats.norm.ppf(alpha/2)**2 - len(effects)
    if k < 0:
        k = 0
    rosenthal_output = [["<h3>Rosenthal's Fail-safe Number</h3>"],
                        ["→ {}: ".format(get_text("Citation")) + get_citation(citation),
                         "→ alpha: " + format(alpha, inline_float(decimal_places))],
                        ["Fail-safe n = " + format(k, inline_float(decimal_places))]]
    return rosenthal_output, k, citation


def orwin_failsafe(n: int, mean_e: float, minimal_e: float, decimal_places: int = 4) -> Tuple[list, float, str]:
    citation = "Orwin_1983"
    k = n * (mean_e - minimal_e) / minimal_e
    if k < 0:
        k = 0
    orwin_output = [["<h3>Orwin's Fail-safe Number</h3>"],
                    ["→ {}: ".format(get_text("Citation")) + get_citation(citation),
                     "→ Minimal Effect Size: " + format(minimal_e, inline_float(decimal_places))],
                    ["Fail-safe n = " + format(k, inline_float(decimal_places))]]
    return orwin_output, k, citation


# --- pooled variance calculations ---
def pooled_var_no_structure(qt, sum_w, sum_w2, df: int) -> float:
    pooled = (qt - df) / (sum_w - sum_w2 / sum_w)
    return max(pooled, 0)


def pooled_var_group_structure(qe, group_w_sums: list, n: int, g_cnt: int) -> float:
    denominator = 0
    for g in group_w_sums:
        sum_w, sum_w2 = g[0], g[1]
        denominator += sum_w - sum_w2/sum_w
    pooled = (qe - (n - g_cnt)) / denominator
    return max(pooled, 0)


def pooled_var_regression_structure(qe, n: int, sum_w, sum_wx, sum_wx2, x_data,  w_data) -> float:
    d_sum = 0
    for j in range(n):
        term2 = 2*x_data[j] * sum_wx
        term3 = x_data[j]**2 * sum_w
        d_sum += w_data[j]**2 * ((sum_wx2 - term2 + term3)/(sum_w*sum_wx2 - sum_wx**2))
    pooled = (qe - (n-2))/(sum_w - d_sum)
    return max(pooled, 0)


def pooled_var_glm(qe, n: int, w: numpy.array, x: numpy.array) -> float:
    np = numpy.shape(x)[1] - 1
    numerator = qe - (n - np - 1)
    xt = numpy.transpose(x)
    xtwxinv = numpy.linalg.inv(numpy.matmul(numpy.matmul(xt, w), x))
    val = numpy.matmul(numpy.matmul(numpy.matmul(numpy.matmul(w, x), xtwxinv), xt), w)
    pooled = numerator / (numpy.trace(w) - numpy.trace(val))
    return max(pooled, 0)


# --- basic calculations ---
def mean_effect_var_and_q(e: numpy.array, w: numpy.array):
    """
    for a set of effects and weights, calculate weighted mean, it's variance, and q, and report back these and
    some of the sums used in the calculations
    """
    sum_ew = numpy.sum(e * w)
    sum_w = numpy.sum(w)
    sum_w2 = numpy.sum(numpy.square(w))
    mean_e = sum_ew / sum_w
    var_e = 1 / sum_w
    qt = numpy.sum(w*numpy.square(e - mean_e))
    return mean_e, var_e, qt, sum_w, sum_w2, sum_ew


def median_effect(e: numpy.array, w: numpy.array):
    """
    for a set of effects and weights, calculate the weighted median effect
    """
    midp = numpy.sum(w)/2
    tmp_data = numpy.zeros(shape=(len(e), 2))
    tmp_data[:, 0] = e
    tmp_data[:, 1] = w
    tmp_data = tmp_data[tmp_data[:, 0].argsort()]  # sort into ascending order by effect size (1st column)
    i = 0
    rsum = tmp_data[0, 1]
    while rsum < midp:
        i += 1
        rsum += tmp_data[i, 1]
    if rsum == midp:  # in the unlikely event that the midpoint of the weights is on the boundary of two effect sizes
        return (tmp_data[i, 0] + tmp_data[i+1, 0]) / 2
    else:
        return tmp_data[i, 0]


def bootstrap_means(bootstrap_n, boot_data, obs_mean, pooled_var, random_effects: bool = False, alpha: float = 0.05,
                    progress_bar=None):
    """
    conduct a bootstrap test to create confidence intervals around mean effect size
    """
    if bootstrap_n is not None:
        rng = numpy.random.default_rng()
        all_means = [obs_mean]

        # if sender is not None:
        #     progress = MetaWinWidgets.progress_bar(sender, "Resampling Analysis", "Bootstrap Progress", bootstrap_n)
        # else:
        #     progress = None

        # f = 0.5  # count the observation as half less than itself
        f = 0
        for i in range(bootstrap_n):
            tmp_data = rng.choice(boot_data, len(boot_data))
            tmp_e = tmp_data[:, 0]
            tmp_v = tmp_data[:, 1]
            """
            for random effects models I'm keeping the process from MW2 where the pooled variance is only
            calculated once from all of the effect size data, rather than recalculated for each bootstrap
            replicate

            should consider whether this has to change or should be an either/or option
            """
            if random_effects:
                tmp_w = numpy.reciprocal(tmp_v + pooled_var)
            else:
                tmp_w = numpy.reciprocal(tmp_v)

            tmp_mean, *_ = mean_effect_var_and_q(tmp_e, tmp_w)
            if tmp_mean < obs_mean:
                f += 1
            # in MW2 we counted ties as 1/2, that doesn't seem to be common in the lit, but may be due to a lack
            # of imagination assuming one would never get a tie
            # elif tmp_mean_e == mean_e:
            #     f += 0.5
            all_means.append(tmp_mean)
            if progress_bar is not None:
                progress_bar.setValue(progress_bar.value() + 1)
        all_means.sort()
        lower_index = round((bootstrap_n + 1) * alpha / 2)
        upper_index = round(bootstrap_n - (bootstrap_n + 1) * alpha / 2)
        lower_bs_ci = all_means[lower_index]
        upper_bs_ci = all_means[upper_index]

        # bias-corrected bootstrap
        f /= (bootstrap_n + 1)
        z_score = -scipy.stats.norm.ppf(alpha / 2)
        z0 = scipy.stats.norm.ppf(f)
        lower_bias_index = round((bootstrap_n + 1) * scipy.stats.norm.cdf(2 * z0 - z_score))
        upper_bias_index = round((bootstrap_n + 1) * scipy.stats.norm.cdf(2 * z0 + z_score))
        if lower_bias_index < 0:
            lower_bias_index = 0
        if upper_bias_index > bootstrap_n:
            upper_bias_index = bootstrap_n
        lower_bias_ci = all_means[lower_bias_index]
        upper_bias_ci = all_means[upper_bias_index]
    else:
        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = None, None, None, None
    return lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci


def calc_i2(qt, n, alpha: float = 0.05):
    try:
        i2 = max(0, 100 * (qt - (n - 1))/qt)
        ln_h = math.log(math.sqrt(qt/(n - 1)))
        if qt > n - 1:
            se_ln_h = (math.log(qt) - math.log(n-1))/(2*(math.sqrt(2*qt)-math.sqrt(2*n - 3)))
        else:
            se_ln_h = math.sqrt((1/(2*(n - 2))) * (1 - (1/(3*(n - 2)**2))))
        z = -scipy.stats.norm.ppf(alpha / 2)
        lower_h = math.exp(ln_h - z*se_ln_h)
        upper_h = math.exp(ln_h + z*se_ln_h)
        lower_i2 = max(0, 100*(lower_h**2 - 1)/lower_h**2)
        upper_i2 = max(0, 100*(upper_h**2 - 1)/upper_h**2)
    except ZeroDivisionError:
        i2, lower_i2, upper_i2 = 0, 0, 0
    return i2, lower_i2, upper_i2


# --- common output ---
def mean_effects_table(effect_label, mean_effect_data, bootstrap_mean, decimal_places: int = 4, alpha: float = 0.05,
                       log_transformed: bool = False, inc_median: bool = True) -> list:
    """
    create a table of mean effect sizes and their confidence intervals

    if log transformed, add rows with the exponentiated (unlogged) results as well
    """
    output = []
    # col_headers = ["", "n", get_text("Mean"), get_text("Median"), "{:0.0%} CI".format(1 - alpha)]
    # col_formats = ["", "d", "f", "f", ""]

    col_headers = ["", "n", get_text("Mean")]
    col_formats = ["", "d", "f"]
    if inc_median:
        col_headers.append(get_text("Median"))
        col_formats.append("f")
    col_headers.append("{:0.0%} CI".format(1 - alpha))
    col_formats.append("")

    if bootstrap_mean is not None:
        col_headers.extend(["Bootstrap CI", "Bias-corrected CI"])
        col_formats.extend(["", ""])
    table_data = []
    for data in mean_effect_data:
        interval_str = interval_to_str(data.lower_ci, data.upper_ci, decimal_places)
        if data.name != "":
            row_name = data.name + " " + effect_label
        else:
            row_name = data.name
        # row_data = [row_name, data.n, data.mean, data.median, interval_str]
        row_data = [row_name, data.n, data.mean]
        if inc_median:
            row_data.append(data.median)
        row_data.append(interval_str)
        if bootstrap_mean is not None:
            row_data.append(interval_to_str(data.lower_bs_ci, data.upper_bs_ci, decimal_places))
            row_data.append(interval_to_str(data.lower_bias_ci, data.upper_bias_ci, decimal_places))
        table_data.append(row_data)
    if log_transformed:
        line_after = [len(mean_effect_data)-1]
        for data in mean_effect_data:
            tmp_mean = math.exp(data.mean)
            if inc_median:
                tmp_median = math.exp(data.median)
            else:
                tmp_median = None
            tmp_lower = math.exp(data.lower_ci)
            tmp_upper = math.exp(data.upper_ci)
            tmp_interval = interval_to_str(tmp_lower, tmp_upper, decimal_places)
            # row_data = [str(data.name + " " + format(exponential_label(effect_label))).strip(), data.n, tmp_mean,
            #             tmp_median, tmp_interval]
            row_data = [str(data.name + " " + format(exponential_label(effect_label))).strip(), data.n, tmp_mean]
            if inc_median:
                row_data.append(tmp_median)
            row_data.append(tmp_interval)
            if bootstrap_mean is not None:
                tmp_bs_lower = math.exp(data.lower_bs_ci)
                tmp_bs_upper = math.exp(data.upper_bs_ci)
                tmp_bias_lower = math.exp(data.lower_bias_ci)
                tmp_bias_upper = math.exp(data.upper_bias_ci)
                row_data.append(interval_to_str(tmp_bs_lower, tmp_bs_upper, decimal_places))
                row_data.append(interval_to_str(tmp_bias_lower, tmp_bias_upper, decimal_places))
            table_data.append(row_data)
    else:
        line_after = []
    create_output_table(output, table_data, col_headers, col_formats, decimal_places, line_after=line_after)
    return output


def heterogeneity_table(het_data, decimal_places: int = 4, total_line: bool = False,
                        randomization: Optional = None) -> list:
    """
    create a table of heterogeneity (Q stats)
    """
    output = []
    col_headers = [get_text("Source"), "Q", "df", "P(χ<sup>2</sup>)"]
    col_formats = ["", "f", "d", "f"]
    if randomization is not None:
        col_headers.append("P({})".format(get_text("randomization")))
        col_formats.append("")
    table_data = []
    for data in het_data:
        tmp_row = [data.source, data.q, data.df, data.p_chi]
        if randomization is not None:
            tmp_row.append(data.p_rand)
        table_data.append(tmp_row)
    if total_line:
        line_after = [len(het_data)-2]
    else:
        line_after = []
    create_output_table(output, table_data, col_headers, col_formats, decimal_places, line_after=line_after)
    return output


def predictor_table(predictor_data, decimal_places: int = 4, alpha: float = 0.05) -> list:
    """
    create a table of model regression/GLM predictors
    """
    output = []
    col_headers = [get_text("Predictor"), get_text("Value"), "SE", "{:0.0%} CI".format(1 - alpha), "P(Normal)"]
    col_formats = ["", "f", "f", "", "f"]
    table_data = []
    for data in predictor_data:
        tmp_lower, tmp_upper = scipy.stats.norm.interval(confidence=1 - alpha, loc=data.value, scale=data.se)
        tmp_row = [data.predictor, data.value, data.se, interval_to_str(tmp_lower, tmp_upper, decimal_places),
                   data.p_norm]
        table_data.append(tmp_row)
    create_output_table(output, table_data, col_headers, col_formats, decimal_places)
    return output


def i2_table(i2_data, decimal_places: int = 4, alpha: float = 0.05) -> list:
    """
    create a table of i2 values
    """
    output_blocks = []
    output = []
    col_headers = [get_text("Source"), "I<sup>2</sup>", "{:0.0%} CI".format(1 - alpha)]
    col_formats = ["", "f", ""]
    table_data = []
    for i in i2_data:
        tmp_row = [i.source, i.i2, interval_to_str(i.i2_lower, i.i2_upper, decimal_places)]
        table_data.append(tmp_row)
    create_output_table(output, table_data, col_headers, col_formats, decimal_places)
    output_blocks.append(output)
    output_blocks.append(["→ {}: ".format(get_text("Citations")) + get_citation("Higgins_Thompson_2002") + ", " +
                         get_citation("Huedo-Medina_et_2006")])
    return output_blocks


def create_global_output(output_blocks: list, effect_label: str, mean_data, het_data, pooled_var, i2_data,
                         bootstrap_mean, decimal_places: int = 4,  alpha: float = 0.05, log_transformed: bool = False,
                         inc_median: bool = True):
    """
    create output for general global calculations (e.g., grand mean, Qtotal)
    """
    output_blocks.append(["<h4>{}</h4>".format(get_text("Heterogeneity"))])
    output_blocks.append(heterogeneity_table([het_data], decimal_places))
    output_blocks.append(["→ {}: ".format(get_text("Citation")) + get_citation("Hedges_Olkin_1985")])
    output_blocks.extend(i2_table(i2_data, decimal_places, alpha))

    output_blocks.append(["<h4>Mean Effect Size</h4>"])
    output_blocks.append(mean_effects_table(effect_label, [mean_data], bootstrap_mean, decimal_places, alpha,
                                            log_transformed, inc_median=inc_median))

    sqrt_pooled = math.sqrt(pooled_var)
    ratio = sqrt_pooled / mean_data.avg_var
    output = ["Sqrt Pooled Variance = " + format(sqrt_pooled, inline_float(decimal_places)),
              "Mean Study Variance = " + format(mean_data.avg_var, inline_float(decimal_places)),
              "ratio = " + format(ratio, inline_float(decimal_places))]

    citations = ["Hedges_Olkin_1985", "Higgins_Thompson_2002", "Huedo-Medina_et_2006"]
    output_blocks.append(output)

    # output = ["AIC of Model: " + format(aic, inline_float(decimal_places))]
    # output_blocks.append(output)

    return citations


def output_filtered_bad(filtered: list, bad_data: list) -> list:
    """
    add list of pre-analysis filtered studies, as well as studies removed due to invalid data
    """
    output_blocks = []
    if len(filtered) > 0:
        output_blocks.append([get_text("Pre-filtered studies excluded from analysis") + ": " + ", ".join(filtered)])
    if len(bad_data) > 0:
        output_blocks.append([get_text("Studies with invalid data") + ": " + ", ".join(bad_data)])
    return output_blocks


# ---- I'm not convinced this is correct, which is why I'm removing it for now ---
# def calc_aic(q: float, n: int, p: int) -> float:
#     """
#     calculate AIC from q, n (sample size), and the number of parameters (p)
#     """
#     try:
#         return 2*p + n*(math.log(2*math.pi*q/n) + 1)
#     except ValueError:
#         return 0


# ---------- basic meta-analysis ----------
def simple_meta_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True,
                         sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    e_data = []
    w_data = []
    v_data = []
    bad_data = []
    boot_data = []
    study_names = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if (e is not None) and (v is not None) and (v > 0):
                e_data.append(e)
                w_data.append(1/v)
                v_data.append(v)
                boot_data.append([e, v])
                study_names.append(row.label)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)
    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)
    boot_data = numpy.array(boot_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    chart_data = None
    n = len(e_data)
    citations = []
    if n > 1:
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
        df = n - 1
        mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(e_data, w_data)
        median_e = median_effect(e_data, w_data)
        mean_v = numpy.sum(v_data) / n
        pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)

        if options.random_effects:
            ws_data = numpy.reciprocal(v_data + pooled_var)
            mean_e, var_e, qt, *_ = mean_effect_var_and_q(e_data, ws_data)
            median_e = median_effect(e_data, ws_data)
            output_blocks.append([get_text("Estimate of pooled variance") + ": " +
                                  format(pooled_var, inline_float(decimal_places))])

        p = 1 - scipy.stats.chi2.cdf(qt, df=df)

        if norm_ci:
            lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1-alpha, loc=mean_e, scale=math.sqrt(var_e))
        else:
            lower_ci, upper_ci = scipy.stats.t.interval(confidence=1-alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))

        if (options.bootstrap_mean is not None) and (sender is not None):
            progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
                                                       get_text("Conducting Bootstrap Analysis"),
                                                       options.bootstrap_mean)
        else:
            progress_bar = None
        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, boot_data,
                                                                                 mean_e, pooled_var,
                                                                                 options.random_effects, alpha,
                                                                                 progress_bar=progress_bar)

        plot_order = 0
        mean_data = mean_data_tuple(get_text("Mean"), plot_order, n, mean_e, median_e, var_e, mean_v,
                                    lower_ci, upper_ci, lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)
        het_data = heterogeneity_test_tuple(get_text("Total"), qt, df, p, None)
        i2, i2_lower, i2_upper = calc_i2(qt, n, alpha)
        i2_data = [i2_values(get_text("Total"), i2, i2_lower, i2_upper)]
        plot_order += 2

        # aic = calc_aic(qt, n, 1)
        # create chart data
        forest_data = [mean_data]
        for i in range(n):
            # individual study data has to use normal dist
            tmp_lower, tmp_upper = scipy.stats.norm.interval(confidence=1-alpha, loc=e_data[i], scale=math.sqrt(v_data[i]))
            study_data = mean_data_tuple(study_names[i], plot_order, 0, e_data[i], None, 0, 0, tmp_lower, tmp_upper,
                                         None, None, None, None)
            forest_data.append(study_data)
            plot_order += 1

        # recreate without label
        mean_data = mean_data_tuple("", plot_order, n, mean_e, median_e, var_e, mean_v, lower_ci, upper_ci, lower_bs_ci,
                                    upper_bs_ci, lower_bias_ci, upper_bias_ci)
        # output
        new_cites = create_global_output(output_blocks, effect_sizes.label, mean_data, het_data, pooled_var, i2_data,
                                         options.bootstrap_mean, decimal_places, alpha, options.log_transformed)
        citations.extend(new_cites)

        new_cites = failsafe_numbers(options, output_blocks, n, e_data, v_data, mean_e, pooled_var, sum_w, sum_ew,
                                     decimal_places)
        citations.extend(new_cites)

        if options.create_graph:
            chart_data = MetaWinCharts.chart_forest_plot("basic analysis", effect_sizes.label, forest_data,
                                                         alpha, options.bootstrap_mean, normal_ci=norm_ci)

    else:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])
        qt, df, p, pooled_var, i2 = None, None, None, None, None
        mean_data = None

    return output_blocks, chart_data, simple_ma_values(mean_data, pooled_var, qt, df, p, i2), citations


# ---------- grouped meta-analysis ----------
def check_data_for_group(output_blocks, n, group_cnts, group_label) -> bool:
    if n < 2:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])
        return False
    if len(group_cnts) < 2:
        output_blocks.append([get_text("Fewer than two valid groups were identified in column {}").format(group_label)])
        return False
    all_good = True
    output = []
    for g in group_cnts:
        if group_cnts[g] < 2:
            output.append(get_text("Fewer than two valid studies were identified for group {} of "
                                   "column {}.").format(g, group_label))
            all_good = False
    if not all_good:
        output.append(get_text("Please filter problematic data to continue"))
        output_blocks.append(output)
    return all_good


def grouped_meta_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True,
                          sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    groups = options.groups
    e_data = []
    w_data = []
    v_data = []
    group_data = []
    bad_data = []
    boot_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            g = data.check_value(r, groups.position(), value_type=MetaWinConstants.VALUE_STRING)
            if (e is not None) and (v is not None) and (v > 0) and (g is not None):
                e_data.append(e)
                w_data.append(1 / v)
                v_data.append(v)
                group_data.append(g)
                boot_data.append([e, v])
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)
    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)
    boot_data = numpy.array(boot_data)
    group_names = sorted(set(group_data))
    group_cnts = {g: group_data.count(g) for g in group_names}
    group_data = numpy.array(group_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    chart_data = None
    n = len(e_data)
    g_cnt = len(group_names)
    citations = []
    if check_data_for_group(output_blocks, n, group_cnts, options.groups.label):
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
        # do enough to calculate the pooled variance
        group_w_sums = []
        qe = 0
        for group in group_names:
            group_mask = [g == group for g in group_data]
            group_e = e_data[group_mask]
            group_w = w_data[group_mask]
            (group_mean, group_var, group_qw, group_sum_w,
             group_sum_w2, group_sum_ew) = mean_effect_var_and_q(group_e, group_w)
            group_w_sums.append([group_sum_w, group_sum_w2])
            qe += group_qw

        pooled_var = pooled_var_group_structure(qe, group_w_sums, n, g_cnt)
        if options.random_effects:
            ws_data = numpy.reciprocal(v_data + pooled_var)
            mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(e_data, ws_data)
            median_e = median_effect(e_data, ws_data)
            output_blocks.append([get_text("Estimate of pooled variance") + ": " +
                                  format(pooled_var, inline_float(decimal_places))])
        else:
            ws_data = w_data
            mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(e_data, w_data)
            median_e = median_effect(e_data, w_data)

        group_het_values = []
        group_mean_values = []
        qe = 0
        chart_order = 2
        group_i2_values = []

        if ((options.bootstrap_mean is not None) or (options.randomize_model is not None)) and (sender is not None):
            if options.randomize_model is not None:
                total_steps = options.randomize_model
            else:
                total_steps = 0
            if options.bootstrap_mean is not None:
                total_steps += (g_cnt + 1)*options.bootstrap_mean
            progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
                                                       get_text("Conducting Bootstrap Analysis"), total_steps)
        else:
            progress_bar = None

        for group in group_names:
            group_mask = [g == group for g in group_data]
            group_e = e_data[group_mask]
            group_w = ws_data[group_mask]
            group_boot = boot_data[group_mask]
            group_n = len(group_e)
            group_df = group_n - 1
            group_mean, group_var, group_qw, _, _, _ = mean_effect_var_and_q(group_e, group_w)
            group_median = median_effect(group_e, group_w)
            qe += group_qw
            group_p = 1 - scipy.stats.chi2.cdf(group_qw, df=group_df)
            if norm_ci:
                group_lower, group_upper = scipy.stats.norm.interval(confidence=1 - alpha, loc=group_mean,
                                                                     scale=math.sqrt(group_var))
            else:
                group_lower, group_upper = scipy.stats.t.interval(confidence=1 - alpha, df=group_df, loc=group_mean,
                                                                  scale=math.sqrt(group_var))
            (group_lower_bs, group_upper_bs,
             group_lower_bias, group_upper_bias) = bootstrap_means(options.bootstrap_mean, group_boot,
                                                                   group_mean, pooled_var, options.random_effects,
                                                                   alpha, progress_bar=progress_bar)
            group_het_values.append(heterogeneity_test_tuple(group + " (within)", group_qw, group_df, group_p, ""))
            group_i2, group_i2_lower, group_i2_upper = calc_i2(group_qw, group_n, alpha)

            group_i2_values.append(i2_values(group + " (within)", group_i2, group_i2_lower, group_i2_upper))

            group_mean_values.append(mean_data_tuple(group, chart_order, group_n, group_mean, group_median, group_var,
                                                     0, group_lower, group_upper, group_lower_bs, group_upper_bs,
                                                     group_lower_bias, group_upper_bias))
            chart_order += 1

        mean_v = numpy.sum(v_data) / n
        if norm_ci:
            lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1 - alpha, loc=mean_e, scale=math.sqrt(var_e))
        else:
            lower_ci, upper_ci = scipy.stats.t.interval(confidence=1 - alpha, df=n-1, loc=mean_e, scale=math.sqrt(var_e))
        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, boot_data,
                                                                                 mean_e, pooled_var,
                                                                                 options.random_effects, alpha,
                                                                                 progress_bar=progress_bar)

        global_mean_data = mean_data_tuple(get_text("Global"), 0, n, mean_e, median_e, var_e, mean_v, lower_ci,
                                           upper_ci, lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)

        forest_data = [global_mean_data]
        forest_data.extend(group_mean_values)

        pqt = 1 - scipy.stats.chi2.cdf(qt, df=n-1)
        pqe = 1 - scipy.stats.chi2.cdf(qe, df=n-g_cnt)
        qm = qt - qe
        pqm = 1 - scipy.stats.chi2.cdf(qm, df=g_cnt-1)
        df = n-1

        global_het_data = heterogeneity_test_tuple(get_text("Total"), qt, df, pqt, "")

        i2, i2_lower, i2_upper = calc_i2(qt, n, alpha)
        i2_data = [i2_values(get_text("Total"), i2, i2_lower, i2_upper)]

        # aic = calc_aic(qe, n, len(group_names))

        # randomization test
        if options.randomize_model:
            nreps = options.randomize_model
            # decimal places to use for randomization-based p-value
            rand_p_dec = max(decimal_places, math.ceil(math.log10(nreps+1)))
            cnt = 1
            rng = numpy.random.default_rng()
            if progress_bar is not None:
                progress_bar.setLabelText(get_text("Conducting Randomization Analysis"))
            for rep in range(nreps):
                tmp_qe = 0
                # rand_group_data = rng.permutation(group_data)
                rand_e_data = rng.permutation(e_data)
                for group in group_names:
                    group_mask = [g == group for g in group_data]
                    group_e = rand_e_data[group_mask]
                    group_w = ws_data[group_mask]
                    _, _, group_qw, _, _, _ = mean_effect_var_and_q(group_e, group_w)
                    tmp_qe += group_qw
                tmp_qmodel = qt - tmp_qe
                if tmp_qmodel >= qm:
                    cnt += 1
                if progress_bar is not None:
                    progress_bar.setValue(progress_bar.value() + 1)
            p_random = cnt / (nreps + 1)
            p_random_str = format(p_random, inline_float(rand_p_dec))
        else:
            p_random_str = ""

        # output
        output_blocks.append(["<h3>{}</h3>".format(get_text("Group Results"))])
        output_blocks.append(["<h4>{}</h4>".format(get_text("Heterogeneity"))])
        output_blocks.append(heterogeneity_table(group_het_values, decimal_places))

        output_blocks.extend(i2_table(group_i2_values, decimal_places, alpha))

        model_het = heterogeneity_test_tuple("{} ({})".format(get_text("Model"), get_text("Between")),
                                             qm, g_cnt - 1, pqm, p_random_str)
        error_het = heterogeneity_test_tuple("{} ({})".format(get_text("Error"), get_text("Within")),
                                             qe, n - g_cnt, pqe, "")
        model_table = [model_het, error_het, global_het_data]
        output_blocks.append(heterogeneity_table(model_table, decimal_places, total_line=True,
                                                 randomization=options.randomize_model))

        output_blocks.append(["<h4>{}</h4>".format(get_text("Mean Effect Sizes"))])
        output_blocks.append(mean_effects_table(effect_sizes.label, group_mean_values, options.bootstrap_mean,
                             decimal_places, alpha, options.log_transformed))

        output_blocks.append(["<h3>{}</h3>".format(get_text("Global Results"))])

        new_cites = create_global_output(output_blocks, effect_sizes.label, global_mean_data, global_het_data,
                                         pooled_var, i2_data, options.bootstrap_mean, decimal_places, alpha,
                                         options.log_transformed)
        citations.extend(new_cites)

        if options.create_graph:
            chart_data = MetaWinCharts.chart_forest_plot("grouped analysis", effect_sizes.label, forest_data, alpha,
                                                         options.bootstrap_mean, groups.label, normal_ci=norm_ci)

        global_values = simple_ma_values(global_mean_data, pooled_var, qt, df, pqt, i2)
    else:
        global_values = None
        group_mean_values = None
        group_het_values = None
        model_het = None
        error_het = None

    return (output_blocks, chart_data,
            group_ma_values(global_values, group_mean_values, group_het_values, model_het, error_het), citations)


# ---------- cumulative meta-analysis ----------
def cumulative_meta_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True,
                             sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    order = options.cumulative_order
    bad_data = []
    tmp_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            g = data.check_value(r, order.position(), value_type=MetaWinConstants.VALUE_ANY)
            if (e is not None) and (v is not None) and (v > 0) and (g is not None):
                tmp_data.append([g, e, v])
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)

    output_blocks = output_filtered_bad(filtered, bad_data)

    chart_data = None
    n = len(tmp_data)
    if n > 1:
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
        tmp_data.sort()
        e_data = []
        v_data = []
        w_data = []
        boot_data = []
        for data in tmp_data:
            e_data.append(data[1])
            v_data.append(data[2])
            w_data.append(1/data[2])
            boot_data.append([data[1], data[2]])
        e_data = numpy.array(e_data)
        w_data = numpy.array(w_data)
        v_data = numpy.array(v_data)
        boot_data = numpy.array(boot_data)

        cumulative_means = []
        cumulative_het = []

        if (options.bootstrap_mean is not None) and (sender is not None):
            total_steps = (n - 1)*options.bootstrap_mean
            progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
                                                       get_text("Conducting Bootstrap Analysis"), total_steps)
        else:
            progress_bar = None

        chart_order = 0
        for ns in range(2, n+1):
            ns_label = get_text("{} studies").format(ns)
            tmp_e = e_data[:ns]
            tmp_w = w_data[:ns]
            tmp_v = v_data[:ns]
            tmp_boot = boot_data[:ns]
            df = ns - 1
            mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(tmp_e, tmp_w)
            median_e = median_effect(tmp_e, tmp_w)
            mean_v = numpy.sum(tmp_v) / ns
            pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
            if options.random_effects:
                ws_data = numpy.reciprocal(tmp_v + pooled_var)
                mean_e, var_e, qt, *_ = mean_effect_var_and_q(tmp_e, ws_data)
            p = 1 - scipy.stats.chi2.cdf(qt, df=df)
            if norm_ci:
                lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1-alpha, loc=mean_e, scale=math.sqrt(var_e))
            else:
                lower_ci, upper_ci = scipy.stats.t.interval(confidence=1-alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))
            lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, tmp_boot,
                                                                                     mean_e, pooled_var,
                                                                                     options.random_effects, alpha,
                                                                                     progress_bar=progress_bar)
            mean_data = mean_data_tuple(ns_label, chart_order, ns, mean_e, median_e, var_e, mean_v, lower_ci, upper_ci,
                                        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)
            cumulative_means.append(mean_data)
            het_data = heterogeneity_test_tuple("{} Qtotal".format(ns_label), qt, df, p, None)
            cumulative_het.append(het_data)
            chart_order += 1

        # output
        output_blocks.append(["<h3>{}</h3>".format(get_text("Cumulative Results"))])
        output_blocks.append(["<h4>{}</h4>".format(get_text("Heterogeneity"))])
        output_blocks.append(heterogeneity_table(cumulative_het, decimal_places))

        output_blocks.append(["<h4>{}</h4>".format(get_text("Mean Effect Sizes"))])
        output_blocks.append(mean_effects_table(effect_sizes.label, cumulative_means, options.bootstrap_mean,
                             decimal_places, alpha, options.log_transformed))

        if options.create_graph:
            chart_data = MetaWinCharts.chart_forest_plot("cumulative analysis", effect_sizes.label,
                                                         cumulative_means, alpha, options.bootstrap_mean, order.label,
                                                         normal_ci=norm_ci)

    else:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])

    return output_blocks, chart_data


# ---------- simple regression meta-analysis ----------
def calculate_regression_ma_values(e_data, w_data, x_data, sum_w, sum_we, qt):
    sum_wxe = numpy.sum(w_data * x_data * e_data)
    sum_wx = numpy.sum(w_data * x_data)
    sum_wx2 = numpy.sum(w_data * numpy.square(x_data))
    b1_slope = (sum_wxe - sum_wx * sum_we / sum_w) / (sum_wx2 - sum_wx ** 2 / sum_w)
    b0_intercept = (sum_we - b1_slope * sum_wx) / sum_w
    var_b1 = 1 / (sum_wx2 - sum_wx**2 / sum_w)
    var_b0 = 1 / (sum_w - sum_wx**2 / sum_wx2)
    qm = b1_slope ** 2 / var_b1
    qe = qt - qm
    return qm, qe, b1_slope, b0_intercept, var_b1, var_b0, sum_wx, sum_wx2


def regression_meta_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True,
                             sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    ind_var = options.independent_variable
    e_data = []
    w_data = []
    v_data = []
    x_data = []
    bad_data = []
    boot_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            x = data.check_value(r, ind_var.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if (e is not None) and (v is not None) and (v > 0) and (x is not None):
                e_data.append(e)
                w_data.append(1 / v)
                v_data.append(v)
                x_data.append(x)
                boot_data.append([e, v])
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)
    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)
    x_data = numpy.array(x_data)
    boot_data = numpy.array(boot_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    chart_data = None
    model_het = None
    error_het = None
    global_values = None
    predictors = None
    n = len(e_data)
    citations = []
    if n > 1:
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
        # calculate various regression sums
        mean_e, var_e, qt, sum_w, sum_w2, sum_we = mean_effect_var_and_q(e_data, w_data)
        (qm, qe, b1_slope, b0_intercept,
         var_b1, var_b0, sum_wx, sum_wx2) = calculate_regression_ma_values(e_data, w_data, x_data, sum_w, sum_we, qt)
        pooled_var = pooled_var_regression_structure(qe, n, sum_w, sum_wx, sum_wx2, x_data, w_data)

        if options.random_effects:
            output_blocks.append([get_text("Estimate of pooled variance") + ": " +
                                  format(pooled_var, inline_float(decimal_places))])
            ws_data = numpy.reciprocal(v_data + pooled_var)
            mean_e, var_e, qt, sum_ws, sum_ws2, sum_wse = mean_effect_var_and_q(e_data, ws_data)
            (qm, qe, b1_slope, b0_intercept,
             var_b1, var_b0, _, _) = calculate_regression_ma_values(e_data, ws_data, x_data, sum_ws, sum_wse, qt)
        else:
            ws_data = w_data
            sum_ws = sum_w
            sum_wse = sum_we

        if ((options.bootstrap_mean is not None) or (options.randomize_model is not None)) and (sender is not None):
            if options.randomize_model is not None:
                total_steps = options.randomize_model
            else:
                total_steps = 0
            if options.bootstrap_mean is not None:
                total_steps += options.bootstrap_mean
            progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
                                                       get_text("Conducting Bootstrap Analysis"),
                                                       total_steps)
        else:
            progress_bar = None

        median_e = median_effect(e_data, ws_data)
        mean_v = numpy.sum(v_data) / n
        if norm_ci:
            lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1 - alpha, loc=mean_e, scale=math.sqrt(var_e))
        else:
            lower_ci, upper_ci = scipy.stats.t.interval(confidence=1 - alpha, df=n-1, loc=mean_e, scale=math.sqrt(var_e))
        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, boot_data,
                                                                                 mean_e, pooled_var,
                                                                                 options.random_effects, alpha,
                                                                                 progress_bar=progress_bar)

        mean_data = mean_data_tuple(get_text("Global"), 0, n, mean_e, median_e, var_e, mean_v, lower_ci, upper_ci,
                                    lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)

        pqt = 1 - scipy.stats.chi2.cdf(qt, df=n-1)
        pqe = 1 - scipy.stats.chi2.cdf(qe, df=n-2)
        pqm = 1 - scipy.stats.chi2.cdf(qm, df=1)

        global_het_data = heterogeneity_test_tuple(get_text("Total"), qt, n-1, pqt, "")

        i2, i2_lower, i2_upper = calc_i2(qt, n, alpha)
        i2_data = [i2_values(get_text("Total"), i2, i2_lower, i2_upper)]

        # aic = calc_aic(qe, n, 2)

        global_values = simple_ma_values(mean_data, pooled_var, qt, n-1, pqt, i2)

        # randomization test
        if options.randomize_model:
            if progress_bar is not None:
                progress_bar.setLabelText(get_text("Conducting Randomization Analysis"))
            nreps = options.randomize_model
            # decimal places to use for randomization-based p-value
            rand_p_dec = max(decimal_places, math.ceil(math.log10(nreps+1)))
            cnt_q = 1
            rng = numpy.random.default_rng()
            for rep in range(nreps):
                rand_e_data = rng.permutation(e_data)
                (rand_qm, rand_qe, rand_b1_slope, rand_b0_intercept,
                 _, _, _, _) = calculate_regression_ma_values(rand_e_data, ws_data, x_data, sum_ws, sum_wse, qt)
                if rand_qm >= qm:
                    cnt_q += 1
                if progress_bar is not None:
                    progress_bar.setValue(progress_bar.value() + 1)
            p_random = cnt_q / (nreps + 1)
            p_random_str = format(p_random, inline_float(rand_p_dec))
        else:
            p_random_str = ""

        # output
        output_blocks.append(["<h3>{}</h3>".format(get_text("Regression Results"))])
        output_blocks.append(["<h4>{}</h4>".format(get_text("Predictors"))])

        pr_int = prob_z_score(b0_intercept/math.sqrt(var_b0))
        pr_slope = prob_z_score(b1_slope/math.sqrt(var_b1))
        intercept_output = predictor_test_tuple(get_text("Intercept"), b0_intercept, math.sqrt(var_b0), pr_int)
        slope_output = predictor_test_tuple(get_text("Slope"), b1_slope, math.sqrt(var_b1), pr_slope)

        predictors = [intercept_output, slope_output]
        output_blocks.append(predictor_table(predictors, decimal_places))

        output_blocks.append(["<h4>{}</h4>".format(get_text("Heterogeneity"))])
        model_het = heterogeneity_test_tuple(get_text("Model"), qm, 1, pqm, p_random_str)
        error_het = heterogeneity_test_tuple(get_text("Error"), qe, n - 2, pqe, "")
        model_table = [model_het, error_het, global_het_data]
        output_blocks.append(heterogeneity_table(model_table, decimal_places, total_line=True,
                                                 randomization=options.randomize_model))

        output_blocks.append(["<h3>{}</h3>".format(get_text("Global Results"))])

        new_cites = create_global_output(output_blocks, effect_sizes.label, mean_data, global_het_data, pooled_var,
                                         i2_data, options.bootstrap_mean, decimal_places, alpha,
                                         options.log_transformed)
        citations.extend(new_cites)

        if options.create_graph:
            if options.random_effects:
                ref_list = "{}, {}, and {}".format(get_citation("Hedges_Olkin_1985"),
                                                   get_citation("Greenland_1987"),
                                                   get_citation("Rosenberg_et_2000"))
                model = get_text("random effects")
                fig_citations = ["Hedges_Olkin_1985", "Greenland_1987", "Rosenberg_et_2000"]

            else:
                ref_list = "{} and {}".format(get_citation("Hedges_Olkin_1985"),
                                              get_citation("Greenland_1987"))
                model = get_text("fixed effects")
                fig_citations = ["Hedges_Olkin_1985", "Greenland_1987"]
            chart_data = MetaWinCharts.chart_meta_regression(options.independent_variable.label, effect_sizes.label,
                                                             x_data, e_data, b1_slope, b0_intercept, model, ref_list,
                                                             fig_citations)

    else:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])

    return output_blocks, chart_data, reg_ma_values(global_values, model_het, error_het, predictors), citations


# ---------- complex (glm) meta-analysis ----------
def check_data_for_glm(output_blocks, n, cat_data, cat_labels) -> bool:
    if n < 2:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])
        return False
    ncols = len(cat_labels)
    for col in range(ncols):
        tmp_dat = [row[col] for row in cat_data]
        group_names = sorted(set(tmp_dat))
        if len(group_names) < 2:
            output_blocks.append([get_text("Fewer than two valid groups were identified in column "
                                           "{}").format(cat_labels[col])])
            return False
        tmp_cnt = {group: tmp_dat.count(group) for group in group_names}
        for group in group_names:
            if tmp_cnt[group] < 2:
                output_blocks.append([get_text("Fewer than two valid studies were identified for group {} of column "
                                               "{}.").format(group, cat_labels[col])])
                return False
    return True


def calculate_glm(e: numpy.array, x: numpy.array, w: numpy.array):
    xt = numpy.transpose(x)
    xtwx = numpy.matmul(numpy.matmul(xt, w), x)
    xtwxinv = numpy.linalg.inv(xtwx)  # this is also sigma_b
    beta = numpy.matmul(numpy.matmul(numpy.matmul(xtwxinv, xt), w), e)
    red_beta = beta[1:]
    red_sigma = xtwxinv[1:, 1:]
    qm = numpy.matmul(numpy.matmul(numpy.transpose(red_beta), numpy.linalg.inv(red_sigma)), red_beta)
    error_vec = e - numpy.matmul(x, beta)
    qe = numpy.matmul(numpy.matmul(numpy.transpose(error_vec), w), error_vec)
    return qm, qe, beta, xtwxinv


def complex_meta_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True,
                          sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    continuous_vars = options.continuous_vars
    categorical_vars = options.categorical_vars
    e_data = []
    w_data = []
    v_data = []
    x_data = []
    tmp_x_data = []
    bad_data = []
    boot_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            x_row = [1]  # first column is for the mean
            bad_x = False
            for c in continuous_vars:
                x = data.check_value(r, c.position(), value_type=MetaWinConstants.VALUE_NUMBER)
                if x is None:
                    bad_x = True
                else:
                    x_row.append(x)
            tmp_x_row = []
            for c in categorical_vars:
                x = data.check_value(r, c.position(), value_type=MetaWinConstants.VALUE_STRING)
                if x is None:
                    bad_x = True
                else:
                    tmp_x_row.append(x)

            if (e is not None) and (v is not None) and (v > 0) and (not bad_x):
                e_data.append(e)
                w_data.append(1 / v)
                v_data.append(v)
                x_data.append(x_row)
                tmp_x_data.append(tmp_x_row)
                boot_data.append([e, v])
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)

    if len(continuous_vars) + len(categorical_vars) > 0:
        predictor_labels = ["intercept"]
        has_model = True
    else:
        predictor_labels = ["mean"]
        has_model = False
    for c in continuous_vars:
        predictor_labels.append(c.label)
    # create columns in x for categorical vars
    if len(tmp_x_data) > 0:
        nc = len(tmp_x_data[0])
        for c in range(nc):
            column = [r[c] for r in tmp_x_data]  # extract column c
            groups = sorted(set(column))
            new_dat = []
            if len(groups) > 1:
                for g in groups[1:]:
                    new_col = []
                    for r in column:
                        if g == r:
                            new_col.append(1)
                        elif groups[0] == r:
                            new_col.append(-1)
                        else:
                            new_col.append(0)
                    new_dat.append(new_col)
                if len(groups) == 2:
                    predictor_labels.append(categorical_vars[c].label)
                else:
                    for i in range(len(groups)-1):
                        predictor_labels.append(categorical_vars[c].label + "_{}".format(i+1))
            else:
                pass  # put warning here?
            for r, row in enumerate(x_data):
                for col in new_dat:
                    row.append(col[r])

    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    w_matrix = numpy.diag(w_data)  # convert w to n x n matrix with w on the diagonal
    v_data = numpy.array(v_data)
    x_data = numpy.array(x_data)
    boot_data = numpy.array(boot_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    model_het = None
    error_het = None
    predictor_table_data = None
    global_values = None
    n = len(e_data)
    citations = []
    if check_data_for_glm(output_blocks, n, tmp_x_data, [c.label for c in categorical_vars]):
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])

        try:
            qm, qe, beta, sigma_b = calculate_glm(e_data, x_data, w_matrix)
            pooled_var = pooled_var_glm(qe, n, w_matrix, x_data)
            if options.random_effects:
                output_blocks.append([get_text("Estimate of pooled variance") + ": " +
                                      format(pooled_var, inline_float(decimal_places))])
                ws_data = numpy.reciprocal(v_data + pooled_var)
                w_matrix = numpy.diag(ws_data)
                qm, qe, beta, sigma_b = calculate_glm(e_data, x_data, w_matrix)
            else:
                ws_data = w_data
            median_e = median_effect(e_data, ws_data)

            qt = qm + qe
            df = n-1
            dfm = numpy.shape(x_data)[1] - 1
            dfe = n - dfm - 1
            pqt = 1 - scipy.stats.chi2.cdf(qt, df=df)
            pqe = 1 - scipy.stats.chi2.cdf(qe, df=dfe)
            pqm = 1 - scipy.stats.chi2.cdf(qm, df=dfm)

            if ((options.bootstrap_mean is not None) or (options.randomize_model is not None)) and (sender is not None):
                if options.randomize_model is not None:
                    total_steps = options.randomize_model
                else:
                    total_steps = 0
                if options.bootstrap_mean is not None:
                    total_steps += options.bootstrap_mean
                progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
                                                           get_text("Conducting Bootstrap Analysis"),
                                                           total_steps)
            else:
                progress_bar = None

            # basic global calcs
            mean_e, var_e, _, _, _, _ = mean_effect_var_and_q(e_data, ws_data)
            mean_v = numpy.sum(v_data) / n
            if norm_ci:
                lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1 - alpha, loc=mean_e, scale=math.sqrt(var_e))
            else:
                lower_ci, upper_ci = scipy.stats.t.interval(confidence=1 - alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))
            lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, boot_data,
                                                                                     mean_e, pooled_var,
                                                                                     options.random_effects, alpha,
                                                                                     progress_bar=progress_bar)
            mean_data = mean_data_tuple(get_text("Global"), 0, n, mean_e, median_e, var_e, mean_v, lower_ci, upper_ci,
                                        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)

            i2, i2_lower, i2_upper = calc_i2(qt, n, alpha)
            i2_data = [i2_values(get_text("Total"), i2, i2_lower, i2_upper)]

            # aic = calc_aic(qe, n, dfm + 1)

            global_values = simple_ma_values(mean_data, pooled_var, qt, n-1, pqt, i2)

            # randomization test
            if options.randomize_model:
                if progress_bar is not None:
                    progress_bar.setLabelText(get_text("Conducting Randomization Analysis"))
                nreps = options.randomize_model
                # decimal places to use for randomization-based p-value
                rand_p_dec = max(decimal_places, math.ceil(math.log10(nreps+1)))
                cnt_q = 1
                rng = numpy.random.default_rng()
                for rep in range(nreps):
                    rand_e_data = rng.permutation(e_data)
                    rand_qm, _, _, _ = calculate_glm(rand_e_data, x_data, w_matrix)
                    if rand_qm >= qm:
                        cnt_q += 1
                    if progress_bar is not None:
                        progress_bar.setValue(progress_bar.value() + 1)
                p_random = cnt_q / (nreps + 1)
                p_random_str = format(p_random, inline_float(rand_p_dec))
            else:
                p_random_str = ""

            # output
            output_blocks.append(["<h3>{}</h3>".format(get_text("Model Results"))])
            output_blocks.append(["<h4>{}</h4>".format(get_text("Predictors"))])

            predictor_table_data = []
            for b in range(len(beta)):
                se = math.sqrt(sigma_b[b, b])
                p = prob_z_score(beta[b]/se)
                predictor_table_data.append(predictor_test_tuple("β{} ({})".format(b, predictor_labels[b]), beta[b], se, p))
            output_blocks.append(predictor_table(predictor_table_data, decimal_places))

            global_het_data = heterogeneity_test_tuple(get_text("Total"), qt, df, pqt, "")
            if has_model:
                output_blocks.append(["<h4>{}</h4>".format(get_text("Heterogeneity"))])
                model_het = heterogeneity_test_tuple(get_text("Model"), qm, dfm, pqm, p_random_str)
                error_het = heterogeneity_test_tuple(get_text("Error"), qe, dfe, pqe, "")
                model_table = [model_het, error_het, global_het_data]
                output_blocks.append(heterogeneity_table(model_table, decimal_places, total_line=True,
                                                         randomization=options.randomize_model))

            output_blocks.append(["<h3>{}</h3>".format(get_text("Global Results"))])

            new_cites = create_global_output(output_blocks, effect_sizes.label, mean_data, global_het_data, pooled_var,
                                             i2_data, options.bootstrap_mean, decimal_places, alpha,
                                             options.log_transformed)
            citations.extend(new_cites)
        except numpy.linalg.LinAlgError as error_msg:
            if str(error_msg) == "Singular matrix":
                output_blocks.append([get_text("Analysis Error Encountered"), get_text("AE-singular")])
            else:
                output_blocks.append([get_text("Analysis Error Encountered"), get_text("AE-unknown")])

    return output_blocks, reg_ma_values(global_values, model_het, error_het, predictor_table_data), citations


# ---------- nested meta-analysis ----------
def check_data_for_nested(output_blocks, n, top_level, level_names) -> bool:
    if n < 2:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])
        return False
    # check top grouping with no parent
    if len(top_level) < 2:
        output_blocks.append([get_text("Fewer than two valid groups were identified in column "
                                       "{}").format(level_names[0])])
        return False
    n_levels = len(level_names)
    nest_good = True
    for group in top_level:
        check_groups = group.structure_check(n_levels)
        # if check is not None:
        #     if check[2]:
        #         output_blocks.append([get_text("nest_error_1").format(check[0], level_names[check[1]])])
        #     else:
        #         output_blocks.append([get_text("nest_error_2").format(check[0], level_names[check[1]])])
        #     nest_good = False
        # print(check_groups)
        for check in check_groups:
            if check[2]:
                output_blocks.append([get_text("nest_error_1").format(check[0], level_names[check[1]])])
            else:
                output_blocks.append([get_text("nest_error_2").format(check[0], level_names[check[1]])])
            nest_good = False
    return nest_good


class NestedGroup:
    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index
        self.children = []
        self.mean = 0
        self.qw = 0
        self.parent = None
        self.includes_rows = []

    def qm(self, index, parent_mean, w):
        q = 0
        n = 0
        if index == self.index:
            n += 1
            for r in self.includes_rows:
                q += w[r]*(self.mean - parent_mean)**2
        else:
            for child in self.children:
                tq, tn = child.qm(index, self.mean, w)
                q += tq
                n += tn
        return q, n

    def qe(self, index):
        if self.index == index:
            return self.qw, 1
        else:
            sq, sn = 0, 0
            for child in self.children:
                cq, cn = child.qe(index)
                sq += cq
                sn += cn
            return sq, sn

    def nested_count(self):
        """
        count the total number of nested groups, including this one
        """
        count = 1
        for c in self.children:
            count += c.nested_count()
        return count

    def group_calculations(self, e, w, chart_order: int, boot_data, bootstrap_mean, alpha: float = 0.05,
                           norm_ci: bool = True, progress_bar=None):
        chart_order += 1
        mean_output = []
        het_output = []
        group_mask = [r in self.includes_rows for r in range(len(e))]
        group_e = e[group_mask]
        group_w = w[group_mask]
        group_boot = boot_data[group_mask]
        group_n = len(group_e)
        group_df = group_n - 1
        self.mean, group_var, self.qw, group_sum_w, _, group_sum_ew = mean_effect_var_and_q(group_e, group_w)
        group_median = median_effect(group_e, group_w)
        group_p = 1 - scipy.stats.chi2.cdf(self.qw, df=group_df)

        if norm_ci:
            group_lower, group_upper = scipy.stats.norm.interval(confidence=1 - alpha, loc=self.mean,
                                                                 scale=math.sqrt(group_var))
        else:
            group_lower, group_upper = scipy.stats.t.interval(confidence=1 - alpha, df=group_df, loc=self.mean,
                                                              scale=math.sqrt(group_var))
        (group_lower_bs, group_upper_bs,
         group_lower_bias, group_upper_bias) = bootstrap_means(bootstrap_mean, group_boot, self.mean,
                                                               0, False, alpha, progress_bar=progress_bar)
        if self.index > 0:
            indent = "  " + "→ "*self.index
        else:
            indent = ""
        het_output.append(heterogeneity_test_tuple(indent + self.name + " (within)", self.qw, group_df, group_p, ""))
        mean_output.append(mean_data_tuple(indent + self.name, chart_order, group_n, self.mean, group_median, group_var,
                                           0, group_lower, group_upper, group_lower_bs, group_upper_bs,
                                           group_lower_bias, group_upper_bias))
        for child in self.children:
            child_het, child_mean, chart_order = child.group_calculations(e, w, chart_order, boot_data,
                                                                          bootstrap_mean, alpha,
                                                                          progress_bar=progress_bar)
            het_output.extend(child_het)
            mean_output.extend(child_mean)
        if len(self.children) > 0:
            chart_order += 1
        return het_output, mean_output, chart_order

    def structure_check(self, max_index):
        # if len(self.includes_rows) < 2:
        #     return self.name, self.index, True
        # if self.index < max_index:
        #     # do we need to require each nesting layer contain at least 2 groups?
        #     # if len(self.children) < 2:
        #     #     return self.name, self.index, False
        #     for child in self.children:
        #         check = child.structure_check(max_index)
        #         if check is not None:
        #             return check
        # return None
        if len(self.includes_rows) < 2:
            if self.index == 0:  # this should prevent a crash if a top level group has only 1 study in it
                return [[self.name, self.index, True]]
            else:
                return [self.name, self.index, True]
        if self.index < max_index:
            tmp_list = []
            for child in self.children:
                check = child.structure_check(max_index)
                if len(check) > 0:
                    tmp_list.append(check)
            return tmp_list
        return []


def find_next_nested_level(index, group_data, parent) -> list:
    group_list = []
    if parent is None:
        level_names = sorted(set(row[index] for row in group_data))
    else:
        level_names = sorted(set(row[index] for row in group_data if row[index-1] == parent.name))
    for name in level_names:
        new_group = NestedGroup(name, index)
        if parent is None:
            new_group.includes_rows = [r for r, row in enumerate(group_data) if row[index] == name]
        else:
            new_group.parent = parent
            new_group.includes_rows = [r for r, row in enumerate(group_data) if (row[index-1] == parent.name) and
                                       (row[index] == name) and r in parent.includes_rows]
        group_list.append(new_group)
        if index < len(group_data[0]) - 1:
            new_group.children = find_next_nested_level(index+1, group_data, new_group)
    return group_list


def nested_meta_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True,
                         sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    group_levels = options.nested_vars
    e_data = []
    w_data = []
    v_data = []
    group_data = []
    bad_data = []
    boot_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            g_dat = []
            for level in group_levels:
                g = data.check_value(r, level.position(), value_type=MetaWinConstants.VALUE_STRING)
                if g is not None:
                    g_dat.append(g)
            if len(g_dat) < len(group_levels):
                g_dat = None
            if (e is not None) and (v is not None) and (v > 0) and (g_dat is not None):
                e_data.append(e)
                w_data.append(1 / v)
                v_data.append(v)
                group_data.append(g_dat)
                boot_data.append([e, v])
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)

    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)
    boot_data = numpy.array(boot_data)

    top_level = find_next_nested_level(0, group_data, None)
    output_blocks = output_filtered_bad(filtered, bad_data)

    n = len(e_data)

    chart_data = None
    group_het_values = None
    group_mean_values = None
    model_het_values = None
    error_het_values = None
    global_values = None
    citations = []
    if check_data_for_nested(output_blocks, n, top_level, [level.label for level in group_levels]):
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])

        total_groups = 0
        for group in top_level:
            total_groups += group.nested_count()

        if ((options.bootstrap_mean is not None) or (options.randomize_model is not None)) and (sender is not None):
            if options.randomize_model is not None:
                total_steps = options.randomize_model
            else:
                total_steps = 0
            if options.bootstrap_mean is not None:
                total_steps += options.bootstrap_mean * (total_groups + 1)
            progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
                                                       get_text("Conducting Bootstrap Analysis"),
                                                       total_steps)
        else:
            progress_bar = None

        mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(e_data, w_data)
        median_e = median_effect(e_data, w_data)
        mean_v = numpy.sum(v_data) / n
        if norm_ci:
            lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1 - alpha, loc=mean_e, scale=math.sqrt(var_e))
        else:
            lower_ci, upper_ci = scipy.stats.t.interval(confidence=1 - alpha, df=n-1, loc=mean_e, scale=math.sqrt(var_e))
        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, boot_data,
                                                                                 mean_e, 0, False, alpha,
                                                                                 progress_bar=progress_bar)
        global_mean_data = mean_data_tuple(get_text("Global"), 0, n, mean_e, median_e, var_e, mean_v, lower_ci,
                                           upper_ci, lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)
        df = n-1
        pqt = 1 - scipy.stats.chi2.cdf(qt, df=df)
        global_het_data = heterogeneity_test_tuple(get_text("Total"), qt, df, pqt, "")

        i2, i2_lower, i2_upper = calc_i2(qt, n, alpha)
        i2_data = [i2_values(get_text("Total"), i2, i2_lower, i2_upper)]

        global_values = simple_ma_values(global_mean_data, 0, qt, df, pqt, i2)

        chart_order = 1
        group_het_values = []
        group_mean_values = []
        for group in top_level:
            het_out, mean_out, chart_order = group.group_calculations(e_data, w_data, chart_order, boot_data,
                                                                      options.bootstrap_mean, alpha,
                                                                      progress_bar=progress_bar)
            group_het_values.extend(het_out)
            group_mean_values.extend(mean_out)

        model_het_values = []
        prev_n = 1
        for i in range(len(group_levels)):
            level_name = group_levels[i].label
            qm = 0
            ng = 0
            for level in top_level:
                tq, tn = level.qm(i, mean_e, w_data)
                qm += tq
                ng += tn
            dfm = ng - prev_n
            prev_n = ng
            pqm = 1 - scipy.stats.chi2.cdf(qm, df=dfm)
            model_het_values.append(heterogeneity_test_tuple("Qm ({})".format(level_name), qm, dfm, pqm, ""))

        # extract Qerror from the lowest level of the nested hierarchy
        qe = 0
        ng = 0
        for group in top_level:
            cq, cn = group.qe(len(group_levels)-1)
            qe += cq
            ng += cn
        dfe = n - ng
        pqe = 1 - scipy.stats.chi2.cdf(qe, df=dfe)
        error_het_values = heterogeneity_test_tuple("Qe", qe, dfe, pqe, "")

        # aic = calc_aic(qe, n, ng)

        forest_data = [global_mean_data]
        forest_data.extend(group_mean_values)

        # randomization test
        if options.randomize_model:
            if progress_bar is not None:
                progress_bar.setLabelText(get_text("Conducting Randomization Analysis"))
            nreps = options.randomize_model
            # decimal places to use for randomization-based p-value
            rand_p_dec = max(decimal_places, math.ceil(math.log10(nreps+1)))
            cnt_list = [1 for _ in range(len(group_levels))]
            rng = numpy.random.default_rng()
            for rep in range(nreps):
                rand_e_data = rng.permutation(e_data)
                rand_level = find_next_nested_level(0, group_data, None)
                for group in rand_level:
                    group.group_calculations(rand_e_data, w_data, 0, boot_data, None, alpha)

                for i in range(len(group_levels)):
                    tmp_qm = 0
                    for level in rand_level:
                        tq, _ = level.qm(i, mean_e, w_data)
                        tmp_qm += tq
                    if tmp_qm >= model_het_values[i].q:
                        cnt_list[i] += 1
                if progress_bar is not None:
                    progress_bar.setValue(progress_bar.value() + 1)
            for i in range(len(group_levels)):
                p_random = cnt_list[i] / (nreps + 1)
                p_random_str = format(p_random, inline_float(rand_p_dec))
                # replace current het value tuple with new one, replacing last value
                chv = model_het_values[i]
                model_het_values[i] = heterogeneity_test_tuple(chv.source, chv.q, chv.df, chv.p_chi, p_random_str)

        # output
        output_blocks.append(["<h3>{}</h3>".format(get_text("Group Results"))])
        output_blocks.append(["<h4>{}</h4>".format(get_text("Heterogeneity"))])
        output_blocks.append(heterogeneity_table(group_het_values, decimal_places))

        model_table = []
        model_table.extend(model_het_values)
        model_table.append(error_het_values)
        model_table.append(global_het_data)
        output_blocks.append(heterogeneity_table(model_table, decimal_places, total_line=True,
                                                 randomization=options.randomize_model))

        output_blocks.append(["<h4>{}</h4>".format(get_text("Mean Effect Sizes"))])
        output_blocks.append(mean_effects_table(effect_sizes.label, group_mean_values, options.bootstrap_mean,
                             decimal_places, alpha, options.log_transformed))

        output_blocks.append(["<h3>{}</h3>".format(get_text("Global Results"))])

        new_cites = create_global_output(output_blocks, effect_sizes.label, global_mean_data, global_het_data, 0,
                                         i2_data, options.bootstrap_mean, decimal_places, alpha,
                                         options.log_transformed)
        citations.extend(new_cites)

        if options.create_graph:
            chart_data = MetaWinCharts.chart_forest_plot("nested analysis", effect_sizes.label, forest_data, alpha,
                                                         options.bootstrap_mean, normal_ci=norm_ci)

    return (output_blocks, chart_data, group_ma_values(global_values, group_mean_values, group_het_values,
                                                       model_het_values, error_het_values), citations)


# # ---------- trim-and-fill analysis ----------
# def trim_and_fill_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True):
#     # filter and prepare data for analysis
#     effect_sizes = options.effect_data
#     variances = options.effect_vars
#     e_data = []
#     w_data = []
#     v_data = []
#     bad_data = []
#     study_names = []
#     filtered = []
#     for r, row in enumerate(data.rows):
#         if row.not_filtered():
#             e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
#             v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
#             if (e is not None) and (v is not None) and (v > 0):
#                 e_data.append(e)
#                 w_data.append(1/v)
#                 v_data.append(v)
#                 study_names.append(row.label)
#             else:
#                 bad_data.append(row.label)
#         else:
#             filtered.append(row.label)
#     e_data = numpy.array(e_data)
#     w_data = numpy.array(w_data)
#     v_data = numpy.array(v_data)
#
#     output_blocks = output_filtered_bad(filtered, bad_data)
#
#     chart_data = None
#     n = len(e_data)
#     citations = []
#
#     if n > 1:
#         output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
#         df = n - 1
#         mean_e, var_e, qt, sum_w, sum_w2, _ = mean_effect_var_and_q(e_data, w_data)
#         median_e = median_effect(e_data, w_data)
#         mean_v = numpy.sum(v_data) / n
#         pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
#
#         if options.random_effects:
#             ws_data = numpy.reciprocal(v_data + pooled_var)
#             mean_e, var_e, qt, *_ = mean_effect_var_and_q(e_data, ws_data)
#             median_e = median_effect(e_data, ws_data)
#             output_blocks.append([get_text("Estimate of pooled variance") + ": " +
#                                   format(pooled_var, inline_float(decimal_places))])
#
#         if norm_ci:
#             lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1-alpha, loc=mean_e, scale=math.sqrt(var_e))
#         else:
#             lower_ci, upper_ci = scipy.stats.t.interval(confidence=1-alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))
#         original_mean_data = mean_data_tuple(get_text("Original Mean"), 0, n, mean_e, median_e, var_e, mean_v,
#                                              lower_ci, upper_ci, 0, 0, 0, 0)
#         original_mean = mean_e
#
#         trim_n = -1
#         new_trim = 0
#         iterations = 0
#         tmp_mean_e = mean_e
#         skew_right = True
#         while (trim_n != new_trim) and (iterations < 1000):
#             iterations += 1
#             trim_n = new_trim
#             tmp_data = numpy.zeros(shape=(n, 3))
#             tmp_data[:, 0] = e_data
#             tmp_data[:, 1] = w_data
#             tmp_data[:, 2] = v_data
#             if skew_right:
#                 tmp_data = tmp_data[tmp_data[:, 0].argsort()[::-1]]  # sort into descending order by first column
#             else:
#                 tmp_data = tmp_data[tmp_data[:, 0].argsort()]  # sort into ascending order by first column
#
#             # trim the first trim_n rows
#             trim_data = tmp_data[trim_n:, :]
#             # calculate the mean for just the trimmed data
#             (tmp_mean_e, tmp_var_e, tmp_qt, tmp_sum_w, tmp_sum_w2,
#              tmp_sum_ew) = mean_effect_var_and_q(trim_data[:, 0], trim_data[:, 1])
#             tmp_df = n - trim_n - 1
#             if options.random_effects:
#                 tmp_pooled_var = pooled_var_no_structure(tmp_qt, tmp_sum_w, tmp_sum_w2, tmp_df)
#                 tmp_ws = numpy.reciprocal(trim_data[:, 2] + tmp_pooled_var)
#                 tmp_mean_e, *_ = mean_effect_var_and_q(trim_data[:, 0], tmp_ws)
#
#             # using this new mean, calculate the thresholds for all of the data
#             diff = tmp_data[:, 0] - tmp_mean_e
#             abs_diff = numpy.abs(diff)
#             ranks = abs_diff.argsort().argsort()
#             ranks = (ranks+1)*numpy.sign(diff)
#             pos = [r > 0 for r in ranks]
#             neg = [r < 0 for r in ranks]
#             t_pos = numpy.sum(ranks[pos])
#             t_neg = numpy.sum(numpy.abs(ranks[neg]))
#             if t_pos > t_neg:  # right skew
#                 gamma = n - abs(numpy.min(ranks))
#                 t_n = t_pos
#             else:  # left skew
#                 gamma = n - abs(numpy.max(ranks))
#                 t_n = t_neg
#                 skew_right = False
#             if options.k_estimator == "R":  # R0
#                 new_trim = max(0, round(gamma - 1))
#             elif options.k_estimator == "Q":  # Q0
#                 new_trim = max(0, round(n - 1 / 2 - math.sqrt(2 * n ** 2 - 4 * t_n + 1 / 4)))
#             else:  # L0
#                 new_trim = max(0, round((4*t_n - n*(n+1))/(2*n - 1)))
#
#         # create the new data set with the estimated missing values
#         sort_data = numpy.zeros(shape=(n, 3))
#         sort_data[:, 0] = e_data
#         sort_data[:, 1] = w_data
#         sort_data[:, 2] = v_data
#         if skew_right:
#             sort_data = sort_data[sort_data[:, 0].argsort()[::-1]]  # sort into descending order by first column
#         else:
#             sort_data = sort_data[sort_data[:, 0].argsort()]  # sort into ascending order by first column
#         tmp_data = numpy.zeros(shape=(n+trim_n, 3))
#         tmp_data[:n, 0] = sort_data[:, 0]
#         tmp_data[:n, 1] = sort_data[:, 1]
#         tmp_data[:n, 2] = sort_data[:, 2]
#         for i in range(trim_n):
#             d = tmp_data[i, 0] - tmp_mean_e
#             tmp_data[n+i, 0] = tmp_mean_e - d
#             tmp_data[n+i, 1] = tmp_data[i, 1]
#             tmp_data[n+i, 2] = tmp_data[i, 2]
#
#         # calculate the new mean, etc.
#         mean_e, var_e, qt, sum_w, sum_w2, _ = mean_effect_var_and_q(tmp_data[:, 0], tmp_data[:, 1])
#         median_e = median_effect(tmp_data[:, 0], tmp_data[:, 1])
#         df = n + trim_n - 1
#         if options.random_effects:
#             pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
#             ws = numpy.reciprocal(tmp_data[:, 2] + pooled_var)
#             mean_e, var_e, *_ = mean_effect_var_and_q(tmp_data[:, 0], ws)
#
#         if norm_ci:
#             lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1-alpha, loc=mean_e, scale=math.sqrt(var_e))
#         else:
#             lower_ci, upper_ci = scipy.stats.t.interval(confidence=1-alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))
#         trim_mean_data = mean_data_tuple(get_text("Trim and Fill Mean"), 0, n+trim_n, mean_e, median_e, var_e, mean_v,
#                                          lower_ci, upper_ci, 0, 0, 0, 0)
#
#         # output
#         output_blocks.append([get_text("Trim and Fill Analysis estimated {} missing studies.").format(trim_n)])
#         mean_data = [original_mean_data, trim_mean_data]
#         output_blocks.append(["<h4>{}</h4>".format(get_text("Mean Effect Sizes"))])
#         output_blocks.append(mean_effects_table(effect_sizes.label, mean_data, options.bootstrap_mean,
#                              decimal_places, alpha, options.log_transformed))
#
#         if options.create_graph:
#             chart_data = MetaWinCharts.chart_trim_fill_plot(effect_sizes.label, tmp_data, n,  original_mean, mean_e)
#
#     else:
#         output_blocks.append([get_text("Fewer than two studies were valid for analysis")])
#
#     return output_blocks, chart_data, None, citations


# ---------- phylogenetic meta-analysis ----------
def phylogenetic_correlation(tip_names, root):
    n = len(tip_names)
    p = numpy.zeros(shape=(n, n))
    # find depth of most recent common ancestor of included taxa
    mrca = root.find_tip_by_name(tip_names[0])
    for name1 in tip_names[1:]:
        tip1 = root.find_tip_by_name(name1)
        mrca = tip1.common_ancestor(mrca)
    max_depth = mrca.max_node_tip_length()
    for i, name1 in enumerate(tip_names):
        tip1 = root.find_tip_by_name(name1)
        for j in range(i+1):  # take advantage of symmetry
            name2 = tip_names[j]
            tip2 = root.find_tip_by_name(name2)
            if i == j:
                p[i, j] = 1
            else:
                common_ancestor = tip1.common_ancestor(tip2)
                shared_dist = common_ancestor.distance_to_ancestor(mrca)
                p[i, j] = shared_dist/max_depth
                p[j, i] = p[i, j]
    return p


def phylogenetic_meta_analysis(data, options, tree, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True,
                               sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    continuous_vars = options.continuous_vars
    categorical_vars = options.categorical_vars
    data_tips = options.tip_names
    tree_tips = tree.tip_names()
    e_data = []
    w_data = []
    v_data = []
    x_data = []
    tip_names = []
    tmp_x_data = []
    bad_data = []
    boot_data = []
    filtered = []
    missing_from_tree = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            x_row = [1]  # first column is for the mean
            bad_x = False
            for c in continuous_vars:
                x = data.check_value(r, c.position(), value_type=MetaWinConstants.VALUE_NUMBER)
                if x is None:
                    bad_x = True
                else:
                    x_row.append(x)
            tmp_x_row = []
            for c in categorical_vars:
                x = data.check_value(r, c.position(), value_type=MetaWinConstants.VALUE_STRING)
                if x is None:
                    bad_x = True
                else:
                    tmp_x_row.append(x)
            t_name = data.check_value(r, data_tips.position(), value_type=MetaWinConstants.VALUE_STRING)
            if t_name not in tree_tips:
                bad_x = True
                missing_from_tree.append(row.label)
            if (e is not None) and (v is not None) and (v > 0) and (not bad_x):
                e_data.append(e)
                w_data.append(1 / v)
                v_data.append(v)
                x_data.append(x_row)
                tmp_x_data.append(tmp_x_row)
                boot_data.append([e, v])
                tip_names.append(t_name)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)

    if len(continuous_vars) + len(categorical_vars) > 0:
        predictor_labels = ["intercept"]
        has_model = True
    else:
        predictor_labels = ["mean"]
        has_model = False
    for c in continuous_vars:
        predictor_labels.append(c.label)
    # create columns in x for categorical vars
    if len(tmp_x_data) > 0:
        nc = len(tmp_x_data[0])
        for c in range(nc):
            column = [r[c] for r in tmp_x_data]  # extract column c
            groups = sorted(set(column))
            new_dat = []
            if len(groups) > 1:
                for g in groups[1:]:
                    new_col = []
                    for r in column:
                        if g == r:
                            new_col.append(1)
                        elif groups[0] == r:
                            new_col.append(-1)
                        else:
                            new_col.append(0)
                    new_dat.append(new_col)
                if len(groups) == 2:
                    predictor_labels.append(categorical_vars[c].label)
                else:
                    for i in range(len(groups)-1):
                        predictor_labels.append(categorical_vars[c].label + "_{}".format(i+1))
            else:
                pass  # put warning here?
            for r, row in enumerate(x_data):
                for col in new_dat:
                    row.append(col[r])

    e_data = numpy.array(e_data)
    # w_data = numpy.array(w_data)
    n = len(e_data)
    v_data = numpy.array(v_data)
    x_data = numpy.array(x_data)
    # boot_data = numpy.array(boot_data)

    p_matrix = phylogenetic_correlation(tip_names, tree)

    v_matrix = numpy.diag(v_data)  # convert w to n x n matrix with w on the diagonal
    # add phylogenetic covariances to v_matrix
    for i in range(n):
        for j in range(i):
            v_matrix[i, j] = p_matrix[i, j]*math.sqrt(v_data[i])*math.sqrt(v_data[j])
            v_matrix[j, i] = v_matrix[i, j]
    w_matrix = numpy.linalg.inv(v_matrix)

    if len(missing_from_tree) > 0:
        print(missing_from_tree)
    output_blocks = output_filtered_bad(filtered, bad_data)


    output_blocks.append(["<h2>Warning: The phylogenetic glm meta-analysis is still experimental and has some kinks "
                          "that have not definitively been worked out yet.<p>Not all of the intended output from this "
                          "analysis is included at this time and the randomization tests have not been "
                          "activated.</h2>"])



    # model_het = None
    # error_het = None
    # predictor_table_data = None
    # global_values = None
    citations = []
    if check_data_for_glm(output_blocks, n, tmp_x_data, [c.label for c in categorical_vars]):
        try:
            output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
            qm, qe, beta, sigma_b = calculate_glm(e_data, x_data, w_matrix)
            pooled_var = pooled_var_glm(qe, n, w_matrix, x_data)
            if options.random_effects:
                output_blocks.append([get_text("Estimate of pooled variance") + ": " +
                                      format(pooled_var, inline_float(decimal_places))])
                vs_data = v_data + pooled_var
                # ws_data = numpy.reciprocal(v_data + pooled_var)
                v_matrix = numpy.diag(vs_data)  # convert w to n x n matrix with w on the diagonal
                # add phylogenetic covariances to v_matrix
                for i in range(n):
                    for j in range(i):
                        v_matrix[i, j] = p_matrix[i, j] * math.sqrt(vs_data[i]) * math.sqrt(vs_data[j])
                        v_matrix[j, i] = v_matrix[i, j]
                w_matrix = numpy.linalg.inv(v_matrix)

                qm, qe, beta, sigma_b = calculate_glm(e_data, x_data, w_matrix)
            # else:
            #     ws_data = w_data
            # median_e = median_effect(e_data, ws_data)

            qt = qm + qe
            df = n-1
            dfm = numpy.shape(x_data)[1] - 1
            dfe = n - dfm - 1
            pqt = 1 - scipy.stats.chi2.cdf(qt, df=df)
            pqe = 1 - scipy.stats.chi2.cdf(qe, df=dfe)
            pqm = 1 - scipy.stats.chi2.cdf(qm, df=dfm)

            # aic = calc_aic(qe, n, dfm + 2)
            # print("AIC:", round(aic, 4))


            """
            everything to here has been cross-checked fairly well
            """

            # basic global calcs
            """ need to pull the values from already calculated model """

            # mean_e, var_e, _, _, _, _ = mean_effect_var_and_q(e_data, ws_data)
            # mean_v = numpy.sum(v_data) / n
            # lower_ci, upper_ci = scipy.stats.t.interval(confidence=1 - alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))
            # lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, boot_data,
            #                                                                          mean_e, pooled_var,
            #                                                                          options.random_effects, alpha)
            # mean_data = mean_data_tuple("Global", 0, n, mean_e, var_e, mean_v, lower_ci, upper_ci, lower_bs_ci,
            #                             upper_bs_ci, lower_bias_ci, upper_bias_ci)

            # i2, i2_lower, i2_upper = calc_i2(qt, n, alpha)
            # i2_data = [i2_values(get_text("Total"), i2, i2_lower, i2_upper)]

            # randomization test
            p_random_str = ""  # temp
            # if options.randomize_model and has_model:
            #     nreps = options.randomize_model
            #     # decimal places to use for randomization-based p-value
            #     rand_p_dec = max(decimal_places, math.ceil(math.log10(nreps+1)))
            #     cnt_q = 1
            #     rng = numpy.random.default_rng()
            #     for rep in range(nreps):
            #         rand_x_data = rng.permutation(x_data)
            #         rand_qm, _, _, _ = calculate_glm(e_data, rand_x_data, w_matrix)
            #         if rand_qm >= qm:
            #             cnt_q += 1
            #     p_random = cnt_q / (nreps + 1)
            #     p_random_str = format(p_random, inline_float(rand_p_dec))
            # else:
            #     p_random_str = ""

            # output
            output_blocks.append(["<h3>{}</h3>".format(get_text("Model Results"))])
            output_blocks.append(["<h4>{}</h4>".format(get_text("Predictors"))])

            predictor_table_data = []
            for b in range(len(beta)):
                se = math.sqrt(sigma_b[b, b])
                p = prob_z_score(beta[b]/se)
                predictor_table_data.append(predictor_test_tuple("β{} ({})".format(b, predictor_labels[b]), beta[b], se, p))
            output_blocks.append(predictor_table(predictor_table_data, decimal_places))

            global_het_data = heterogeneity_test_tuple(get_text("Total"), qt, df, pqt, "")
            if has_model:
                output_blocks.append(["<h4>{}</h4>".format(get_text("Heterogeneity"))])
                model_het = heterogeneity_test_tuple(get_text("Model"), qm, dfm, pqm, p_random_str)
                error_het = heterogeneity_test_tuple(get_text("Error"), qe, dfe, pqe, "")
                model_table = [model_het, error_het, global_het_data]
                output_blocks.append(heterogeneity_table(model_table, decimal_places, total_line=True,
                                                         randomization=options.randomize_model))
            else:
                """ need to pull the values from already calculated model """
                mean_e = beta[0]
                var_e = sigma_b[0, 0]
                mean_v = numpy.sum(v_data) / n
                lower_ci, upper_ci = scipy.stats.t.interval(confidence=1 - alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))
                mean_data = mean_data_tuple(get_text("Global"), 0, n, mean_e, None, var_e, mean_v, lower_ci, upper_ci,
                                            0, 0, 0, 0)

                i2, i2_lower, i2_upper = calc_i2(qt, n, alpha)
                i2_data = [i2_values(get_text("Total"), i2, i2_lower, i2_upper)]

                output_blocks.append(["<h3>{}</h3>".format(get_text("Global Results"))])
                new_cites = create_global_output(output_blocks, effect_sizes.label, mean_data, global_het_data, pooled_var,
                                                 i2_data, options.bootstrap_mean, decimal_places, alpha,
                                                 options.log_transformed, inc_median=False)
                citations.extend(new_cites)
        except numpy.linalg.LinAlgError as error_msg:
            if str(error_msg) == "Singular matrix":
                output_blocks.append([get_text("Analysis Error Encountered"), get_text("AE-singular")])
            else:
                output_blocks.append([get_text("Analysis Error Encountered"), get_text("AE-unknown")])

    return output_blocks, citations


# ---------- jackknife meta-analysis ----------
def jackknife_meta_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True,
                            sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    e_data = []
    w_data = []
    v_data = []
    bad_data = []
    boot_data = []
    study_names = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if (e is not None) and (v is not None) and (v > 0):
                e_data.append(e)
                w_data.append(1/v)
                v_data.append(v)
                boot_data.append([e, v])
                study_names.append(row.label)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)
    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)
    boot_data = numpy.array(boot_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    chart_data = None
    n = len(e_data)
    citations = []
    if n > 1:
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])

        if (options.bootstrap_mean is not None) and (sender is not None):
            total_steps = options.bootstrap_mean*(n + 1)
            progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
                                                       get_text("Conducting Bootstrap Analysis"),
                                                       total_steps)
        else:
            progress_bar = None

        # global value
        df = n - 1
        mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(e_data, w_data)
        median_e = median_effect(e_data, w_data)
        mean_v = numpy.sum(v_data) / n
        pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
        if options.random_effects:
            ws_data = numpy.reciprocal(v_data + pooled_var)
            mean_e, var_e, qt, *_ = mean_effect_var_and_q(e_data, ws_data)
            median_e = median_effect(e_data, ws_data)
            output_blocks.append([get_text("Estimate of pooled variance") + ": " +
                                  format(pooled_var, inline_float(decimal_places))])

        p = 1 - scipy.stats.chi2.cdf(qt, df=df)
        if norm_ci:
            lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1-alpha, loc=mean_e, scale=math.sqrt(var_e))
        else:
            lower_ci, upper_ci = scipy.stats.t.interval(confidence=1-alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))

        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, boot_data,
                                                                                 mean_e, pooled_var,
                                                                                 options.random_effects, alpha,
                                                                                 progress_bar=progress_bar)
        plot_order = 0
        mean_data = mean_data_tuple(get_text("Mean"), plot_order, n, mean_e, median_e, var_e, mean_v, lower_ci,
                                    upper_ci, lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)
        global_het_data = heterogeneity_test_tuple(get_text("Total"), qt, df, p, None)
        i2, i2_lower, i2_upper = calc_i2(qt, n, alpha)
        i2_data = [i2_values(get_text("Total"), i2, i2_lower, i2_upper)]

        # aic = calc_aic(qt, n, 1)

        plot_order += 2
        forest_data = [mean_data]
        global_mean_data = mean_data_tuple("", plot_order, n, mean_e, median_e, var_e, mean_v, lower_ci, upper_ci,
                                           lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)

        # do jackknife
        jackknife_means = []
        jackknife_het = []
        for j in range(n):
            j_label = "w/o " + study_names[j]
            s_filter = [True for _ in range(n)]
            s_filter[j] = False
            tmp_e = e_data[s_filter]
            tmp_w = w_data[s_filter]
            tmp_v = v_data[s_filter]
            tmp_boot = boot_data[s_filter]
            df = n - 2
            mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(tmp_e, tmp_w)
            median_e = median_effect(tmp_e, tmp_w)
            mean_v = numpy.sum(tmp_v) / (n-1)
            pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
            if options.random_effects:
                ws_data = numpy.reciprocal(tmp_v + pooled_var)
                mean_e, var_e, qt, *_ = mean_effect_var_and_q(tmp_e, ws_data)
                median_e = median_effect(tmp_e, ws_data)
            p = 1 - scipy.stats.chi2.cdf(qt, df=df)
            if norm_ci:
                lower_ci, upper_ci = scipy.stats.norm.interval(confidence=1-alpha, loc=mean_e, scale=math.sqrt(var_e))
            else:
                lower_ci, upper_ci = scipy.stats.t.interval(confidence=1-alpha, df=df, loc=mean_e,
                                                            scale=math.sqrt(var_e))
            lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci = bootstrap_means(options.bootstrap_mean, tmp_boot,
                                                                                     mean_e, pooled_var,
                                                                                     options.random_effects, alpha,
                                                                                     progress_bar=progress_bar)
            mean_data = mean_data_tuple(j_label, plot_order, n-1, mean_e, median_e, var_e, mean_v, lower_ci, upper_ci,
                                        lower_bs_ci, upper_bs_ci, lower_bias_ci, upper_bias_ci)
            jackknife_means.append(mean_data)
            het_data = heterogeneity_test_tuple("{} Qtotal".format(j_label), qt, df, p, None)
            jackknife_het.append(het_data)
            forest_data.append(mean_data)
            plot_order += 1

        # output
        output_blocks.append(["<h3>{}</h3>".format(get_text("Jackknife Results"))])
        output_blocks.append(["<h4>{}</h4>".format(get_text("Heterogeneity"))])
        output_blocks.append(heterogeneity_table(jackknife_het, decimal_places))

        output_blocks.append(["<h4>{}</h4>".format(get_text("Mean Effect Sizes"))])
        output_blocks.append(mean_effects_table(effect_sizes.label, jackknife_means, options.bootstrap_mean,
                             decimal_places, alpha, options.log_transformed))

        output_blocks.append(["<h3>{}</h3>".format(get_text("Global Results"))])
        new_cites = create_global_output(output_blocks, effect_sizes.label, global_mean_data, global_het_data,
                                         pooled_var, i2_data, options.bootstrap_mean, decimal_places, alpha,
                                         options.log_transformed)
        citations.extend(new_cites)

        if options.create_graph:
            chart_data = MetaWinCharts.chart_forest_plot("jackknife analysis", effect_sizes.label, forest_data, alpha,
                                                         options.bootstrap_mean, normal_ci=norm_ci)
    else:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])

    return output_blocks, chart_data, citations


# # ---------- rank correlation analysis ----------
# def get_ranks(x):
#     return scipy.stats.rankdata(x, "average")
#
#
# def correlation(x, y):
#     n = len(x)
#     x_mean = numpy.sum(x)/n
#     y_mean = numpy.sum(y)/n
#     sum_xy = numpy.sum((x - x_mean)*(y - y_mean))
#     sum_x2 = numpy.sum(numpy.square(x - x_mean))
#     sum_y2 = numpy.sum(numpy.square(y - y_mean))
#     return sum_xy / math.sqrt(sum_x2 * sum_y2)
#
#
# def kendalls_tau(e_ranks, x_ranks):
#     n = len(e_ranks)
#     sort_data = numpy.zeros(shape=(n, 2))
#     # if there are no ties in e_ranks, sort by it, otherwise, sort by x_ranks
#     if len(numpy.unique(e_ranks)) < n:
#         sort_data[:, 0] = x_ranks
#         sort_data[:, 1] = e_ranks
#     else:
#         sort_data[:, 0] = e_ranks
#         sort_data[:, 1] = x_ranks
#     sort_data = sort_data[sort_data[:, 0].argsort()]  # sort into ascending order by first column
#     c = 0
#     for i in range(n):
#         for j in range(i + 1, n):
#             if sort_data[j, 1] > sort_data[i, 1]:
#                 c += 1
#             elif sort_data[j, 1] == sort_data[i, 1]:
#                 c += 0.5
#     sum_n = 4 * c - n * (n - 1)
#     # correction terms for ties
#     unique, cnts = numpy.unique(e_ranks, return_counts=True)
#     t1 = 0
#     for c in cnts:
#         if c > 1:
#             t1 += c * (c - 1)
#     unique, cnts = numpy.unique(x_ranks, return_counts=True)
#     t2 = 0
#     for c in cnts:
#         if c > 1:
#             t2 += c * (c - 1)
#
#     tau = sum_n / math.sqrt((n * (n - 1) - t1) * (n * (n - 1) - t2))
#     return tau
#
#
# def rank_correlation_analysis(data, options, decimal_places: int = 4, sender=None):
#     # filter and prepare data for analysis
#     effect_sizes = options.effect_data
#     variances = options.effect_vars
#     if options.sample_size is not None:
#         sample_sizes = options.sample_size
#         do_n = True
#     else:
#         sample_sizes = None
#         do_n = False
#     e_data = []
#     w_data = []
#     v_data = []
#     n_data = []
#     bad_data = []
#     study_names = []
#     filtered = []
#     for r, row in enumerate(data.rows):
#         if row.not_filtered():
#             e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
#             v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
#             if do_n:
#                 ns = data.check_value(r, sample_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
#             else:
#                 ns = 1
#             if (e is not None) and (v is not None) and (v > 0) and (ns is not None) and (ns > 0):
#                 e_data.append(e)
#                 w_data.append(1/v)
#                 v_data.append(v)
#                 if do_n:
#                     n_data.append(ns)
#                 study_names.append(row.label)
#             else:
#                 bad_data.append(row.label)
#         else:
#             filtered.append(row.label)
#     e_data = numpy.array(e_data)
#     w_data = numpy.array(w_data)
#     v_data = numpy.array(v_data)
#     if do_n:
#         n_data = numpy.array(n_data)
#
#     output_blocks = output_filtered_bad(filtered, bad_data)
#
#     n = len(e_data)
#     citations = []
#     if n > 1:
#         output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
#
#         # global value
#         df = n - 1
#         mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(e_data, w_data)
#         pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
#         if options.random_effects:
#             ws_data = numpy.reciprocal(v_data + pooled_var)
#             mean_e, var_e, *_ = mean_effect_var_and_q(e_data, ws_data)
#
#         # standardize e and v
#         v_star = [v - 1/sum_w for v in v_data]
#         e_star = [(e_data[i] - mean_e)/math.sqrt(v_star[i]) for i in range(n)]
#         v_star = numpy.array(v_star)
#         e_star = numpy.array(e_star)
#
#         if do_n:
#             x_star = n_data
#         else:
#             x_star = v_star
#
#         # calculate rank correlation
#         e_ranks = get_ranks(e_star)
#         x_ranks = get_ranks(x_star)
#         if options.cor_test == "tau":  # Kendall's tau
#             r = kendalls_tau(e_ranks, x_ranks)
#         else:  # Spearman's rho
#             r = correlation(e_ranks, x_ranks)
#
#         # test with randomization
#         nreps = options.randomize_model
#
#         if sender is not None:
#             progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
#                                                        get_text("Conducting Randomization Analysis"), nreps)
#         else:
#             progress_bar = None
#
#         # decimal places to use for randomization-based p-value
#         rand_p_dec = max(decimal_places, math.ceil(math.log10(nreps+1)))
#         cnt_r = 1
#         rng = numpy.random.default_rng()
#         for rep in range(nreps):
#             rand_e_ranks = rng.permutation(e_ranks)
#             if options.cor_test == "tau":
#                 rand_r = kendalls_tau(rand_e_ranks, x_ranks)
#             else:
#                 rand_r = correlation(e_ranks, x_ranks)
#             if abs(rand_r) >= abs(r):
#                 cnt_r += 1
#             if progress_bar is not None:
#                 progress_bar.setValue(progress_bar.value() + 1)
#
#         p_random = cnt_r / (nreps + 1)
#         p_random_str = format(p_random, inline_float(rand_p_dec))
#         rstr = format(r, inline_float(decimal_places))
#
#         # output
#         output_blocks.append(["<h3>{}</h3>".format(get_text("Rank Correlation Results"))])
#         if options.cor_test == "tau":
#             output = ["Kendall's &tau; = {}".format(rstr)]
#         else:
#             output = ["Spearman's &rho; = {}".format(rstr)]
#         output.append("Probability = {}".format(p_random_str))
#         output_blocks.append(output)
#         citations.append("Sokal_Rohlf_1995")
#
#     else:
#         output_blocks.append([get_text("Fewer than two studies were valid for analysis")])
#
#     return output_blocks, citations
