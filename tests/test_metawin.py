"""
testing MetaWin

some of these functions are formal tests where values are compared to expectations, whether from MetaWin 2 or other
published or calculated sources

other tests are strictly functional (e.g., bootstrapping and randomization), checking that interfaces haven't
broken or producing figures that can be  visually examined to see if they look correct

whether figures are displayed or not across tests is controlled by the global boolean TEST_FIGURES
"""


import math
from typing import Tuple

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFrame, QPushButton, QTextEdit

# note these may be marked by the IDE as unknown modules, but pytest.ini will resolve the errors when tests
# are actually executed
import MetaWinCharts
from MetaWinImport import ImportTextOptions, split_text_data, convert_strings_to_numbers
from MetaWinEffects import EffectSizeOptions, do_effect_calculations
from MetaWinData import MetaWinData
import MetaWinEffectFunctions
import MetaWinAnalysis
import MetaWinTree
import MetaWinDraw


TEST_FIGURES = True


class TestFigureDialog(QDialog):
    def __init__(self, figure, caption):
        super().__init__()
        self.init_ui(figure, caption)

    def init_ui(self, figure, caption):
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.accept)
        figure_layout = QVBoxLayout()
        figure_layout.addWidget(figure)
        caption_area = QTextEdit()
        caption_area.setText(caption)
        main_frame = QFrame()
        main_frame.setLayout(figure_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_frame)
        main_layout.addWidget(caption_area)
        main_layout.addWidget(ok_button)
        self.setLayout(main_layout)


def print_test_output(output: list) -> None:
    for block in output:
        print()
        for line in block:
            print(line)


def import_test_data(filename: str) -> Tuple[MetaWinData, list]:
    with open(filename, "r") as infile:
        indata = infile.readlines()
        import_options = ImportTextOptions()
        import_options.col_headers = True
        data = split_text_data(indata, import_options)
        convert_strings_to_numbers(data)
    return data, import_options.return_output()


def test_data_import() -> None:
    col_headers = ["Habitat", "+/-", "Nc", "Ne", "Xc", "Xe", "Sc", "Se", "Author", "Species"]
    answer = [["Terrestrial", "+", 7, 7, 78.14, 79.71, 40.65, 40.65, "Fo1", "Bouteloua rigidiseta"],
              ["Terrestrial", "+", 7, 7, 18.86, 26, 9.17, 9.17, "Fo2", "Aristida longiseta"],
              ["Terrestrial", "-", 6, 6, -1.8, -2.1, 0.49, 0.49, "Pl1", "Mirabilis hirsuta"],
              ["Terrestrial", "-", 5, 5, -2.2, -2.8, 0.224, 0.447, "Pl2", "Verbena stricta"],
              ["Terrestrial", "-", 7, 7, -2.1, -3, 0.265, 0.529, "Pl3", "Solidaga rigada"],
              ["Terrestrial", "-", 6, 6, -2.3, -4.2, 0.49, 1.225, "Pl4", "Asclepias syriaca"],
              ["Terrestrial", "+", 3, 3, 85.3, 285.7, 115.008, 153.806, "Gr1", "Verbascum thapsus"],
              ["Terrestrial", "+", 3, 3, 0, 3, 0, 2.425, "Gr2", "Oenothera biennis"],
              ["Terrestrial", "+", 3, 3, 0, 2, 0, 2.078, "Gr3", "Verbascum thapsus"],
              ["Terrestrial", "+", 3, 3, 0, 1.67, 0, 1.732, "Gr4", "Oenothera biennis"],
              ["Terrestrial", "+", 5, 5, 17, 17, 7.603, 5.367, "Po1", "Plantago major"],
              ["Terrestrial", "+", 5, 5, 47, 37, 10.286, 9.391, "Po2", "Plantago lanceolata"],
              ["Terrestrial", "+", 4, 4, 87, 272, 37.712, 183.532, "Bu1", "Metrosideros polymorpha"],
              ["Terrestrial", "+", 18, 20, -0.113, 0.294, 0.255, 0.215, "Gu1", "Stipa neomexicana"],
              ["Terrestrial", "+", 20, 20, -0.163, 0.412, 0.588, 0.218, "Gu2", "Stipa neomexicana"],
              ["Terrestrial", "+", 18, 20, 0.14, 0.632, 0.38, 0.359, "Gu3", "Stipa neomexicana"],
              ["Terrestrial", "+", 20, 20, -0.184, 0.259, 0.326, 0.238, "Gu4", "Aristida glauca"],
              ["Terrestrial", "+", 20, 20, -0.075, 0.354, 0.487, 0.182, "Gu5", "Aristida glauca"],
              ["Terrestrial", "+", 20, 20, 0.147, 0.541, 0.34, 0.299, "Gu6", "Aristida glauca"],
              ["Lentic", "-", 4, 4, 281.11, -201.03, 158.038, 27.52, "Mc1", "Eleocharis acicularis"],
              ["Lentic", "-", 4, 4, 187.31, -155.32, 80.163, 41.252, "Mc2", "Juncus pelocarpus"],
              ["Marine", "+", 7, 7, 11.8, 16, 3.08, 3.37, "St1", "Acropora spp."],
              ["Marine", "+", 3, 10, 0.4, 9.5, 1.47, 7.23, "St2", "Pocillopora verrucosa"],
              ["Marine", "+", 20, 20, 0, 14.1, 7.603, 7.603, "Re1", "Pterygophora californica"],
              ["Marine", "+", 20, 20, 0, 7.1, 3.13, 3.13, "Re2", "Macrocystis pyrifera"],
              ["Marine", "+", 20, 20, 0, 1.4, 1.789, 1.789, "Re3", "Desmarestia ligulata"],
              ["Marine", "+", 10, 10, 82.2, 94, 29.093, 9.171, "Re4", "Desmarestia ligulata"],
              ["Marine", "+", 10, 10, 8.3, 10.5, 14.546, 11.068, "Re5", "Desmarestiia kurilensis"],
              ["Marine", "+", 10, 10, 0, 20, 42.691, 42.691, "Re6", "Nereocystis luetkeana"],
              ["Marine", "+", 2, 2, 3.63, 18.5, 3.352, 4.257, "Jo1", "Laminaria longicruris"],
              ["Marine", "+", 2, 2, 0, 0.25, 0, 0.354, "Jo2", "Laminaria longicruris"],
              ["Marine", "+", 2, 2, 3.63, 2.25, 3.354, 0.707, "Jo3", "Laminaria longicruris"],
              ["Marine", "+", 4, 4, 0, 34.8, 0, 58.2, "Tu1", "Rhodemela larix"],
              ["Marine", "+", 4, 4, 0, 25.3, 0, 35.8, "Tu2", "Cryptosiphonia woodii"],
              ["Marine", "+", 4, 4, 5.4, 23.6, 10.88, 47, "Tu3", "Phaestrophion irregulare"],
              ["Marine", "+", 4, 4, 1.8, 10.5, 5.2, 24.2, "Tu4", "Odonthalia floccosa"],
              ["Marine", "+", 4, 4, 0, 10.3, 0, 17.4, "Tu5", "Mirocladia borealis"],
              ["Marine", "+", 4, 4, 0, 8.7, 0, 17, "Tu6", "Fucus distichus"],
              ["Marine", "+", 4, 4, 0, 5.7, 0, 14, "Tu7", "Iridaea heterocarpa"],
              ["Marine", "+", 4, 4, 10.8, 5.4, 15.8, 8.8, "Tu8", "Bossiella plumosa"],
              ["Marine", "+", 4, 4, 21.25, 37.25, 9.54, 22.02, "Du1", "Ralfsia pacifica"],
              ["Marine", "+", 4, 4, 40.25, 20.25, 8.78, 9, "Du2", "Ralfsia pacifica"],
              ["Marine", "+", 5, 5, 15.8445, 11.9533, 10.787, 6.24, "Du3", "Ralfsia pacifica"]]

    data, import_output = import_test_data("gur_hed.txt")
    print_test_output(import_output)
    for c, col in enumerate(data.cols):
        assert col.label == col_headers[c]
    for r, row in enumerate(data.rows):
        for c, col in enumerate(data.cols):
            assert data.value(r, c).value == answer[r][c]


def calc_hedges_d() -> Tuple[MetaWinData, list]:
    data, _ = import_test_data("gur_hed.txt")
    options = EffectSizeOptions()
    options.effect_size = MetaWinEffectFunctions.hedges_d_function()
    options.control_means = data.cols[4]
    options.treatment_means = data.cols[5]
    options.control_sd = data.cols[6]
    options.treatment_sd = data.cols[7]
    options.control_n = data.cols[2]
    options.treatment_n = data.cols[3]
    options.polarity = data.cols[1]
    output, _, _ = do_effect_calculations(data, options, 4)
    return data, output


def test_hedges_d() -> None:
    # answers from MetaWin 2
    answer = [[0.0362, 0.2858],
              [0.7289, 0.3047],
              [0.5651, 0.3466],
              [1.5329, 0.5175],
              [2.0139, 0.4306],
              [1.8799, 0.4806],
              [1.1806, 0.7828],
              [1.3996, 0.8299],
              [1.0889, 0.7655],
              [1.0909, 0.7658],
              [0, 0.4],
              [-0.9171, 0.4421],
              [1.2142, 0.5921],
              [1.6975, 0.1435],
              [1.2709, 0.1202],
              [1.3051, 0.128],
              [1.5213, 0.1289],
              [1.1438, 0.1164],
              [1.2062, 0.1182],
              [3.6961, 1.3538],
              [4.6736, 1.8652],
              [1.218, 0.3387],
              [1.2885, 0.4972],
              [1.8177, 0.1413],
              [2.2233, 0.1618],
              [0.767, 0.1074],
              [0.5239, 0.2069],
              [0.163, 0.2007],
              [0.4487, 0.205],
              [2.2178, 1.6148],
              [0.5707, 1.0407],
              [-0.3254, 1.0132],
              [0.7353, 0.5338],
              [0.8691, 0.5472],
              [0.4639, 0.5135],
              [0.4322, 0.5117],
              [0.728, 0.5331],
              [0.6293, 0.5248],
              [0.5007, 0.5157],
              [-0.3672, 0.5084],
              [0.8199, 0.542],
              [-1.9561, 0.7392],
              [-0.3989, 0.408]]

    data, output = calc_hedges_d()
    print_test_output(output)
    # effect size will be in column 10, variance in column 11
    for r, row in enumerate(data.rows):
        assert round(data.value(r, 10).value, 4) == answer[r][0]
        assert round(data.value(r, 11).value, 4) == answer[r][1]


def calc_ln_response_ratio() -> Tuple[MetaWinData, list]:
    data, _ = import_test_data("gur_hed.txt")
    options = EffectSizeOptions()
    options.effect_size = MetaWinEffectFunctions.ln_rr_function()
    options.control_means = data.cols[4]
    options.treatment_means = data.cols[5]
    options.control_sd = data.cols[6]
    options.treatment_sd = data.cols[7]
    options.control_n = data.cols[2]
    options.treatment_n = data.cols[3]
    options.polarity = data.cols[1]
    output, _, _ = do_effect_calculations(data, options, 4)
    return data, output


def test_ln_response_ratio() -> None:
    # answers from MetaWin 2
    """
    MetaWin 2 calculated the ln response ratio as ln(control) - ln(experiment) rather than ln(control/experiment)
    While these normally would produce the same thing, if both the control and experiment values were negative,
    the MW2 behavior would choke and claim the value was invalid, when in fact the negative signs should cancel out

    Because of this, we only test against values produced by both versions
    """
    answer = [[0.0199, 0.0758],
              [0.3211, 0.0515],
              [None, None],
              [None, None],
              [None, None],
              [None, None],
              [1.2088, 0.7026],
              [None, None],
              [None, None],
              [None, None],
              [0, 0.0599],
              [-0.2392, 0.0225],
              [1.1399, 0.1608],
              [None, None],
              [None, None],
              [1.5072, 0.4254],
              [None, None],
              [None, None],
              [1.303, 0.2828],
              [None, None],
              [None, None],
              [0.3045, 0.0161],
              [3.1676, 4.5598],
              [None, None],
              [None, None],
              [None, None],
              [0.1341, 0.0135],
              [0.2351, 0.4182],
              [None, None],
              [1.6285, 0.4528],
              [None, None],
              [-0.4783, 0.4762],
              [None, None],
              [None, None],
              [1.4748, 2.0064],
              [1.7636, 3.4144],
              [None, None],
              [None, None],
              [None, None],
              [-0.6931, 1.199],
              [0.5613, 0.1377],
              [-0.687, 0.0613],
              [-0.2818, 0.1472]]

    data, output = calc_ln_response_ratio()
    print_test_output(output)
    # effect size will be in column 10, variance in column 11
    for r, row in enumerate(data.rows):
        if (data.value(r, 10) is not None) and answer[r][0] is not None:
            assert round(data.value(r, 10).value, 4) == answer[r][0]
            assert round(data.value(r, 11).value, 4) == answer[r][1]


def test_simple_meta_analysis():
    # answers from MetaWin 2
    qt_answer = 85.9814
    df_answer = 42
    prob_answer = 0.00007
    mean_e_answer = 1.0099
    # lower_ci_answer = 0.8408
    # upper_ci_answer = 1.1789
    sqrt_pool_var_answer = 0.5662
    mean_stud_var_answer = 0.5191

    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.SIMPLE_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.orwin_failsafe = 0.2
    options.rosenthal_failsafe = 0.05
    options.rosenberg_failsafe = 0.05
    options.create_graph = True

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    mean_values = analysis_values.mean_data

    assert round(mean_values.mean, 4) == mean_e_answer
    assert round(analysis_values.qt, 4) == qt_answer
    assert round(analysis_values.df, 4) == df_answer
    assert round(analysis_values.p, 5) == prob_answer
    # assert round(mean_values.lower_ci, 4) == lower_ci_answer
    # assert round(mean_values.upper_ci, 4) == upper_ci_answer
    assert round(math.sqrt(analysis_values.pooled_var), 4) == sqrt_pool_var_answer
    assert round(mean_values.avg_var, 4) == mean_stud_var_answer


def test_simple_meta_analysis_lep():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    qt_answer = 46.55
    df_answer = 24
    prob_answer = 0.00380
    mean_e_answer = 0.3588
    # lower_ci_answer = 0.2659
    # upper_ci_answer = 0.4517
    pooled_answer = 0.0486
    i2_answer = 48.44

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.SIMPLE_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.create_graph = True

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    mean_values = analysis_values.mean_data

    assert round(mean_values.mean, 4) == mean_e_answer
    assert round(analysis_values.qt, 2) == qt_answer
    assert round(analysis_values.df) == df_answer
    assert round(analysis_values.p, 4) == prob_answer
    # assert round(mean_values.lower_ci, 4) == lower_ci_answer
    # assert round(mean_values.upper_ci, 4) == upper_ci_answer
    assert round(analysis_values.pooled_var, 4) == pooled_answer
    assert round(analysis_values.i2, 2) == i2_answer


def test_simple_meta_analysis_lep_randeff():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    qt_answer = 23.01
    df_answer = 24
    prob_answer = 0.519
    mean_e_answer = 0.3308
    # lower_ci_answer = 0.1929
    # upper_ci_answer = 0.4686
    pooled_answer = 0.0486

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.SIMPLE_MA
    options.random_effects = True
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.create_graph = True

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    mean_values = analysis_values.mean_data

    assert round(mean_values.mean, 4) == mean_e_answer
    assert round(analysis_values.qt, 2) == qt_answer
    assert round(analysis_values.df) == df_answer
    assert round(analysis_values.p, 3) == prob_answer
    # assert round(mean_values.lower_ci, 3) == round(lower_ci_answer, 3)
    # assert round(mean_values.upper_ci, 4) == upper_ci_answer
    assert round(analysis_values.pooled_var, 4) == pooled_answer


def test_simple_meta_analysis_random_effects():
    # answers from MetaWin 2
    qt_answer = 47.4908
    df_answer = 42
    prob_answer = 0.25886
    mean_e_answer = 0.9333
    # lower_ci_answer = 0.6736
    # upper_ci_answer = 1.1929
    sqrt_pool_var_answer = 0.5662
    mean_stud_var_answer = 0.5191
    pool_var_answer = 0.3206

    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.SIMPLE_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.random_effects = True
    options.orwin_failsafe = 0.2
    options.rosenthal_failsafe = 0.05
    options.rosenberg_failsafe = 0.05

    output, _, _, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    mean_values = analysis_values.mean_data

    assert round(mean_values.mean, 4) == mean_e_answer
    assert round(analysis_values.qt, 4) == qt_answer
    assert round(analysis_values.df, 4) == df_answer
    assert round(analysis_values.p, 5) == prob_answer
    # assert round(mean_values.lower_ci, 4) == lower_ci_answer
    # assert round(mean_values.upper_ci, 4) == upper_ci_answer
    assert round(math.sqrt(analysis_values.pooled_var), 4) == sqrt_pool_var_answer
    assert round(mean_values.avg_var, 4) == mean_stud_var_answer
    assert round(analysis_values.pooled_var, 4) == pool_var_answer


def test_simple_meta_analysis_lrr():
    # this isn't a true test
    data, _ = calc_ln_response_ratio()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.SIMPLE_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.log_transformed = True

    output, *_ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)


def test_simple_meta_analysis_bootstrap():
    # this isn't a true test
    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.SIMPLE_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.bootstrap_mean = 9999
    options.create_graph = True

    output, figure, chart_data, _ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_group_meta_analysis_lep_suborders():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    group_n_answers = {"Heterocera": 18,  # moths
                       "Rhopalocera": 7}  # butterflies and skippers
    group_mean_answers = {"Heterocera": 0.363,
                          "Rhopalocera": 0.336}
    # group_lower_answers = {"Heterocera": 0.260,
    #                        "Rhopalocera": 0.043}
    # group_upper_answers = {"Heterocera": 0.465,
    #                        "Rhopalocera": 0.628}
    group_q_answers = {"Heterocera (within)": 40.3206,
                       "Rhopalocera (within)": 6.1872}
    group_qp_answers = {"Heterocera (within)": 0.00117,
                        "Rhopalocera (within)": 0.40255}
    model_q_answer = 0.04
    model_p_answer = 0.83400
    model_df_answer = 1
    error_q_answer = 46.51
    error_p_answer = 0.00258
    error_df_answer = 23
    total_q_answer = 46.55
    total_p_answer = 0.00380
    total_df_answer = 24
    pooled_answer = 0.0526

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.GROUPED_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.groups = data.cols[1]
    options.create_graph = True

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    global_values = analysis_values.global_values
    group_mean_values = analysis_values.group_mean_values
    group_het_values = analysis_values.group_het_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values

    for group in group_mean_values:
        assert group.n == group_n_answers[group.name]
        assert round(group.mean, 3) == group_mean_answers[group.name]
        # assert round(group.lower_ci, 3) == group_lower_answers[group.name]
        # assert round(group.upper_ci, 3) == group_upper_answers[group.name]
    for group in group_het_values:
        assert round(group.q, 4) == round(group_q_answers[group.source], 4)
        assert round(group.p_chi, 4) == round(group_qp_answers[group.source], 4)
    assert round(model_het.q, 2) == round(model_q_answer, 2)
    assert model_het.df == model_df_answer
    assert round(model_het.p_chi, 5) == round(model_p_answer, 5)
    assert round(error_het.q, 2) == round(error_q_answer, 2)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 2) == round(total_q_answer, 2)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)
    assert round(global_values.pooled_var, 4) == round(pooled_answer, 4)


def test_group_meta_analysis_lep_suborders_rand_eff():
    model_q_answer = 0.0833
    model_p_answer = 0.77292
    model_df_answer = 1
    error_q_answer = 22.0897
    error_p_answer = 0.51484
    error_df_answer = 23
    total_q_answer = 22.1730
    total_p_answer = 0.56894
    total_df_answer = 24
    pooled_answer = 0.0526

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.GROUPED_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.groups = data.cols[1]
    options.random_effects = True
    options.create_graph = True

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    global_values = analysis_values.global_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values

    assert round(model_het.q, 4) == round(model_q_answer, 4)
    assert model_het.df == model_df_answer
    assert round(model_het.p_chi, 5) == round(model_p_answer, 5)
    assert round(error_het.q, 4) == round(error_q_answer, 4)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 4) == round(total_q_answer, 4)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)
    assert round(global_values.pooled_var, 4) == round(pooled_answer, 4)


def test_group_meta_analysis_lep_families():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    group_n_answers = {"Noctuidae": 6,
                       "Pieridae": 3,
                       "Pyralidae": 4,
                       "Tortricidae": 5,
                       "Papilionidae": 2,
                       "Gelechiidae": 2}
    group_mean_answers = {"Noctuidae": 0.2450,
                          "Pieridae": 0.7304,
                          "Pyralidae": 0.2441,
                          "Tortricidae": 0.3228,
                          "Papilionidae": 0.2358,
                          "Gelechiidae": 0.6515}
    # group_lower_answers = {"Noctuidae": 0.0003,
    #                        "Pieridae": -0.4282,
    #                        "Pyralidae": -0.0635,
    #                        "Tortricidae": 0.0387,
    #                        "Papilionidae": -2.1061,
    #                        "Gelechiidae": -0.7009}
    # group_upper_answers = {"Noctuidae": 0.4897,
    #                        "Pieridae": 1.8891,
    #                        "Pyralidae": 0.5517,
    #                        "Tortricidae": 0.6069,
    #                        "Papilionidae": 2.5778,
    #                        "Gelechiidae": 2.0038}
    group_q_answers = {"Noctuidae (within)": 4.9239,
                       "Pieridae (within)": 3.0609,
                       "Pyralidae (within)": 3.0375,
                       "Tortricidae (within)": 19.1049,
                       "Papilionidae (within)": 0.0018,
                       "Gelechiidae (within)": 2.0062}
    group_qp_answers = {"Noctuidae (within)": 0.425,
                        "Pieridae (within)": 0.216,
                        "Pyralidae (within)": 0.386,
                        "Tortricidae (within)": 0.001,
                        "Papilionidae (within)": 0.966,
                        "Gelechiidae (within)": 0.157}

    model_q_answer = 12.87
    model_p_answer = 0.02463
    model_df_answer = 5
    error_q_answer = 32.14
    error_p_answer = 0.00960
    error_df_answer = 16
    total_q_answer = 45.01
    total_p_answer = 0.00173
    total_df_answer = 21

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.GROUPED_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.groups = data.cols[2]
    options.create_graph = True
    data.cols[2].group_filter = ["Yponomeutidae", "Lycaenidae", "Hesperiidae"]

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    global_values = analysis_values.global_values
    group_mean_values = analysis_values.group_mean_values
    group_het_values = analysis_values.group_het_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values

    for group in group_mean_values:
        assert group.n == group_n_answers[group.name]
        assert round(group.mean, 4) == round(group_mean_answers[group.name], 4)
        # assert round(group.lower_ci, 3) == round(group_lower_answers[group.name], 3)
        # assert round(group.upper_ci, 3) == round(group_upper_answers[group.name], 3)
    for group in group_het_values:
        assert round(group.q, 4) == round(group_q_answers[group.source], 4)
        assert round(group.p_chi, 3) == round(group_qp_answers[group.source], 3)
    assert round(model_het.q, 2) == round(model_q_answer, 2)
    assert model_het.df == model_df_answer
    assert round(model_het.p_chi, 5) == round(model_p_answer, 5)
    assert round(error_het.q, 2) == round(error_q_answer, 2)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 2) == round(total_q_answer, 2)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)


def test_group_meta_analysis_bootstrap():
    # this isn't a true test
    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.GROUPED_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.groups = data.cols[0]
    options.bootstrap_mean = 9999
    options.create_graph = True

    output, figure, chart_data, _ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_group_meta_analysis_lrr():
    # this isn't a true test
    data, _ = calc_ln_response_ratio()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.GROUPED_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.groups = data.cols[0]
    options.log_transformed = True
    options.bootstrap_mean = 9999

    options.create_graph = True

    output, figure, chart_data, _ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_group_meta_analysis_randomization():
    # this isn't a true test
    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.GROUPED_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.groups = data.cols[0]
    options.randomize_model = 9999

    output, *_ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)


def test_cumulative_meta_analysis():
    # this isn't a true test
    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.CUMULATIVE_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.cumulative_order = data.cols[9]

    options.create_graph = True

    output, figure, chart_data, _ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_cumulative_meta_analysis_bootstrap():
    # this isn't a true test
    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.CUMULATIVE_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.cumulative_order = data.cols[9]
    options.bootstrap_mean = 999

    options.create_graph = True

    output, figure, chart_data, _ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_regression_meta_analysis_lep():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    model_q_answer = 9.4576
    model_p_answer = 0.00210
    model_df_answer = 1
    error_q_answer = 36.5623
    error_p_answer = 0.01320
    error_df_answer = 20
    total_q_answer = 46.0199
    total_p_answer = 0.00127
    total_df_answer = 21
    predictor_answers = {"Slope": 0.0059,
                         "Intercept": 0.1161}

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.REGRESSION_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.independent_variable = data.cols[3]
    options.create_graph = True

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    global_values = analysis_values.global_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values
    predictors = analysis_values.predictors

    for x in predictors:
        assert round(x.value, 4) == round(predictor_answers[x.predictor], 4)
    assert round(model_het.q, 4) == round(model_q_answer, 4)
    assert round(model_het.p_chi, 5) == round(model_p_answer, 5)
    assert model_het.df == model_df_answer
    assert round(error_het.q, 4) == round(error_q_answer, 4)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 4) == round(total_q_answer, 4)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)


def test_regression_meta_analysis_lep_randeff():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    model_q_answer = 4.1667
    model_p_answer = 0.04123
    model_df_answer = 1
    error_q_answer = 20.4476
    error_p_answer = 0.43026
    error_df_answer = 20
    total_q_answer = 24.6143
    total_p_answer = 0.26425
    total_df_answer = 21

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.REGRESSION_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.independent_variable = data.cols[3]
    options.random_effects = True
    options.create_graph = True

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    global_values = analysis_values.global_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values

    assert round(model_het.q, 4) == round(model_q_answer, 4)
    assert round(model_het.p_chi, 5) == round(model_p_answer, 5)
    assert model_het.df == model_df_answer
    assert round(error_het.q, 4) == round(error_q_answer, 4)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 4) == round(total_q_answer, 4)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)


def test_complex_meta_analysis_no_ind():
    """
    Test the complex GLM algorithm with no structure; results should be identical to the simple analysis
    """
    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.COMPLEX_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.categorical_vars = []
    options.continuous_vars = []

    output, *_ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)


def test_complex_meta_analysis_lep_simple_regression():
    """
    Test the complex GLM algorithm with a simple regression; results should be identical to the regression
    algorithm
    """
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    model_q_answer = 9.4576
    model_p_answer = 0.00210
    model_df_answer = 1
    error_q_answer = 36.5623
    error_p_answer = 0.01320
    error_df_answer = 20
    total_q_answer = 46.0199
    total_p_answer = 0.00127
    total_df_answer = 21
    predictor_answers = {"β0 (intercept)": 0.1161,
                         "β1 (%Polyandry)": 0.0059}

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.COMPLEX_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.categorical_vars = []
    options.continuous_vars = [data.cols[3]]
    options.create_graph = True

    output, _, _, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    global_values = analysis_values.global_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values
    predictors = analysis_values.predictors

    for x in predictors:
        assert round(x.value, 2) == round(predictor_answers[x.predictor], 2)
    assert round(model_het.q, 4) == round(model_q_answer, 4)
    assert round(model_het.p_chi, 5) == round(model_p_answer, 5)
    assert model_het.df == model_df_answer
    assert round(error_het.q, 4) == round(error_q_answer, 4)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 4) == round(total_q_answer, 4)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)


def test_complex_meta_analysis_lep_group():
    """
    Test the complex GLM algorithm with a simple group struture; results should be identical to the group
    algorithm
    """
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    model_q_answer = 0.04
    model_p_answer = 0.83400
    model_df_answer = 1
    error_q_answer = 46.51
    error_p_answer = 0.00258
    error_df_answer = 23
    total_q_answer = 46.55
    total_p_answer = 0.00380
    total_df_answer = 24

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.COMPLEX_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.categorical_vars = [data.cols[1]]
    options.continuous_vars = []
    options.create_graph = True

    output, _, _, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    global_values = analysis_values.global_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values
    assert round(model_het.q, 2) == round(model_q_answer, 2)
    assert round(model_het.p_chi, 5) == round(model_p_answer, 5)
    assert model_het.df == model_df_answer
    assert round(error_het.q, 2) == round(error_q_answer, 2)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 2) == round(total_q_answer, 2)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)


def test_complex_meta_analysis_lep():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    model_q_answer = 9.4807
    model_p_answer = 0.00874
    model_df_answer = 2
    error_q_answer = 36.5392
    error_p_answer = 0.00906
    error_df_answer = 19
    total_q_answer = 46.0199
    total_p_answer = 0.00127
    total_df_answer = 21
    predictor_answers = {"β0 (intercept)": 0.1235,
                         "β1 (%Polyandry)": 0.0059,
                         "β2 (Suborder)": -0.0106}
    predictor_se = {"β0 (intercept)": 0.1042,
                    "β1 (%Polyandry)": 0.0019,
                    "β2 (Suborder)": 0.0698}
    predictor_p = {"β0 (intercept)": 0.2358,
                   "β1 (%Polyandry)": 0.0021,
                   "β2 (Suborder)": 0.8794}
    pooled_answer = 0.0447

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.COMPLEX_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.categorical_vars = [data.cols[1]]
    options.continuous_vars = [data.cols[3]]
    options.create_graph = True

    output, _, _, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    global_values = analysis_values.global_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values
    predictors = analysis_values.predictors

    for x in predictors:
        # the sign on the categorical predictor is reversed, prob because a different approach was taken to
        # creating the x matrix
        assert round(x.value, 2) == abs(round(predictor_answers[x.predictor], 2))
        assert round(x.se, 3) == round(predictor_se[x.predictor], 3)
        assert round(x.p_norm, 4) == round(predictor_p[x.predictor], 4)
    assert round(model_het.q, 4) == round(model_q_answer, 4)
    assert round(model_het.p_chi, 5) == round(model_p_answer, 5)
    assert model_het.df == model_df_answer
    assert round(error_het.q, 4) == round(error_q_answer, 4)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 4) == round(total_q_answer, 4)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)
    assert round(global_values.pooled_var, 4) == round(pooled_answer, 4)


def test_complex_meta_analysis_lep_randomeff():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    # the se listed for the suborder in part B of Table 9.6 (last line) is wrong; the value listed is actually the
    # variance
    model_q_answer = 4.3074
    model_p_answer = 0.1161
    model_df_answer = 2
    error_q_answer = 19.2236
    error_p_answer = 0.4426
    error_df_answer = 19
    total_q_answer = 23.5310
    total_p_answer = 0.3163
    total_df_answer = 21
    predictor_answers = {"β0 (intercept)": 0.1471,
                         "β1 (%Polyandry)": 0.0056,
                         "β2 (Suborder)": -0.0552}
    predictor_se = {"β0 (intercept)": 0.1419,
                    "β1 (%Polyandry)": 0.0028,
                    "β2 (Suborder)": 0.0919}  # this value was wrong in the chapter
    predictor_p = {"β0 (intercept)": 0.2999,
                   "β1 (%Polyandry)": 0.0444,
                   "β2 (Suborder)": 0.5482}

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.COMPLEX_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.categorical_vars = [data.cols[1]]
    options.continuous_vars = [data.cols[3]]
    options.random_effects = True
    options.create_graph = True

    output, _, _, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    global_values = analysis_values.global_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values
    predictors = analysis_values.predictors

    for x in predictors:
        # the sign on the categorical predictor is reversed, prob because a different approach was taken to
        # creating the x matrix
        assert round(x.value, 2) == abs(round(predictor_answers[x.predictor], 2))
        assert round(x.se, 4) == round(predictor_se[x.predictor], 4)
        assert round(x.p_norm, 2) == round(predictor_p[x.predictor], 2)
    assert round(model_het.q, 4) == round(model_q_answer, 4)
    assert round(model_het.p_chi, 4) == round(model_p_answer, 4)
    assert model_het.df == model_df_answer
    assert round(error_het.q, 4) == round(error_q_answer, 4)
    assert round(error_het.p_chi, 4) == round(error_p_answer, 4)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 4) == round(total_q_answer, 4)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 4) == round(total_p_answer, 4)


def test_complex_meta_analysis_two_cat():

    data, _ = calc_hedges_d()
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.COMPLEX_MA
    options.effect_data = data.cols[10]
    options.effect_vars = data.cols[11]
    options.categorical_vars = [data.cols[0], data.cols[1]]
    options.continuous_vars = [data.cols[2]]

    output, *_ = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)


def test_nested_meta_analysis_lep():
    # answers from Chapter 9, Handbook of Meta-Analysis in Ecology and Evolution
    model_q_answer = {"Qm (Suborder)": 0.07,
                      "Qm (Family)": 12.80}
    model_p_answer = {"Qm (Suborder)": 0.79828,
                      "Qm (Family)": 0.01230}
    model_df_answer = {"Qm (Suborder)": 1,
                       "Qm (Family)": 4}
    error_q_answer = 32.14
    error_p_answer = 0.00960
    error_df_answer = 16
    total_q_answer = 45.01
    total_p_answer = 0.00173
    total_df_answer = 21

    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.NESTED_MA
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.nested_vars = [data.cols[1], data.cols[2]]
    options.create_graph = True
    data.cols[2].group_filter = ["Yponomeutidae", "Lycaenidae", "Hesperiidae"]

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()

    global_values = analysis_values.global_values
    model_het = analysis_values.model_het_values
    error_het = analysis_values.error_het_values

    for m in model_het:
        assert round(m.q, 2) == round(model_q_answer[m.source], 2)
        assert m.df == model_df_answer[m.source]
        assert round(m.p_chi, 4) == round(model_p_answer[m.source], 4)
    assert round(error_het.q, 2) == round(error_q_answer, 2)
    assert round(error_het.p_chi, 5) == round(error_p_answer, 5)
    assert error_het.df == error_df_answer
    assert round(global_values.qt, 2) == round(total_q_answer, 2)
    assert global_values.df == total_df_answer
    assert round(global_values.p, 5) == round(total_p_answer, 5)


def test_tree_import():
    n_answer = 66
    names_answer = ["Megaptera",
                    "Tursiops",
                    "Hippopotamus",
                    "Tragelaphus",
                    "Okapia",
                    "Sus",
                    "Lama",
                    "Ceratotherium",
                    "Tapirus",
                    "Equus",
                    "Felis",
                    "Leopardus",
                    "Panthera",
                    "Canis",
                    "Ursus",
                    "Manis",
                    "Artibeus",
                    "Nycteris",
                    "Pteropus",
                    "Rousettus",
                    "Erinaceus",
                    "Sorex",
                    "Asioscalops",
                    "Condylura",
                    "Cavia",
                    "Hydrochoeris",
                    "Agouti",
                    "Erethizon",
                    "Myocastor",
                    "Dinomys",
                    "Hystrix",
                    "Heterocephalus",
                    "Mus",
                    "Rattus",
                    "Cricetus",
                    "Pedetes",
                    "Castor",
                    "Dipodomys",
                    "Tamias",
                    "Muscardinus",
                    "Sylvilagus",
                    "Ochotona",
                    "Hylobates",
                    "Homo",
                    "Macaca",
                    "Ateles",
                    "Callimico",
                    "Cynocephalus",
                    "Lemur",
                    "Tarsius",
                    "Tupaia",
                    "Choloepus_hoffmanni",
                    "Choloepus_didactylus",
                    "Tamandua",
                    "Myrmechophaga",
                    "Euphractus",
                    "Chaetophractus",
                    "Trichechus",
                    "Loxodonta",
                    "Procavia",
                    "Echinops",
                    "Orycteropus",
                    "Macroscelides",
                    "Elephantulus",
                    "Didelphis",
                    "Macropus"]

    with open("mammal_tree.txt", "r") as infile:
        newick_str = infile.readline()
    tree = MetaWinTree.read_newick_tree(newick_str)

    assert tree.n_tips() == n_answer
    taxa_list = tree.tip_names()
    for i, taxon in enumerate(taxa_list):
        assert taxon == names_answer[i]

    if TEST_FIGURES:
        figure = MetaWinCharts.chart_phylogeny(tree)
        test_win = TestFigureDialog(figure, "imported phylogeny")
        test_win.exec()


def test_scatter_plot():
    data, _ = calc_hedges_d()
    x_col = data.cols[11]
    y_col = data.cols[10]
    if TEST_FIGURES:
        figure, chart_data = MetaWinDraw.draw_scatter_plot(data, x_col, y_col)
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_normal_quantile_plot():
    data, _ = calc_hedges_d()
    e_col = data.cols[10]
    v_col = data.cols[11]
    if TEST_FIGURES:
        figure, chart_data = MetaWinDraw.draw_normal_quantile_plot(data, e_col, v_col)
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_radial_plot_d():
    data, _ = calc_hedges_d()
    e_col = data.cols[10]
    v_col = data.cols[11]
    if TEST_FIGURES:
        figure, chart_data = MetaWinDraw.draw_radial_plot(data, e_col, v_col, False)
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_radial_plot_lnrr():
    data, _ = calc_ln_response_ratio()
    e_col = data.cols[10]
    v_col = data.cols[11]
    if TEST_FIGURES:
        figure, chart_data = MetaWinDraw.draw_radial_plot(data, e_col, v_col, True)
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_histogram_d_unweighted():
    data, _ = calc_hedges_d()
    e_col = data.cols[10]
    v_col = data.cols[11]
    if TEST_FIGURES:
        figure, chart_data = MetaWinDraw.draw_histogram_plot(data, e_col, v_col, 0, 10)
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_histogram_d_weighted_invvar():
    data, _ = calc_hedges_d()
    e_col = data.cols[10]
    v_col = data.cols[11]
    if TEST_FIGURES:
        figure, chart_data = MetaWinDraw.draw_histogram_plot(data, e_col, v_col, 1, 10)
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_histogram_d_weighted_sample_size():
    data, _ = calc_hedges_d()
    e_col = data.cols[10]
    v_col = data.cols[2]
    if TEST_FIGURES:
        figure, chart_data = MetaWinDraw.draw_histogram_plot(data, e_col, v_col, 2, 15)
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_forest_plot():
    data, _ = calc_hedges_d()
    e_col = data.cols[10]
    v_col = data.cols[11]
    if TEST_FIGURES:
        figure, chart_data = MetaWinDraw.draw_forest_plot(data, e_col, v_col)
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_trim_and_fill_analysis():
    """
    funnel_test.txt contains a simulated data set; a true funnel plot was simulated where variance around a true
    mean was dependent on sample size, then points on one side of the funnel were deliberately removed as if
    due to publication bias
    """
    filename = "funnel_test.txt"
    with open(filename, "r") as infile:
        indata = infile.readlines()
        import_options = ImportTextOptions()
        import_options.col_headers = True
        data = split_text_data(indata, import_options)
        convert_strings_to_numbers(data)

    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.TRIM_FILL
    options.effect_data = data.cols[1]
    options.effect_vars = data.cols[0]
    options.create_graph = True
    options.k_estimator = "L"

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_trim_and_fill_analysis_negative_mean():
    """
    reverse the funnel plot to test when the bias applies to the other side of the mean
    """
    filename = "funnel_test.txt"
    with open(filename, "r") as infile:
        indata = infile.readlines()
        import_options = ImportTextOptions()
        import_options.col_headers = True
        data = split_text_data(indata, import_options)
        convert_strings_to_numbers(data)

    for r in range(data.nrows()):
        data.replace_value(r, 1, -data.value(r, 1).value)
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.TRIM_FILL
    options.effect_data = data.cols[1]
    options.effect_vars = data.cols[0]
    options.create_graph = True
    options.k_estimator = "R"

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_tree_functions():
    with open("mammal_tree.txt", "r") as infile:
        newick_str = infile.readline()
    tree = MetaWinTree.read_newick_tree(newick_str)
    tip1 = tree.find_tip_by_name("Homo")
    tip2 = tree.find_tip_by_name("Mus")
    tip3 = tree.find_tip_by_name("Hello, World")

    assert tip1 is not None
    assert tip2 is not None
    assert tip3 is None


def test_jackknife():
    data, _ = import_test_data("lepidoptera.txt")
    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.structure = MetaWinAnalysis.JACKKNIFE
    options.effect_data = data.cols[4]
    options.effect_vars = data.cols[5]
    options.create_graph = True

    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    if TEST_FIGURES:
        test_win = TestFigureDialog(figure, chart_data.caption_text())
        test_win.exec()


def test_phylogenetic_simple_test():
    """
    simple example from chapter 17 of Meta Analysis handbook    
    """
    data, _ = import_test_data("simple_phylo_data.txt")
    with open("simple_phylo_tree.txt", "r") as infile:
        newick_str = infile.read()
    tree = MetaWinTree.read_newick_tree(newick_str)

    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.effect_data = data.cols[1]
    options.effect_vars = data.cols[3]
    options.tip_names = data.cols[0]
    print("UNWEIGHTED")
    options.structure = MetaWinAnalysis.SIMPLE_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    print()
    print()
    print("WEIGHTED")
    options.effect_vars = data.cols[2]
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)

    print()
    print()
    print("PHYLOGENETIC")
    options.structure = MetaWinAnalysis.PHYLOGENETIC_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4, tree=tree)
    print_test_output(output)


def test_phylogenetic_glm_simple():
    data, _ = import_test_data("herbivore_data.txt")
    with open("herbivore_tree.txt", "r") as infile:
        newick_str = infile.read()
    tree = MetaWinTree.read_newick_tree(newick_str)

    options = MetaWinAnalysis.MetaAnalysisOptions()
    options.effect_data = data.cols[1]
    options.effect_vars = data.cols[2]
    options.tip_names = data.cols[0]
    options.random_effects = True

    options.structure = MetaWinAnalysis.SIMPLE_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    options.structure = MetaWinAnalysis.PHYLOGENETIC_MA
    print(data.column_labels()[1])
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4, tree=tree)
    print_test_output(output)

    print()
    print()
    print(20*"-")
    print()
    print(data.column_labels()[3])
    options.effect_data = data.cols[3]
    options.effect_vars = data.cols[4]

    options.structure = MetaWinAnalysis.SIMPLE_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    options.structure = MetaWinAnalysis.PHYLOGENETIC_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4, tree=tree)
    print_test_output(output)

    print()
    print()
    print(20*"-")
    print()
    print(data.column_labels()[5])
    options.effect_data = data.cols[5]
    options.effect_vars = data.cols[6]
    options.structure = MetaWinAnalysis.SIMPLE_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    options.structure = MetaWinAnalysis.PHYLOGENETIC_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4, tree=tree)
    print_test_output(output)

    print()
    print()
    print(20*"-")
    print()
    print(data.column_labels()[7])
    options.effect_data = data.cols[7]
    options.effect_vars = data.cols[8]
    options.structure = MetaWinAnalysis.SIMPLE_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    options.structure = MetaWinAnalysis.PHYLOGENETIC_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4, tree=tree)
    print_test_output(output)

    print()
    print()
    print(20*"-")
    print()
    print(data.column_labels()[9].upper())
    options.effect_data = data.cols[9]
    options.effect_vars = data.cols[10]
    options.structure = MetaWinAnalysis.SIMPLE_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    options.structure = MetaWinAnalysis.PHYLOGENETIC_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4, tree=tree)
    print_test_output(output)

    print()
    print()
    print(20*"-")
    print()
    print(data.column_labels()[11].upper())
    options.effect_data = data.cols[11]
    options.effect_vars = data.cols[12]
    options.structure = MetaWinAnalysis.SIMPLE_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4)
    print_test_output(output)
    options.structure = MetaWinAnalysis.PHYLOGENETIC_MA
    output, figure, chart_data, analysis_values = MetaWinAnalysis.do_meta_analysis(data, options, 4, tree=tree)
    print_test_output(output)
