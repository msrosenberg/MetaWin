"""
Publicationj bias module

This module contains the functions for publication bias methods
"""

import math

import numpy
import scipy.stats

import MetaWinConstants
from MetaWinConstants import mean_data_tuple
from MetaWinUtils import inline_float, calculate_regression, prob_t_score, interval_to_str, create_output_table
import MetaWinCharts
import MetaWinWidgets
from MetaWinLanguage import get_text
from MetaWinAnalysisFunctions import output_filtered_bad, mean_effect_var_and_q, pooled_var_no_structure, \
    median_effect, mean_effects_table


# ---------- rank correlation analysis ----------
def get_ranks(x):
    return scipy.stats.rankdata(x, "average")


def correlation(x, y):
    n = len(x)
    x_mean = numpy.sum(x)/n
    y_mean = numpy.sum(y)/n
    sum_xy = numpy.sum((x - x_mean)*(y - y_mean))
    sum_x2 = numpy.sum(numpy.square(x - x_mean))
    sum_y2 = numpy.sum(numpy.square(y - y_mean))
    return sum_xy / math.sqrt(sum_x2 * sum_y2)


def kendalls_tau(e_ranks, x_ranks):
    n = len(e_ranks)
    sort_data = numpy.zeros(shape=(n, 2))
    # if there are no ties in e_ranks, sort by it, otherwise, sort by x_ranks
    if len(numpy.unique(e_ranks)) < n:
        sort_data[:, 0] = x_ranks
        sort_data[:, 1] = e_ranks
    else:
        sort_data[:, 0] = e_ranks
        sort_data[:, 1] = x_ranks
    sort_data = sort_data[sort_data[:, 0].argsort()]  # sort into ascending order by first column
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            if sort_data[j, 1] > sort_data[i, 1]:
                c += 1
            elif sort_data[j, 1] == sort_data[i, 1]:
                c += 0.5
    sum_n = 4 * c - n * (n - 1)
    # correction terms for ties
    unique, cnts = numpy.unique(e_ranks, return_counts=True)
    t1 = 0
    for c in cnts:
        if c > 1:
            t1 += c * (c - 1)
    unique, cnts = numpy.unique(x_ranks, return_counts=True)
    t2 = 0
    for c in cnts:
        if c > 1:
            t2 += c * (c - 1)

    tau = sum_n / math.sqrt((n * (n - 1) - t1) * (n * (n - 1) - t2))
    return tau


def rank_correlation_analysis(data, options, decimal_places: int = 4, sender=None):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    if options.sample_size is not None:
        sample_sizes = options.sample_size
        do_n = True
    else:
        sample_sizes = None
        do_n = False
    e_data = []
    w_data = []
    v_data = []
    n_data = []
    bad_data = []
    study_names = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if do_n:
                ns = data.check_value(r, sample_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            else:
                ns = 1
            if (e is not None) and (v is not None) and (v > 0) and (ns is not None) and (ns > 0):
                e_data.append(e)
                w_data.append(1/v)
                v_data.append(v)
                if do_n:
                    n_data.append(ns)
                study_names.append(row.label)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)
    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)
    if do_n:
        n_data = numpy.array(n_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    n = len(e_data)
    citations = []
    if n > 1:
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])

        # global value
        df = n - 1
        mean_e, var_e, qt, sum_w, sum_w2, sum_ew = mean_effect_var_and_q(e_data, w_data)
        pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
        if options.random_effects:
            ws_data = numpy.reciprocal(v_data + pooled_var)
            mean_e, var_e, *_ = mean_effect_var_and_q(e_data, ws_data)

        # standardize e and v
        v_star = [v - 1/sum_w for v in v_data]
        e_star = [(e_data[i] - mean_e)/math.sqrt(v_star[i]) for i in range(n)]
        v_star = numpy.array(v_star)
        e_star = numpy.array(e_star)

        if do_n:
            x_star = n_data
        else:
            x_star = v_star

        # calculate rank correlation
        e_ranks = get_ranks(e_star)
        x_ranks = get_ranks(x_star)
        if options.cor_test == "tau":  # Kendall's tau
            r = kendalls_tau(e_ranks, x_ranks)
        else:  # Spearman's rho
            r = correlation(e_ranks, x_ranks)

        # test with randomization
        nreps = options.randomize_model

        if sender is not None:
            progress_bar = MetaWinWidgets.progress_bar(sender, get_text("Resampling Progress"),
                                                       get_text("Conducting Randomization Analysis"), nreps)
        else:
            progress_bar = None

        # decimal places to use for randomization-based p-value
        rand_p_dec = max(decimal_places, math.ceil(math.log10(nreps+1)))
        cnt_r = 1
        rng = numpy.random.default_rng()
        for rep in range(nreps):
            rand_e_ranks = rng.permutation(e_ranks)
            if options.cor_test == "tau":
                rand_r = kendalls_tau(rand_e_ranks, x_ranks)
            else:
                rand_r = correlation(e_ranks, x_ranks)
            if abs(rand_r) >= abs(r):
                cnt_r += 1
            if progress_bar is not None:
                progress_bar.setValue(progress_bar.value() + 1)

        p_random = cnt_r / (nreps + 1)
        p_random_str = format(p_random, inline_float(rand_p_dec))
        rstr = format(r, inline_float(decimal_places))

        # output
        output_blocks.append(["<h3>{}</h3>".format(get_text("Rank Correlation Results"))])
        if options.cor_test == "tau":
            output = ["Kendall's &tau; = {}".format(rstr)]
        else:
            output = ["Spearman's &rho; = {}".format(rstr)]
        output.append("Probability = {}".format(p_random_str))
        output_blocks.append(output)
        citations.append("Sokal_Rohlf_1995")

    else:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])

    return output_blocks, citations


# ---------- trim-and-fill analysis ----------
def trim_and_fill_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    e_data = []
    w_data = []
    v_data = []
    bad_data = []
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
                study_names.append(row.label)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)
    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    chart_data = None
    n = len(e_data)
    citations = []

    if n > 1:
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
        df = n - 1
        mean_e, var_e, qt, sum_w, sum_w2, _ = mean_effect_var_and_q(e_data, w_data)
        median_e = median_effect(e_data, w_data)
        mean_v = numpy.sum(v_data) / n
        pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)

        if options.random_effects:
            ws_data = numpy.reciprocal(v_data + pooled_var)
            mean_e, var_e, qt, *_ = mean_effect_var_and_q(e_data, ws_data)
            median_e = median_effect(e_data, ws_data)
            output_blocks.append([get_text("Estimate of pooled variance") + ": " +
                                  format(pooled_var, inline_float(decimal_places))])

        if norm_ci:
            lower_ci, upper_ci = scipy.stats.norm.interval(alpha=1-alpha, loc=mean_e, scale=math.sqrt(var_e))
        else:
            lower_ci, upper_ci = scipy.stats.t.interval(alpha=1-alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))
        original_mean_data = mean_data_tuple(get_text("Original Mean"), 0, n, mean_e, median_e, var_e, mean_v,
                                             lower_ci, upper_ci, 0, 0, 0, 0)
        original_mean = mean_e

        trim_n = -1
        new_trim = 0
        iterations = 0
        tmp_mean_e = mean_e
        skew_right = True
        while (trim_n != new_trim) and (iterations < 1000):
            iterations += 1
            trim_n = new_trim
            tmp_data = numpy.zeros(shape=(n, 3))
            tmp_data[:, 0] = e_data
            tmp_data[:, 1] = w_data
            tmp_data[:, 2] = v_data
            if skew_right:
                tmp_data = tmp_data[tmp_data[:, 0].argsort()[::-1]]  # sort into descending order by first column
            else:
                tmp_data = tmp_data[tmp_data[:, 0].argsort()]  # sort into ascending order by first column

            # trim the first trim_n rows
            trim_data = tmp_data[trim_n:, :]
            # calculate the mean for just the trimmed data
            (tmp_mean_e, tmp_var_e, tmp_qt, tmp_sum_w, tmp_sum_w2,
             tmp_sum_ew) = mean_effect_var_and_q(trim_data[:, 0], trim_data[:, 1])
            tmp_df = n - trim_n - 1
            if options.random_effects:
                tmp_pooled_var = pooled_var_no_structure(tmp_qt, tmp_sum_w, tmp_sum_w2, tmp_df)
                tmp_ws = numpy.reciprocal(trim_data[:, 2] + tmp_pooled_var)
                tmp_mean_e, *_ = mean_effect_var_and_q(trim_data[:, 0], tmp_ws)

            # using this new mean, calculate the thresholds for all of the data
            diff = tmp_data[:, 0] - tmp_mean_e
            abs_diff = numpy.abs(diff)
            ranks = abs_diff.argsort().argsort()
            ranks = (ranks+1)*numpy.sign(diff)
            pos = [r > 0 for r in ranks]
            neg = [r < 0 for r in ranks]
            t_pos = numpy.sum(ranks[pos])
            t_neg = numpy.sum(numpy.abs(ranks[neg]))
            if t_pos > t_neg:  # right skew
                gamma = n - abs(numpy.min(ranks))
                t_n = t_pos
            else:  # left skew
                gamma = n - abs(numpy.max(ranks))
                t_n = t_neg
                skew_right = False
            if options.k_estimator == "R":  # R0
                new_trim = max(0, round(gamma - 1))
            elif options.k_estimator == "Q":  # Q0
                new_trim = max(0, round(n - 1 / 2 - math.sqrt(2 * n ** 2 - 4 * t_n + 1 / 4)))
            else:  # L0
                new_trim = max(0, round((4*t_n - n*(n+1))/(2*n - 1)))

        # create the new data set with the estimated missing values
        sort_data = numpy.zeros(shape=(n, 3))
        sort_data[:, 0] = e_data
        sort_data[:, 1] = w_data
        sort_data[:, 2] = v_data
        if skew_right:
            sort_data = sort_data[sort_data[:, 0].argsort()[::-1]]  # sort into descending order by first column
        else:
            sort_data = sort_data[sort_data[:, 0].argsort()]  # sort into ascending order by first column
        tmp_data = numpy.zeros(shape=(n+trim_n, 3))
        tmp_data[:n, 0] = sort_data[:, 0]
        tmp_data[:n, 1] = sort_data[:, 1]
        tmp_data[:n, 2] = sort_data[:, 2]
        for i in range(trim_n):
            d = tmp_data[i, 0] - tmp_mean_e
            tmp_data[n+i, 0] = tmp_mean_e - d
            tmp_data[n+i, 1] = tmp_data[i, 1]
            tmp_data[n+i, 2] = tmp_data[i, 2]

        # calculate the new mean, etc.
        mean_e, var_e, qt, sum_w, sum_w2, _ = mean_effect_var_and_q(tmp_data[:, 0], tmp_data[:, 1])
        median_e = median_effect(tmp_data[:, 0], tmp_data[:, 1])
        df = n + trim_n - 1
        if options.random_effects:
            pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, df)
            ws = numpy.reciprocal(tmp_data[:, 2] + pooled_var)
            mean_e, var_e, *_ = mean_effect_var_and_q(tmp_data[:, 0], ws)

        if norm_ci:
            lower_ci, upper_ci = scipy.stats.norm.interval(alpha=1-alpha, loc=mean_e, scale=math.sqrt(var_e))
        else:
            lower_ci, upper_ci = scipy.stats.t.interval(alpha=1-alpha, df=df, loc=mean_e, scale=math.sqrt(var_e))
        trim_mean_data = mean_data_tuple(get_text("Trim and Fill Mean"), 0, n+trim_n, mean_e, median_e, var_e, mean_v,
                                         lower_ci, upper_ci, 0, 0, 0, 0)

        # output
        output_blocks.append([get_text("Trim and Fill Analysis estimated {} missing studies.").format(trim_n)])
        mean_data = [original_mean_data, trim_mean_data]
        output_blocks.append(["<h4>{}</h4>".format(get_text("Mean Effect Sizes"))])
        output_blocks.append(mean_effects_table(effect_sizes.label, mean_data, options.bootstrap_mean,
                             decimal_places, alpha, options.log_transformed))

        if options.create_graph:
            chart_data = MetaWinCharts.chart_trim_fill_plot(effect_sizes.label, tmp_data, n,  original_mean, mean_e)

    else:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])

    return output_blocks, chart_data, None, citations


def funnel_plot_setup(data, options):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    if options.sample_size is not None:
        sample_sizes = options.sample_size
        do_n = True
    else:
        sample_sizes = None
        do_n = False

    e_data = []
    w_data = []
    v_data = []
    n_data = []
    bad_data = []
    study_names = []
    filtered = []

    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, effect_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, variances.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if do_n:
                ns = data.check_value(r, sample_sizes.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            else:
                ns = 1
            if (e is not None) and (v is not None) and (v > 0) and (ns is not None) and (ns > 0):
                e_data.append(e)
                w_data.append(1/v)
                v_data.append(v)
                if do_n:
                    n_data.append(ns)
                study_names.append(row.label)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)
    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)

    if options.funnel_y == "variance":
        y_data = v_data
    elif options.funnel_y == "inverse variance":
        y_data = w_data
    elif options.funnel_y == "standard error":
        y_data = numpy.sqrt(v_data)
    elif options.funnel_y == "precision":
        y_data = 1/numpy.sqrt(v_data)
    else:
        y_data = numpy.array(n_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    n = len(e_data)
    citations = []
    if n > 1:
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])
        mean_e, *_ = mean_effect_var_and_q(e_data, w_data)
        citations.append("Light_Pillemer_1984")
        citations.append("Sterne_Egger_2001")
        chart_data = MetaWinCharts.chart_funnel_plot(e_data, y_data, mean_e, effect_sizes.label, options.funnel_y)
    else:
        output_blocks.append([get_text("Fewer than two studies were valid for analysis")])
        chart_data = None

    return output_blocks, chart_data, citations


# ---------- Egger regression ----------
def egger_regression(data, options, decimal_places: int = 4, alpha: float = 0.05, norm_ci: bool = True):
    # filter and prepare data for analysis
    effect_sizes = options.effect_data
    variances = options.effect_vars
    e_data = []
    w_data = []
    v_data = []
    bad_data = []
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
                study_names.append(row.label)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)
    e_data = numpy.array(e_data)
    w_data = numpy.array(w_data)
    v_data = numpy.array(v_data)

    output_blocks = output_filtered_bad(filtered, bad_data)

    chart_data = None
    n = len(e_data)

    citations = []
    if n > 2:
        output_blocks.append([get_text("{} studies will be included in this analysis").format(n)])

        if options.random_effects:
            _, _, qt, sum_w, sum_w2, _ = mean_effect_var_and_q(e_data, w_data)
            pooled_var = pooled_var_no_structure(qt, sum_w, sum_w2, n - 1)
            x_data = numpy.sqrt(numpy.reciprocal(v_data + pooled_var))
            citations.append("Lin_Chu_2018")
        else:
            x_data = numpy.sqrt(w_data)
        y_data = e_data*x_data

        # x_data = numpy.sqrt(w_data)
        # y_data = e_data*x_data
        slope, intercept, s2slope, s2intercept = calculate_regression(x_data, y_data)
        se_slope = math.sqrt(s2slope)
        se_intercept = math.sqrt(s2intercept)
        slope_lower, slope_upper = scipy.stats.t.interval(alpha=1-alpha, df=n-2, loc=slope, scale=se_slope)
        intercept_lower, intercept_upper = scipy.stats.t.interval(alpha=1-alpha, df=n-2, loc=intercept,
                                                                  scale=se_intercept)
        p_slope = prob_t_score(slope/se_slope, df=n-2)
        p_intercept = prob_t_score(intercept/se_intercept, df=n-2)

        # output
        output = []
        col_headers = [get_text("Predictor"), get_text("Value"), "SE", "df", "{:0.0%} CI".format(1 - alpha), "P(t)"]
        col_formats = ["", "f", "f", "", "", "f"]
        table_data = [["Intercept", intercept, se_intercept, n-2, interval_to_str(intercept_lower, intercept_upper,
                                                                                  decimal_places), p_intercept],
                      ["Slope", slope, se_slope, n-2, interval_to_str(slope_lower, slope_upper, decimal_places),
                       p_slope]]
        create_output_table(output, table_data, col_headers, col_formats, decimal_places)
        output_blocks.append(output)

        if options.create_graph:
            if options.random_effects:
                model = get_text("random effects")
            else:
                model = get_text("fixed effects")
            chart_data = MetaWinCharts.chart_stnd_regression("precision", "standardized effect size", x_data,
                                                             y_data, slope, intercept, model, 0)
    else:
        output_blocks.append([get_text("Fewer than three studies were valid for analysis")])

    return output_blocks, chart_data, citations
