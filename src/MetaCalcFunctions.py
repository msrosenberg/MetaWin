from typing import Tuple, Optional, Union
from PyQt6.QtWidgets import QListWidgetItem
import MetaCalcMath

# field types
NUMBER_ZERO_OR_POS = 0
NUMBER_POSITIVE = 1
NUMBER_ANY = 2
NUMBER_0_TO_1 = 3
NUMBER_NEG1_TO_POS1 = 4
INT_2_OR_MORE = 5
INT_1_OR_MORE = 6
NUMBER_1_OR_MORE = 7

Number = Union[float, int]


"""
MetaCalculator Classes
"""


class MetaCalcListItem(QListWidgetItem):
    """
    Variant of QListWidgetItem which has a MetaCalc function attached to it
    """
    def __init__(self):
        super().__init__()
        self.__mc_function = None

    @property
    def mc_function(self):
        return self.__mc_function

    @mc_function.setter
    def mc_function(self, mcf):
        self.__mc_function = mcf


class InputField:
    def __init__(self, name="", ft=None):
        self.__field_name = name
        self.__field_type = ft

    @property
    def field_name(self) -> str:
        return self.__field_name

    @field_name.setter
    def field_name(self, name: str) -> None:
        self.__field_name = name

    @property
    def field_type(self) -> str:
        return self.__field_type

    @field_type.setter
    def field_type(self, ft: str) -> None:
        self.__field_type = ft


class MetaCalcFunction:
    def __init__(self):
        self.__name = ""
        self.__output_text = ""
        self.__input_fields = []
        self.calculate = None

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, new_name: str) -> None:
        self.__name = new_name

    def n_inputs(self) -> int:
        return len(self.__input_fields)

    @property
    def input_fields(self) -> list:
        return self.__input_fields

    @input_fields.setter
    def input_fields(self, fields: list) -> None:
        self.__input_fields = fields

    @property
    def output_text(self) -> str:
        return self.__output_text

    @output_text.setter
    def output_text(self, output: str) -> None:
        self.__output_text = output

    def do_calculation(self, input_fields: list, *args) -> Tuple[Optional[float], str]:
        """
        Check all values for validity and create error messages if necessary; if all is good
        call the unique calculate function with the converted inputs
        """
        error_msg = ""
        inputs = []
        for i, inp in enumerate(input_fields):
            v = evaluate_value(args[i], inp.field_type)
            if v is None:
                error_msg = add_error_message(error_msg, inp, args[i])
            inputs.append(v)
        if None in inputs:
            return None, error_msg
        else:
            return self.calculate(*inputs), error_msg


"""
Evaluate Inputs for Validity

Each function takes a string and tries to evaluate it for a valid numeric type. Beyond simply checking type, in
most cases it also checks to confirm the number is part of a valid range. The functions return None if the type 
or value is invalid, otherwise they return the number.
"""


# generic function call to call others
def evaluate_value(input_str: str, field_type: int) -> Optional[Number]:
    if input_str.strip() == "":
        return None
    elif field_type == NUMBER_ZERO_OR_POS:
        return eval_number_zero_or_positive(input_str)
    elif field_type == NUMBER_POSITIVE:
        return eval_number_positive(input_str)
    elif field_type == NUMBER_ANY:
        return eval_number(input_str)
    elif field_type == NUMBER_0_TO_1:
        return eval_number_0_to_1(input_str)
    elif field_type == NUMBER_NEG1_TO_POS1:
        return eval_number_neg1_to_pos1(input_str)
    elif field_type == INT_2_OR_MORE:
        return eval_int_2_or_more(input_str)
    elif field_type == INT_1_OR_MORE:
        return eval_int_1_or_more(input_str)
    elif field_type == NUMBER_1_OR_MORE:
        return eval_number_1_or_more(input_str)
    else:
        return None


# real number greater than or equal to zero
def eval_number_zero_or_positive(input_str: str) -> Optional[Number]:
    try:
        try:
            value = int(input_str.strip())
        except ValueError:
            value = float(input_str.strip())
        if value < 0:
            value = None
    except ValueError:
        value = None
    return value


# real number greater than zero
def eval_number_positive(input_str: str) -> Optional[Number]:
    try:
        try:
            value = int(input_str.strip())
        except ValueError:
            value = float(input_str.strip())
        if value <= 0:
            value = None
    except ValueError:
        value = None
    return value


# real number between 0 and 1, inclusive
def eval_number_0_to_1(input_str: str) -> Optional[Number]:
    try:
        try:
            value = int(input_str.strip())
        except ValueError:
            value = float(input_str.strip())
        if (value < 0) or (value > 1):
            value = None
    except ValueError:
        value = None
    return value


# real number between -1 and 1, inclusive
def eval_number_neg1_to_pos1(input_str: str) -> Optional[Number]:
    try:
        try:
            value = int(input_str.strip())
        except ValueError:
            value = float(input_str.strip())
        if (value < -1) or (value > 1):
            value = None
    except ValueError:
        value = None
    return value


# real number greater or equal to 1
def eval_number_1_or_more(input_str: str) -> Optional[Number]:
    try:
        try:
            value = int(input_str.strip())
        except ValueError:
            value = float(input_str.strip())
        if value < 1:
            value = None
    except ValueError:
        value = None
    return value


# any real number
def eval_number(input_str: str) -> Optional[Number]:
    try:
        try:
            value = int(input_str.strip())
        except ValueError:
            value = float(input_str.strip())
    except ValueError:
        value = None
    return value


# integer greater than one
def eval_int_2_or_more(input_str: str) -> Optional[int]:
    try:
        value = int(input_str.strip())
        if value < 2:
            value = None
    except ValueError:
        value = None
    return value


# integer greater than zero
def eval_int_1_or_more(input_str: str) -> Optional[int]:
    try:
        value = int(input_str.strip())
        if value < 1:
            value = None
    except ValueError:
        value = None
    return value


"""
Miscellaneous Support Functions
"""


def add_error_message(msg: str, inp: InputField, inp_str: str) -> str:
    if msg != "":
        msg += "\n\n"
    msg += "Invalid {}: {}".format(inp.field_name, inp_str) + "\n"
    if inp.field_type == NUMBER_ZERO_OR_POS:
        msg += "{} must be a real number greater or equal to zero.".format(inp.field_name)
    elif inp.field_type == NUMBER_POSITIVE:
        msg += "{} must be a real number greater than zero.".format(inp.field_name)
    elif inp.field_type == INT_2_OR_MORE:
        msg += "{} must be an integer greater or equal to two.".format(inp.field_name)
    elif inp.field_type == INT_1_OR_MORE:
        msg += "{} must be an integer greater or equal to one.".format(inp.field_name)
    elif inp.field_type == NUMBER_NEG1_TO_POS1:
        msg += "{} must be a real number between negative one and one.".format(inp.field_name)
    elif inp.field_type == NUMBER_0_TO_1:
        msg += "{} must be a real number between zero and one.".format(inp.field_name)
    elif inp.field_type == NUMBER_ANY:
        msg += "{} must be a real number.".format(inp.field_name)
    elif inp.field_type == NUMBER_1_OR_MORE:
        msg += "{} must be a real number greater or equal to one.".format(inp.field_name)
    return msg


"""
MetaCalculator Functions
"""


# Variance → Standard Deviation
def variance_to_sd_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Variance → Standard Deviation"
    f.output_text = "Standard Deviation"
    var_field = InputField("Variance", NUMBER_ZERO_OR_POS)
    f.input_fields = [var_field]
    f.calculate = MetaCalcMath.variance_to_sd
    return f


# Standard Error → Standard Deviation
def se_to_sd_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Standard Error → Standard Deviation"
    f.output_text = "Standard Deviation"
    se_field = InputField("Standard Error", NUMBER_ZERO_OR_POS)
    n_field = InputField("Sample Size", INT_2_OR_MORE)
    f.input_fields = [se_field, n_field]
    f.calculate = MetaCalcMath.se_to_sd
    return f


# Normal Deviate
def normal_deviate_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Z-score (Standard Normal Deviate)"
    f.output_text = "Z-score"
    sd_field = InputField("Standard Deviation", NUMBER_POSITIVE)
    mean_field = InputField("Mean", NUMBER_ANY)
    variate_field = InputField("Variate", NUMBER_ANY)
    f.input_fields = [sd_field, mean_field, variate_field]
    f.calculate = MetaCalcMath.normal_deviate
    return f


# Z-score → r
def zscore_to_r_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Z-score → Correlation"
    f.output_text = "Correlation (r)"
    z_field = InputField("Z-score", NUMBER_ANY)
    n_field = InputField("Sample Size", INT_2_OR_MORE)
    f.input_fields = [z_field, n_field]
    f.calculate = MetaCalcMath.zscore_to_r
    return f


# Z-score → one-tailed p
def zscore_to_one_tailed_p_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Z-score → One-tailed Probability"
    f.output_text = "One-tailed Probability (p)"
    z_field = InputField("Z-score", NUMBER_ANY)
    f.input_fields = [z_field]
    f.calculate = MetaCalcMath.zscore_to_one_tailed_p
    return f


# Z-score → two-tailed p
def zscore_to_two_tailed_p_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Z-score → Two-tailed Probability"
    f.output_text = "Two-tailed Probability (p)"
    z_field = InputField("Z-score", NUMBER_ANY)
    f.input_fields = [z_field]
    f.calculate = MetaCalcMath.zscore_to_two_tailed_p
    return f


# one-tailed p → Z-score
def one_tailed_p_to_zscore_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "One-tailed Probability → Z-score"
    f.output_text = "Z-score"
    p_field = InputField("One-tailed Probability", NUMBER_0_TO_1)
    f.input_fields = [p_field]
    f.calculate = MetaCalcMath.one_tailed_p_to_zscore
    return f


# two-tailed p → Z-score
def two_tailed_p_to_zscore_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Two-tailed Probability → Z-score"
    f.output_text = "Z-score"
    p_field = InputField("Two-tailed Probability", NUMBER_0_TO_1)
    f.input_fields = [p_field]
    f.calculate = MetaCalcMath.two_tailed_p_to_zscore
    return f


# χ2 to Correlation
def chi2_to_r_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "χ2 → Correlation (Equal Expectation)"
    f.output_text = "Correlation (r)"
    chi2_field = InputField("χ2 [1 df]", NUMBER_ZERO_OR_POS)
    n_field = InputField("Sample Size", INT_2_OR_MORE)
    f.input_fields = [chi2_field, n_field]
    f.calculate = MetaCalcMath.chi2_to_r
    return f


# χ2 (uneven) to Correlation
def chi2_uneven_to_r_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "χ2 → Correlation (Unequal Expectation)"
    f.output_text = "Correlation (r)"
    chi2_field = InputField("χ2 [1 df]", NUMBER_ZERO_OR_POS)
    n_field = InputField("Sample Size", INT_2_OR_MORE)
    k_field = InputField("Ratio of Expectations (k)", NUMBER_POSITIVE)
    f.input_fields = [chi2_field, n_field, k_field]
    f.calculate = MetaCalcMath.chi2_uneven_to_r
    return f


# χ2 to Probability
def chi2_to_p_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "χ2 → Probability"
    f.output_text = "Probability (p)"
    chi2_field = InputField("χ2 [DF]", NUMBER_ZERO_OR_POS)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    f.input_fields = [chi2_field, df_field]
    f.calculate = MetaCalcMath.chi2_to_p
    return f


# F to Probability
def f_to_p_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "F Statistic → Probability"
    f.output_text = "Probability (p)"
    f_field = InputField("F Statistic [DF1, DF2]", NUMBER_ZERO_OR_POS)
    df1_field = InputField("Degrees of Freedom (DF1)", INT_1_OR_MORE)
    df2_field = InputField("Residual Degrees of Freedom (DF2)", INT_1_OR_MORE)
    f.input_fields = [f_field, df1_field, df2_field]
    f.calculate = MetaCalcMath.f_to_p
    return f


# F to Correlation
def f_to_r_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "F Statistic → Correlation"
    f.output_text = "Correlation (r)"
    f_field = InputField("F Statistic [1, DF2]", NUMBER_ZERO_OR_POS)
    df2_field = InputField("Residual Degrees of Freedom (DF2)", INT_1_OR_MORE)
    f.input_fields = [f_field, df2_field]
    f.calculate = MetaCalcMath.f_to_r
    return f


# t to Correlation
def t_to_r_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "t-Statistic → Correlation"
    f.output_text = "Correlation (r)"
    t_field = InputField("t-Statistic [DF]", NUMBER_ANY)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    f.input_fields = [t_field, df_field]
    f.calculate = MetaCalcMath.t_to_r
    return f


# t to One-tailed Probability
def t_to_one_tailed_p_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "t-Statistic → One-tailed Probability"
    f.output_text = "One-tailed Probability (p)"
    t_field = InputField("t-Statistic [DF]", NUMBER_ANY)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    f.input_fields = [t_field, df_field]
    f.calculate = MetaCalcMath.t_to_one_tailed_p
    return f


# t to Two-tailed Probability
def t_to_two_tailed_p_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "t-Statistic → Two-tailed Probability"
    f.output_text = "Two-tailed Probability (p)"
    t_field = InputField("t-Statistic [DF]", NUMBER_ANY)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    f.input_fields = [t_field, df_field]
    f.calculate = MetaCalcMath.t_to_two_tailed_p
    return f


# Z-transform to correlation
def zr_to_r_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Z-transform → Correlation"
    f.output_text = "Correlation (r)"
    zr_field = InputField("Z-transform", NUMBER_ANY)
    f.input_fields = [zr_field]
    f.calculate = MetaCalcMath.zr_to_r
    return f


# Correlation to Z-transform
def r_to_zr_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Correlation → Z-transform"
    f.output_text = "Z-transform"
    r_field = InputField("Correlation (r)", NUMBER_NEG1_TO_POS1)
    f.input_fields = [r_field]
    f.calculate = MetaCalcMath.r_to_zr
    return f


# Hedges' g to r
def hedges_g_to_r_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Hedges\' g → Correlation"
    f.output_text = "Correlation (r)"
    g_field = InputField("Hedges\' g", NUMBER_ANY)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Control Sample Size", INT_2_OR_MORE)
    f.input_fields = [g_field, df_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.hedges_g_to_r
    return f


# r to Hedges' g
def r_to_hedges_g_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Correlation → Hedges\' g"
    f.output_text = "Hedges\' g"
    r_field = InputField("Correlation (r)", NUMBER_ANY)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Control Sample Size", INT_2_OR_MORE)
    f.input_fields = [r_field, df_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.r_to_hedges_g
    return f


# Hedges' g to Hedges' d
def hedges_g_to_hedges_d_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Hedges\' g → Hedges\' d"
    f.output_text = "Hedges\' d"
    g_field = InputField("Hedges\' g", NUMBER_ANY)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Control Sample Size", INT_2_OR_MORE)
    f.input_fields = [g_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.hedges_g_to_hedges_d
    return f


# t to Hedges' g
def t_to_hedges_g_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "t-Statistic → Hedges\' g"
    f.output_text = "Hedges\' g"
    t_field = InputField("t-Statistic", NUMBER_ANY)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Control Sample Size", INT_2_OR_MORE)
    f.input_fields = [t_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.t_to_hedges_g
    return f


# Hedges' g to Cohen's d
def hedges_g_to_cohens_d_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Hedges\' g → Cohen\'s d"
    f.output_text = "Cohen\'s d"
    g_field = InputField("Hedges\' g", NUMBER_ANY)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Control Sample Size", INT_2_OR_MORE)
    f.input_fields = [g_field, df_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.hedges_g_to_hedges_d
    return f


# t to Cohen's d
def t_to_cohens_d_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "t-Statistic → Cohen\'s d"
    f.output_text = "Cohen\'s d"
    t_field = InputField("t-Statistic", NUMBER_ANY)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Sample Size", INT_2_OR_MORE)
    f.input_fields = [t_field, df_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.t_to_cohens_d
    return f


# r to Cohen's d
def r_to_cohens_d_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Correlation → Cohen\'s d"
    f.output_text = "Cohen\'s d"
    r_field = InputField("Correlation (r)", NUMBER_ANY)
    f.input_fields = [r_field]
    f.calculate = MetaCalcMath.r_to_cohens_d
    return f


# F to Cohhen's d
def f_to_cohens_d_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "F Statistic → Cohen\'s d"
    f.output_text = "Cohen\'s d"
    f_field = InputField("F Statistic [1, DF]", NUMBER_ZERO_OR_POS)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Control Sample Size", INT_2_OR_MORE)
    f.input_fields = [f_field, df_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.f_to_cohens_d
    return f


# Cohen's d to r
def cohens_d_to_r_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Cohen\'s d → Correlation"
    f.output_text = "Correlation (r)"
    d_field = InputField("Cohen\'s d", NUMBER_ANY)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Control Sample Size", INT_2_OR_MORE)
    f.input_fields = [d_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.cohens_d_to_r
    return f


# Cohen's d to Hedges' g
def cohens_d_to_hedges_g_function() -> MetaCalcFunction:
    f = MetaCalcFunction()
    f.name = "Cohen\'s d → Hedges\' g"
    f.output_text = "Hedges\' g"
    d_field = InputField("Cohen\'s d", NUMBER_ANY)
    df_field = InputField("Degrees of Freedom", INT_1_OR_MORE)
    n1_field = InputField("Experiment Sample Size", INT_2_OR_MORE)
    n2_field = InputField("Control Sample Size", INT_2_OR_MORE)
    f.input_fields = [d_field, df_field, n1_field, n2_field]
    f.calculate = MetaCalcMath.cohens_d_to_hedges_g
    return f


# master function to create a list of all calculation functions
def load_all_functions() -> tuple:
    function_list = (variance_to_sd_function(),
                     se_to_sd_function(),
                     normal_deviate_function(),
                     zscore_to_r_function(),
                     zscore_to_one_tailed_p_function(),
                     zscore_to_two_tailed_p_function(),
                     one_tailed_p_to_zscore_function(),
                     two_tailed_p_to_zscore_function(),
                     chi2_to_r_function(),
                     chi2_uneven_to_r_function(),
                     chi2_to_p_function(),
                     f_to_r_function(),
                     f_to_p_function(),
                     t_to_r_function(),
                     t_to_one_tailed_p_function(),
                     t_to_two_tailed_p_function(),
                     zr_to_r_function(),
                     r_to_zr_function(),
                     hedges_g_to_r_function(),
                     r_to_hedges_g_function(),
                     hedges_g_to_hedges_d_function(),
                     t_to_hedges_g_function(),
                     hedges_g_to_cohens_d_function(),
                     t_to_cohens_d_function(),
                     r_to_cohens_d_function(),
                     f_to_cohens_d_function(),
                     cohens_d_to_r_function(),
                     cohens_d_to_hedges_g_function())
    return function_list
