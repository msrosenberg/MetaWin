"""
Mathematics for the MetaCalculator functions
"""

import math
import scipy.stats


def variance_to_sd(variance: float) -> float:
    return math.sqrt(variance)


def se_to_sd(se: float, n: int) -> float:
    return se * math.sqrt(n)


def normal_deviate(sd: float, mean: float, variate: float) -> float:
    return (variate - mean) / sd


def zscore_to_r(z: float, n: int) -> float:
    return z / math.sqrt(n)


def zscore_to_one_tailed_p(z: float) -> float:
    return 1-scipy.stats.norm.cdf(z)


def zscore_to_two_tailed_p(z: float) -> float:
    return 2*(1-scipy.stats.norm.cdf(abs(z)))


def one_tailed_p_to_zscore(p: float) -> float:
    return scipy.stats.norm.ppf(1 - p)


def two_tailed_p_to_zscore(p: float) -> float:
    return scipy.stats.norm.ppf(1 - p/2)


def chi2_to_r(chisq: float, n: int) -> float:
    return math.sqrt(chisq / n)


def chi2_uneven_to_r(chisq: float, n: int, k: float) -> float:
    return math.sqrt(chisq / (k * n))


def chi2_to_p(chisq: float, df: int) -> float:
    return 1-scipy.stats.chi2.cdf(chisq, df)


def f_to_p(f: float, df1: int, df2: int) -> float:
    return 1-scipy.stats.f.cdf(f, df1, df2)


def f_to_r(f: float, df2: int) -> float:
    return math.sqrt(f / (f + df2))


def t_to_r(t: float, df: int) -> float:
    return math.sqrt(t**2 / (t**2 + df))


def t_to_one_tailed_p(t: float, df: int) -> float:
    return 1-scipy.stats.t.cdf(t, df)


def t_to_two_tailed_p(t: float, df: int) -> float:
    return 2*(1-scipy.stats.t.cdf(abs(t), df))


def zr_to_r(zr: float) -> float:
    return math.tanh(zr)


def r_to_zr(r: float) -> float:
    return math.atanh(r)


def hedges_g_to_r(g: float, df: int, n1: int, n2: int) -> float:
    return math.sqrt((g**2 * n1 * n2) / ((g**2 * n1 * n2) + (df*(n1 + n2))))


def r_to_hedges_g(r: float, df: int, n1: int, n2: int) -> float:
    return (r / math.sqrt(1 - r**2)) * math.sqrt((df * (n1 + n2)) / (n1 * n2))


def hedges_g_to_cohens_d(g: float, df: int, n1: int, n2: int) -> float:
    return g * math.sqrt((n1 + n2) / df)


def t_to_hedges_g(t, n1, n2) -> float:
    return t * math.sqrt(n1 + n2) / math.sqrt(n1 * n2)


def hedges_g_to_hedges_d(g: float, n1: int, n2: int) -> float:
    return g * (1 - (3 / ((4 * (n1 + n2 - 2)) - 1)))


def t_to_cohens_d(t: float, df: int, n1: int, n2: int) -> float:
    return t * (n1 + n2) / (math.sqrt(df) * math.sqrt(n1*n2))


def r_to_cohens_d(r: float) -> float:
    return 2 * r / math.sqrt(1 - r**2)


def f_to_cohens_d(f: float, df: int, n1: int, n2: int) -> float:
    return (math.sqrt(f) * (n1 + n2)) / (math.sqrt(df) * math.sqrt(n1*n2))


def cohens_d_to_r(d: float, n1: int, n2: int) -> float:
    return d / (math.sqrt(d**2 + ((n1 + n2)**2 / (n1*n2))))


def cohens_d_to_hedges_g(d: float, df: int, n1: int, n2: int) -> float:
    return d / math.sqrt((n1 + n2) / df)
