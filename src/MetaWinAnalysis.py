"""
Module controlling choice selection for primary meta-analytic analyses
"""


from typing import Optional
import webbrowser

from PyQt6.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QGridLayout, QFrame, QComboBox, QGroupBox, \
    QCheckBox, QLineEdit, QRadioButton, QHBoxLayout
from PyQt6.QtGui import QIcon, QIntValidator, QDoubleValidator

from MetaWinData import MetaWinData
import MetaWinConstants
import MetaWinAnalysisFunctions
from MetaWinMessages import report_warning
from MetaWinWidgets import add_ok_cancel_help_button_layout, add_cancel_help_button_layout, add_drag_drop_list, \
    create_list_item, add_effect_choice_to_dialog
from MetaWinUtils import get_citation, create_reference_list
from MetaWinLanguage import get_text


SIMPLE_MA = 0
GROUPED_MA = 1
NESTED_MA = 2
REGRESSION_MA = 3
COMPLEX_MA = 4
CUMULATIVE_MA = 5
PHYLOGENETIC_MA = 6
TRIM_FILL = 7
JACKKNIFE = 8
RANKCOR = 9


class MetaAnalysisOptions:
    def __init__(self):
        self.structure = None
        self.effect_data = None
        self.effect_vars = None
        self.groups = None
        self.cumulative_order = None
        self.independent_variable = None
        self.sample_size = None
        self.tip_names = None
        self.nested_vars = []
        self.categorical_vars = []
        self.continuous_vars = []
        self.random_effects = False
        self.log_transformed = False
        self.bootstrap_mean = None
        self.randomize_model = None
        self.randomize_phylogeny = None
        self.rosenberg_failsafe = None
        self.rosenthal_failsafe = None
        self.orwin_failsafe = None
        self.create_graph = False
        self.k_estimator = "L"
        self.cor_test = "tau"
        self.norm_ci = True

    def report_choices(self):
        output_blocks = []
        citations = []
        if self.structure is not None:
            output = []
            if self.structure == SIMPLE_MA:
                output.append("{}: {}".format(get_text("Structure"), get_text("None")))
                output.append("→ {}: ".format(get_text("Citation")) + get_citation("Hedges_Olkin_1985"))
                citations.append("Hedges_Olkin_1985")
            elif self.structure == GROUPED_MA:
                output.append("{}: {}".format(get_text("Structure"), get_text("Grouped")))
                tmpstr = "→ {}: ".format(get_text("Citation")) + get_citation("Hedges_Olkin_1985")
                citations.append("Hedges_Olkin_1985")
                if self.random_effects:
                    tmpstr = "→ {}: ".format(get_text("Citations")) + get_citation("Hedges_Olkin_1985") + ", " + \
                             get_citation("Gurevitch_Heges_1993")
                    citations.append("Gurevitch_Heges_1993")
                output.append(tmpstr)
            elif self.structure == REGRESSION_MA:
                output.append("{}: {}".format(get_text("Structure"), get_text("Linear Regression")))
                tmpstr = "→ {}: ".format(get_text("Citations")) + get_citation("Hedges_Olkin_1985") + ", " + \
                         get_citation("Greenland_1987")
                citations.append("Hedges_Olkin_1985")
                citations.append("Greenland_1987")
                if self.random_effects:
                    tmpstr += ", " + get_citation("Rosenberg_et_2000")
                    citations.append("Rosenberg_et_2000")
                output.append(tmpstr)
            elif self.structure == CUMULATIVE_MA:
                output.append(get_text("Cumulative Meta-Analysis"))
                output.append("→ {}: ".format(get_text("Citation")) + get_citation("Chalmers_1991"))
                citations.append("Chalmers_1991")
            elif self.structure == COMPLEX_MA:
                output.append("{}: {}".format(get_text("Structure"), get_text("Complex/GLM")))
                output.append("→ {}: ".format(get_text("Citations")) + get_citation("Hedges_Olkin_1985") + ", " +
                              get_citation("Rosenberg_et_2000"))
                citations.append("Hedges_Olkin_1985")
                citations.append("Rosenberg_et_2000")
            elif self.structure == NESTED_MA:
                output.append("{}: {}".format(get_text("Structure"), get_text("Nested Groups")))
                output.append("→ {}: ".format(get_text("Citation")) + get_citation("Rosenberg_2013"))
                citations.append("Rosenberg_2013")
            elif self.structure == TRIM_FILL:
                output.append(get_text("Trim and Fill Analysis"))
                output.append("→ {}: ".format(get_text("Citations")) + get_citation("Duval_Tweedie_2000a") + ", " +
                              get_citation("Duval_Tweedie_2000b"))
                citations.append("Duval_Tweedie_2000a")
                citations.append("Duval_Tweedie_2000b")
            elif self.structure == JACKKNIFE:
                output.append(get_text("Jackknife Meta-Analysis"))
            elif self.structure == PHYLOGENETIC_MA:
                output.append(get_text("Phylogenetic GLM Meta-Analysis"))
                output.append("→ {}: ".format(get_text("Citations")) + get_citation("Lajeunesse_2009") + ", " +
                              get_citation("Lajeunesse_et_2013"))
                citations.append("Lajeunesse_2009")
                citations.append("Lajeunesse_et_2013")
            elif self.structure == RANKCOR:
                output.append(get_text("Rank Correlation Analysis"))
                output.append("→ {}: ".format(get_text("Citations")) + get_citation("Begg_1994") + ", " +
                              get_citation("Begg_Mazumdar_1994"))
                citations.append("Begg_1994")
                citations.append("Begg_Mazumdar_1994")

            output_blocks.append(output)

            output = ["→ {}: ".format(get_text("Effect Sizes")) + self.effect_data.label,
                      "→ {}: ".format(get_text("Effect Size Variances")) + self.effect_vars.label]
            if self.structure == GROUPED_MA:
                output.append("→ {}: ".format(get_text("Groups")) + self.groups.label)
            elif self.structure == CUMULATIVE_MA:
                output.append("→ {}: ".format(get_text("Cumulative Order")) + self.cumulative_order.label)
            elif self.structure == REGRESSION_MA:
                output.append("→ {}: ".format(get_text("Independent Variable")) + self.independent_variable.label)
            elif (self.structure == COMPLEX_MA) or (self.structure == PHYLOGENETIC_MA):
                if len(self.categorical_vars) > 0:
                    cat_labels = [x.label for x in self.categorical_vars]
                    output.append("→ {}: ".format(get_text("Categorical Independent Variables(s)")) +
                                  ", ".join(cat_labels))
                if len(self.continuous_vars) > 0:
                    cont_labels = [x.label for x in self.continuous_vars]
                    output.append("→ {}: ".format(get_text("Continuous Independent Variables(s)")) +
                                  ", ".join(cont_labels))
            elif self.structure == NESTED_MA:
                nest_labels = [x.label for x in self.nested_vars]
                output.append("→ {}: ".format(get_text("Nested Variables (top to bottom)")) + ", ".join(nest_labels))
            elif self.structure == TRIM_FILL:
                output.append("→ {}: {}<sub>0</sub>".format(get_text("Estimator of Missing Studies"),
                                                            self.k_estimator))
            elif self.structure == RANKCOR:
                if self.cor_test == "tau":
                    output.append("→ {}: {}".format(get_text("Rank Correlation Method"), "Kendall's &tau;"))
                    output.append("→ {}: ".format(get_text("Citation")) + get_citation("Kendall_1938"))
                    citations.append("Kendall_1938")
                else:
                    output.append("→ {}: {}".format(get_text("Estimator of Missing Studies"), "Spearman's &rho;"))
                    output.append("→ {}: ".format(get_text("Citation")) + get_citation("Spearman_1904"))
                    citations.append("Spearman_1904")

            if self.structure == PHYLOGENETIC_MA:
                output.append("→ {}: ".format(get_text("Phylogeny Tip Names")) + self.tip_names.label)

            if self.random_effects:
                if self.structure == GROUPED_MA:
                    ostr = "→ {}".format(get_text("Random (Mixed) Effects Model"))
                else:
                    ostr = "→ {}".format(get_text("Random Effects Model"))
                output.append(ostr)
            else:
                output.append("→ {}".format(get_text("Fixed Effects Model")))
            output_blocks.append(output)

            output = []
            if self.norm_ci:
                output.append("→ {}".format(get_text("ci from norm")))
            else:
                output.append("→ {}".format(get_text("ci from t")))
            if self.bootstrap_mean is not None:
                output.extend(["→ {}: {} {}".format(get_text("Use bootstrap for confidence intervals around means"),
                                                    self.bootstrap_mean, get_text("iterations")),
                               "→ {}: ".format(get_text("Citations")) + get_citation("Adams_et_1997") + ", " +
                               get_citation("Dixon_1993")])
                # output_blocks.append(["→ {}: {} {}".format(get_text("Use bootstrap for confidence intervals around "
                #                                                     "means"), self.bootstrap_mean,
                #                                            get_text("iterations")),
                #                       "→ {}: ".format(get_text("Citations")) + get_citation("Adams_et_1997") + ", " +
                #                       get_citation("Dixon_1993")])
                citations.append("Adams_et_1997")
                citations.append("Dixon_1993")
            output_blocks.append(output)

            if self.structure == RANKCOR:
                output_blocks.append(["→ {}: {} {}".format(get_text("Randomization to test correlation"),
                                                           self.randomize_model, get_text("iterations"))])
            elif self.randomize_model is not None:
                output_blocks.append(["→ {}: {} {}".format(get_text("Use randomization to test model structure"),
                                                           self.randomize_model, get_text("iterations")),
                                      "→ {}: ".format(get_text("Citation")) + get_citation("Adams_et_1997")])
                citations.append("Adams_et_1997")
            if self.randomize_phylogeny is not None:
                output_blocks.append(["→ {}: {} {}".format(get_text("Use randomization to test phylogenentic "
                                                                    "structure"), self.randomize_phylogeny,
                                                           get_text("iterations"))])

        return output_blocks, citations


class MetaAnalysisStructureDialog(QDialog):
    """
    Dialog for choosing primary analysis to perform
    """
    def __init__(self, options: MetaAnalysisOptions, tree):
        super().__init__()
        self.help = MetaWinConstants.help_index["analyses"]
        self.__options = options
        self.init_ui(tree)

    def init_ui(self, tree):
        analysis_layout = QVBoxLayout()
        simple_button = QPushButton(get_text("Basic Meta-Analysis"))
        simple_button.clicked.connect(self.simple_button_click)
        analysis_layout.addWidget(simple_button)

        rank_cor_button = QPushButton(get_text("Rank Correlation Analysis"))
        rank_cor_button.clicked.connect(self.rank_cor_button_click)
        analysis_layout.addWidget(rank_cor_button)

        trim_fill_button = QPushButton(get_text("Trim and Fill Analysis"))
        trim_fill_button.clicked.connect(self.trim_fill_button_click)
        analysis_layout.addWidget(trim_fill_button)
        jackknife_button = QPushButton(get_text("Jackknife Meta-Analysis"))
        jackknife_button.clicked.connect(self.jackknife_button_click)
        analysis_layout.addWidget(jackknife_button)
        cumulative_button = QPushButton(get_text("Cumulative Meta-Analysis"))
        cumulative_button.clicked.connect(self.cumulative_button_click)
        analysis_layout.addWidget(cumulative_button)
        grouped_button = QPushButton(get_text("Grouped Meta-Analysis"))
        grouped_button.clicked.connect(self.grouped_button_click)
        analysis_layout.addWidget(grouped_button)
        nested_button = QPushButton(get_text("Nested Group Analysis"))
        nested_button.clicked.connect(self.nested_button_click)
        analysis_layout.addWidget(nested_button)
        regression_button = QPushButton(get_text("Linear Meta-Regression Analysis"))
        regression_button.clicked.connect(self.regression_button_click)
        analysis_layout.addWidget(regression_button)
        complex_button = QPushButton(get_text("Complex/GLM Meta-Analysis"))
        complex_button.clicked.connect(self.complex_button_click)
        analysis_layout.addWidget(complex_button)
        tree_button = QPushButton(get_text("Phylogenetic GLM Meta-Analysis"))
        tree_button.clicked.connect(self.tree_button_click)
        analysis_layout.addWidget(tree_button)
        if tree is None:
            tree_button.setEnabled(False)

        button_layout = add_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Choose an Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(analysis_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def simple_button_click(self):
        self.__options.structure = SIMPLE_MA
        self.accept()

    def grouped_button_click(self):
        self.__options.structure = GROUPED_MA
        self.accept()

    def nested_button_click(self):
        self.__options.structure = NESTED_MA
        self.accept()

    def regression_button_click(self):
        self.__options.structure = REGRESSION_MA
        self.accept()

    def complex_button_click(self):
        self.__options.structure = COMPLEX_MA
        self.accept()

    def cumulative_button_click(self):
        self.__options.structure = CUMULATIVE_MA
        self.accept()

    def tree_button_click(self):
        self.__options.structure = PHYLOGENETIC_MA
        self.accept()

    def trim_fill_button_click(self):
        self.__options.structure = TRIM_FILL
        self.accept()

    def jackknife_button_click(self):
        self.__options.structure = JACKKNIFE
        self.accept()

    def rank_cor_button_click(self):
        self.__options.structure = RANKCOR
        self.accept()


class MetaAnalysisSimpleStructureDialog(QDialog):
    """
    Dialog for choosing options for a simple meta-analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["basic_analysis"]
        self.effect_size_box = None
        self.variance_box = None
        self.columns = None
        self.random_effects_checkbox = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Basic Meta-Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(self.log_transform_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(self.random_effects_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Basic Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.log_transformed = self.log_transform_box.isChecked()


class MetaAnalysisSimpleStructureExtraDialog(QDialog):
    """
    Dialog for choosing extra options for a simple meta-analysis
    """
    def __init__(self):
        super().__init__()
        self.bootstrap_checkbox = None
        self.bootstrap_n_label = None
        self.bootstrap_n_box = None
        self.rosenberg_checkbox = None
        self.rosenberg_label = None
        self.rosenberg_alpha_box = None
        self.rosenthal_checkbox = None
        self.rosenthal_label = None
        self.rosenthal_alpha_box = None
        self.orwin_checkbox = None
        self.orwin_label = None
        self.orwin_alpha_box = None
        self.graph_checkbox = None
        self.help = MetaWinConstants.help_index["basic_analysis"]
        self.init_ui()

    def init_ui(self):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        options_label = QLabel(get_text("Additional Options"))
        options_label.setStyleSheet(MetaWinConstants.title_label_style)

        randomization_group = add_resampling_options_to_dialog(self, False)

        self.graph_checkbox = QCheckBox(get_text("Graph Effect Sizes and Mean (Forest Plot)"))

        # fail-safe tests
        failsafe_group = QGroupBox(get_text("Failsafe Tests"))
        failsafe_layout = QGridLayout()
        self.rosenberg_checkbox = QCheckBox("Rosenberg Failsafe Calculation")
        self.rosenberg_checkbox.clicked.connect(self.click_rosenberg_checkbox)
        failsafe_layout.addWidget(self.rosenberg_checkbox, 0, 0, 1, 2)
        self.rosenberg_label = QLabel("alpha")
        failsafe_layout.addWidget(self.rosenberg_label, 1, 0)
        self.rosenberg_alpha_box = QLineEdit()
        self.rosenberg_alpha_box.setText("0.05")
        self.rosenberg_alpha_box.setValidator(QDoubleValidator(0.001, 1, 3))
        failsafe_layout.addWidget(self.rosenberg_alpha_box, 1, 1)
        failsafe_group.setLayout(failsafe_layout)
        self.click_rosenberg_checkbox()

        self.rosenthal_checkbox = QCheckBox("Rosenthal Failsafe Calculation")
        self.rosenthal_checkbox.clicked.connect(self.click_rosenthal_checkbox)
        failsafe_layout.addWidget(self.rosenthal_checkbox, 2, 0, 1, 2)
        self.rosenthal_label = QLabel("alpha")
        failsafe_layout.addWidget(self.rosenthal_label, 3, 0)
        self.rosenthal_alpha_box = QLineEdit()
        self.rosenthal_alpha_box.setText("0.05")
        self.rosenthal_alpha_box.setValidator(QDoubleValidator(0.001, 1, 3))
        failsafe_layout.addWidget(self.rosenthal_alpha_box, 3, 1)
        failsafe_group.setLayout(failsafe_layout)
        self.click_rosenthal_checkbox()

        self.orwin_checkbox = QCheckBox("Orwin Failsafe Calculation")
        self.orwin_checkbox.clicked.connect(self.click_orwin_checkbox)
        failsafe_layout.addWidget(self.orwin_checkbox, 4, 0, 1, 2)
        self.orwin_label = QLabel(get_text("minimal effect size"))
        failsafe_layout.addWidget(self.orwin_label, 5, 0)
        self.orwin_alpha_box = QLineEdit()
        self.orwin_alpha_box.setText("0.20")
        self.orwin_alpha_box.setValidator(QDoubleValidator(-10, 10, 3))
        failsafe_layout.addWidget(self.orwin_alpha_box, 5, 1)
        failsafe_group.setLayout(failsafe_layout)
        self.click_orwin_checkbox()

        options_layout = QVBoxLayout()
        options_layout.addWidget(randomization_group)
        options_layout.addWidget(failsafe_group)
        options_layout.addWidget(self.graph_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(options_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Basic Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_bootstrap_checkbox(self):
        if self.bootstrap_checkbox.isChecked():
            self.bootstrap_n_label.setEnabled(True)
            self.bootstrap_n_box.setEnabled(True)
        else:
            self.bootstrap_n_label.setEnabled(False)
            self.bootstrap_n_box.setEnabled(False)

    def click_rosenberg_checkbox(self):
        if self.rosenberg_checkbox.isChecked():
            self.rosenberg_label.setEnabled(True)
            self.rosenberg_alpha_box.setEnabled(True)
        else:
            self.rosenberg_label.setEnabled(False)
            self.rosenberg_alpha_box.setEnabled(False)

    def click_rosenthal_checkbox(self):
        if self.rosenthal_checkbox.isChecked():
            self.rosenthal_label.setEnabled(True)
            self.rosenthal_alpha_box.setEnabled(True)
        else:
            self.rosenthal_label.setEnabled(False)
            self.rosenthal_alpha_box.setEnabled(False)

    def click_orwin_checkbox(self):
        if self.orwin_checkbox.isChecked():
            self.orwin_label.setEnabled(True)
            self.orwin_alpha_box.setEnabled(True)
        else:
            self.orwin_label.setEnabled(False)
            self.orwin_alpha_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        if self.bootstrap_checkbox.isChecked():
            options.bootstrap_mean = int(self.bootstrap_n_box.text())
        else:
            options.bootstrap_mean = None
        if self.rosenberg_checkbox.isChecked():
            options.rosenberg_failsafe = float(self.rosenberg_alpha_box.text())
        else:
            options.rosenberg_failsafe = None
        if self.rosenthal_checkbox.isChecked():
            options.rosenthal_failsafe = float(self.rosenthal_alpha_box.text())
        else:
            options.rosenthal_failsafe = None
        if self.orwin_checkbox.isChecked():
            options.orwin_failsafe = float(self.orwin_alpha_box.text())
        else:
            options.orwin_failsafe = None
        options.create_graph = self.graph_checkbox.isChecked()


class MetaAnalysisGroupedStructureDialog(QDialog):
    """
    Dialog for choosing options for a grouped/categorical meta-analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["grouped_analysis"]
        self.effect_size_box = None
        self.variance_box = None
        self.group_box = None
        self.columns = None
        self.random_effects_checkbox = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Grouped Meta-Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        group_label = QLabel(get_text("Groups"))
        self.group_box = QComboBox()
        for col in self.columns:
            self.group_box.addItem(col.label)

        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(self.log_transform_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(group_label)
        options_layout.addWidget(self.group_box)
        options_layout.addWidget(self.random_effects_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Grouped Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.groups = self.columns[self.group_box.currentIndex()]
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.log_transformed = self.log_transform_box.isChecked()


class MetaAnalysisGroupStructureExtraDialog(QDialog):
    """
    Dialog for choosing extra options for a grouped/categorical meta-analysis
    """
    def __init__(self):
        super().__init__()
        self.bootstrap_checkbox = None
        self.bootstrap_n_label = None
        self.bootstrap_n_box = None
        self.randomize_checkbox = None
        self.randomize_n_label = None
        self.randomize_n_box = None
        self.graph_checkbox = None
        self.help = MetaWinConstants.help_index["grouped_analysis"]
        self.init_ui()

    def init_ui(self):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        options_label = QLabel(get_text("Additional Options"))
        options_label.setStyleSheet(MetaWinConstants.title_label_style)

        randomization_group = add_resampling_options_to_dialog(self, True)

        self.graph_checkbox = QCheckBox(get_text("Graph Mean Effect Sizes (Forest Plot)"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(randomization_group)
        options_layout.addWidget(self.graph_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(options_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Grouped Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_bootstrap_checkbox(self):
        if self.bootstrap_checkbox.isChecked():
            self.bootstrap_n_label.setEnabled(True)
            self.bootstrap_n_box.setEnabled(True)
        else:
            self.bootstrap_n_label.setEnabled(False)
            self.bootstrap_n_box.setEnabled(False)

    def click_randomize_checkbox(self):
        if self.randomize_checkbox.isChecked():
            self.randomize_n_label.setEnabled(True)
            self.randomize_n_box.setEnabled(True)
        else:
            self.randomize_n_label.setEnabled(False)
            self.randomize_n_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        if self.bootstrap_checkbox.isChecked():
            options.bootstrap_mean = int(self.bootstrap_n_box.text())
        else:
            options.bootstrap_mean = None
        if self.randomize_checkbox.isChecked():
            options.randomize_model = int(self.randomize_n_box.text())
        else:
            options.randomize_model = None
        options.create_graph = self.graph_checkbox.isChecked()


class MetaAnalysisCumulativeStructureDialog(QDialog):
    """
    Dialog for choosing options for a cumulative meta-analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["cumulative_analysis"]
        self.effect_size_box = None
        self.variance_box = None
        self.cumulative_box = None
        self.columns = None
        self.random_effects_checkbox = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Cumulative Meta-Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        cumulative_label = QLabel(get_text("Cumulative Order"))
        self.cumulative_box = QComboBox()
        for col in self.columns:
            self.cumulative_box.addItem(col.label)

        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(self.log_transform_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(cumulative_label)
        options_layout.addWidget(self.cumulative_box)
        options_layout.addWidget(self.random_effects_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Cumulative Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.cumulative_order = self.columns[self.cumulative_box.currentIndex()]
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.log_transformed = self.log_transform_box.isChecked()


class MetaAnalysisCumulativeStructureExtraDialog(QDialog):
    """
    Dialog for choosing extra options for a cumulative meta-analysis
    """
    def __init__(self):
        super().__init__()
        self.bootstrap_checkbox = None
        self.bootstrap_n_label = None
        self.bootstrap_n_box = None
        self.graph_checkbox = None
        self.help = MetaWinConstants.help_index["cumulative_analysis"]
        self.init_ui()

    def init_ui(self):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        options_label = QLabel(get_text("Additional Options"))
        options_label.setStyleSheet(MetaWinConstants.title_label_style)

        randomization_group = add_resampling_options_to_dialog(self, False)

        self.graph_checkbox = QCheckBox(get_text("Graph Cumulative Mean Effect (Forest Plot)"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(randomization_group)
        options_layout.addWidget(self.graph_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(options_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Cumulative Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_bootstrap_checkbox(self):
        if self.bootstrap_checkbox.isChecked():
            self.bootstrap_n_label.setEnabled(True)
            self.bootstrap_n_box.setEnabled(True)
        else:
            self.bootstrap_n_label.setEnabled(False)
            self.bootstrap_n_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        if self.bootstrap_checkbox.isChecked():
            options.bootstrap_mean = int(self.bootstrap_n_box.text())
        else:
            options.bootstrap_mean = None
        options.create_graph = self.graph_checkbox.isChecked()


class MetaAnalysisLinearStructureDialog(QDialog):
    """
    Dialog for choosing options for a simple regression meta-analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["linear_analysis"]
        self.effect_size_box = None
        self.variance_box = None
        self.ind_var_box = None
        self.columns = None
        self.random_effects_checkbox = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Linear Meta-Regression Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        ind_var_label = QLabel(get_text("Independent Variable"))
        self.ind_var_box = QComboBox()
        for col in self.columns:
            self.ind_var_box.addItem(col.label)

        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(self.log_transform_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(ind_var_label)
        options_layout.addWidget(self.ind_var_box)
        options_layout.addWidget(self.random_effects_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Linear Meta-Regression Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.independent_variable = self.columns[self.ind_var_box.currentIndex()]
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.log_transformed = self.log_transform_box.isChecked()


class MetaAnalysisLinearStructureExtraDialog(QDialog):
    """
    Dialog for choosing extra options for a simple regression meta-analysis
    """
    def __init__(self):
        super().__init__()
        self.bootstrap_checkbox = None
        self.bootstrap_n_label = None
        self.bootstrap_n_box = None
        self.randomize_checkbox = None
        self.randomize_n_label = None
        self.randomize_n_box = None
        self.graph_checkbox = None
        self.help = MetaWinConstants.help_index["linear_analysis"]
        self.init_ui()

    def init_ui(self):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        options_label = QLabel(get_text("Additional Options"))
        options_label.setStyleSheet(MetaWinConstants.title_label_style)

        randomization_group = add_resampling_options_to_dialog(self, True)

        self.graph_checkbox = QCheckBox(get_text("Graph Regression"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(randomization_group)
        options_layout.addWidget(self.graph_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(options_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Linear Meta-Regression Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_bootstrap_checkbox(self):
        if self.bootstrap_checkbox.isChecked():
            self.bootstrap_n_label.setEnabled(True)
            self.bootstrap_n_box.setEnabled(True)
        else:
            self.bootstrap_n_label.setEnabled(False)
            self.bootstrap_n_box.setEnabled(False)

    def click_randomize_checkbox(self):
        if self.randomize_checkbox.isChecked():
            self.randomize_n_label.setEnabled(True)
            self.randomize_n_box.setEnabled(True)
        else:
            self.randomize_n_label.setEnabled(False)
            self.randomize_n_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        if self.bootstrap_checkbox.isChecked():
            options.bootstrap_mean = int(self.bootstrap_n_box.text())
        else:
            options.bootstrap_mean = None
        if self.randomize_checkbox.isChecked():
            options.randomize_model = int(self.randomize_n_box.text())
        else:
            options.randomize_model = None
        options.create_graph = self.graph_checkbox.isChecked()


class MetaAnalysisComplexStructureDialog(QDialog):
    """
    Dialog for choosing options for a complex GLM meta-analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["glm_analysis"]
        self.effect_size_box = None
        self.variance_box = None
        self.cat_box = None
        self.cont_box = None
        self.columns = None
        self.random_effects_checkbox = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, ok_button = add_ok_cancel_help_button_layout(self)
        ok_button.clicked.disconnect()
        ok_button.clicked.connect(self.click_ok_button)

        analysis_label = QLabel(get_text("Complex/GLM Meta-Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        ind_group_box = QGroupBox(get_text("Independent Variables"))
        ind_layout = QGridLayout()
        unused_label = QLabel(get_text("Unused"))
        cat_var_label = QLabel(get_text("Categorical Variables"))
        cont_var_label = QLabel(get_text("Continuous Variables"))
        unused_box = add_drag_drop_list()
        self.cat_box = add_drag_drop_list()
        self.cont_box = add_drag_drop_list()
        for col in self.columns:
            unused_box.addItem(create_list_item(col))

        drag_label = QLabel(get_text("Drag and drop variables to indicate desired structure"))
        ind_layout.addWidget(unused_label, 0, 0)
        ind_layout.addWidget(cat_var_label, 0, 1)
        ind_layout.addWidget(cont_var_label, 0, 2)
        ind_layout.addWidget(unused_box, 1, 0)
        ind_layout.addWidget(self.cat_box, 1, 1)
        ind_layout.addWidget(self.cont_box, 1, 2)
        ind_layout.addWidget(drag_label, 2, 0, 1, 3)
        ind_group_box.setLayout(ind_layout)

        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(self.log_transform_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(ind_group_box)
        options_layout.addWidget(self.random_effects_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Complex/GLM Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_ok_button(self):
        e = self.columns[self.effect_size_box.currentIndex()]
        cats = [self.cat_box.item(i).column for i in range(self.cat_box.count())]
        conts = [self.cont_box.item(i).column for i in range(self.cont_box.count())]
        if (e in cats) or (e in conts):
            report_warning(self, get_text("Invalid Choices"), get_text("effect_size_ind_error"))
        else:
            self.accept()

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.categorical_vars = [self.cat_box.item(i).column for i in range(self.cat_box.count())]
        options.continuous_vars = [self.cont_box.item(i).column for i in range(self.cont_box.count())]
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.log_transformed = self.log_transform_box.isChecked()


class MetaAnalysisComplexStructureExtraDialog(QDialog):
    """
    Dialog for choosing extra options for a complex GLM meta-analysis
    """
    def __init__(self):
        super().__init__()
        self.bootstrap_checkbox = None
        self.bootstrap_n_label = None
        self.bootstrap_n_box = None
        self.randomize_checkbox = None
        self.randomize_n_label = None
        self.randomize_n_box = None
        self.help = MetaWinConstants.help_index["glm_analysis"]
        self.init_ui()

    def init_ui(self):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        options_label = QLabel(get_text("Additional Options"))
        options_label.setStyleSheet(MetaWinConstants.title_label_style)

        randomization_group = add_resampling_options_to_dialog(self, True)

        options_layout = QVBoxLayout()
        options_layout.addWidget(randomization_group)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(options_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Complex/GLM Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_bootstrap_checkbox(self):
        if self.bootstrap_checkbox.isChecked():
            self.bootstrap_n_label.setEnabled(True)
            self.bootstrap_n_box.setEnabled(True)
        else:
            self.bootstrap_n_label.setEnabled(False)
            self.bootstrap_n_box.setEnabled(False)

    def click_randomize_checkbox(self):
        if self.randomize_checkbox.isChecked():
            self.randomize_n_label.setEnabled(True)
            self.randomize_n_box.setEnabled(True)
        else:
            self.randomize_n_label.setEnabled(False)
            self.randomize_n_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        if self.bootstrap_checkbox.isChecked():
            options.bootstrap_mean = int(self.bootstrap_n_box.text())
        else:
            options.bootstrap_mean = None
        if self.randomize_checkbox.isChecked():
            options.randomize_model = int(self.randomize_n_box.text())
        else:
            options.randomize_model = None


class MetaAnalysisNestedStructureDialog(QDialog):
    """
    Dialog for choosing options for a nested meta-analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["nested_analysis"]
        self.effect_size_box = None
        self.variance_box = None
        self.nest_box = None
        self.columns = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, ok_button = add_ok_cancel_help_button_layout(self)
        ok_button.clicked.disconnect()
        ok_button.clicked.connect(self.click_ok_button)

        analysis_label = QLabel(get_text("Nested Group Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        ind_group_box = QGroupBox(get_text("Independent Variables"))
        ind_layout = QGridLayout()
        unused_label = QLabel(get_text("Unused"))
        nest_var_label = QLabel(get_text("Nested Variables"))
        unused_box = add_drag_drop_list()
        self.nest_box = add_drag_drop_list()
        for col in self.columns:
            unused_box.addItem(create_list_item(col))

        drag_label = QLabel(get_text("drag_nesting"))
        ind_layout.addWidget(unused_label, 0, 0)
        ind_layout.addWidget(nest_var_label, 0, 1)
        ind_layout.addWidget(unused_box, 1, 0)
        ind_layout.addWidget(self.nest_box, 1, 1)
        ind_layout.addWidget(drag_label, 2, 0, 1, 2)
        ind_group_box.setLayout(ind_layout)

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(self.log_transform_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(ind_group_box)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Nested Group Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_ok_button(self):
        if self.nest_box.count() < 2:
            report_warning(self, get_text("Invalid Choices"), get_text("nest_structure_error"))
        else:
            e = self.columns[self.effect_size_box.currentIndex()]
            cats = [self.nest_box.item(i).column for i in range(self.nest_box.count())]
            if e in cats:
                report_warning(self, get_text("Invalid Choices"), get_text("effect_size_ind_error"))
            else:
                self.accept()

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.nested_vars = [self.nest_box.item(i).column for i in range(self.nest_box.count())]
        options.log_transformed = self.log_transform_box.isChecked()


class MetaAnalysisNestedStructureExtraDialog(QDialog):
    """
    Dialog for choosing extra options for a nested meta-analysis
    """
    def __init__(self):
        super().__init__()
        self.bootstrap_checkbox = None
        self.bootstrap_n_label = None
        self.bootstrap_n_box = None
        self.randomize_checkbox = None
        self.randomize_n_label = None
        self.randomize_n_box = None
        self.graph_checkbox = None
        self.help = MetaWinConstants.help_index["nested_analysis"]
        self.init_ui()

    def init_ui(self):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        options_label = QLabel(get_text("Additional Options"))
        options_label.setStyleSheet(MetaWinConstants.title_label_style)

        randomization_group = add_resampling_options_to_dialog(self, True)
        self.graph_checkbox = QCheckBox(get_text("Graph Mean Effect Sizes (Forest Plot)"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(randomization_group)
        options_layout.addWidget(self.graph_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(options_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Nested Group Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_bootstrap_checkbox(self):
        if self.bootstrap_checkbox.isChecked():
            self.bootstrap_n_label.setEnabled(True)
            self.bootstrap_n_box.setEnabled(True)
        else:
            self.bootstrap_n_label.setEnabled(False)
            self.bootstrap_n_box.setEnabled(False)

    def click_randomize_checkbox(self):
        if self.randomize_checkbox.isChecked():
            self.randomize_n_label.setEnabled(True)
            self.randomize_n_box.setEnabled(True)
        else:
            self.randomize_n_label.setEnabled(False)
            self.randomize_n_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        if self.bootstrap_checkbox.isChecked():
            options.bootstrap_mean = int(self.bootstrap_n_box.text())
        else:
            options.bootstrap_mean = None
        if self.randomize_checkbox.isChecked():
            options.randomize_model = int(self.randomize_n_box.text())
        else:
            options.randomize_model = None
        options.create_graph = self.graph_checkbox.isChecked()


class MetaAnalysisTrimFillDialog(QDialog):
    """
    Dialog for choosing options for a trim and fill analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["trim_fill"]
        self.effect_size_box = None
        self.variance_box = None
        self.columns = None
        self.random_effects_checkbox = None
        self.log_transform_box = None
        self.graph_checkbox = None
        self.r_button = None
        self.l_button = None
        self.q_button = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Trim and Fill Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(self.log_transform_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(self.random_effects_checkbox)

        missing_box = QGroupBox(get_text("Estimator of Missing Studies"))
        missing_layout = QHBoxLayout()
        self.r_button = QRadioButton("R0")
        self.l_button = QRadioButton("L0")
        self.q_button = QRadioButton("Q0")
        missing_layout.addWidget(self.r_button)
        missing_layout.addWidget(self.l_button)
        missing_layout.addWidget(self.q_button)
        missing_box.setLayout(missing_layout)
        self.l_button.setChecked(True)

        self.graph_checkbox = QCheckBox(get_text("Graph Trim and Fill Funnel Plot"))

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addWidget(missing_box)
        main_layout.addWidget(self.graph_checkbox)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Trim and Fill Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.log_transformed = self.log_transform_box.isChecked()
        options.create_graph = self.graph_checkbox.isChecked()
        if self.r_button.isChecked():
            options.k_estimator = "R"
        elif self.q_button.isChecked():
            options.k_estimator = "Q"
        else:
            options.k_estimator = "L"


class MetaAnalysisPhylogeneticStructureDialog(QDialog):
    """
    Dialog for choosing options for a phylogenetic meta-analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["phylogenetic_glm"]
        self.effect_size_box = None
        self.variance_box = None
        self.cat_box = None
        self.cont_box = None
        self.unused_box = None
        self.unused_label = None
        self.cat_var_label = None
        self.cont_var_label = None
        # self.include_ind_box = None
        self.drag_label = None
        self.tips_box = None
        self.columns = None
        self.random_effects_checkbox = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, ok_button = add_ok_cancel_help_button_layout(self)
        ok_button.clicked.disconnect()
        ok_button.clicked.connect(self.click_ok_button)

        analysis_label = QLabel(get_text("Phylogenetic GLM Meta-Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        ind_group_box = QGroupBox("")
        ind_layout = QGridLayout()
        self.unused_label = QLabel(get_text("Unused"))
        self.cat_var_label = QLabel(get_text("Categorical Variables"))
        self.cont_var_label = QLabel(get_text("Continuous Variables"))
        self.unused_box = add_drag_drop_list()
        self.cat_box = add_drag_drop_list()
        self.cont_box = add_drag_drop_list()
        tips_label = QLabel(get_text("Phylogeny Tip Names"))
        self.tips_box = QComboBox()
        for col in self.columns:
            self.unused_box.addItem(create_list_item(col))
            self.tips_box.addItem(col.label)

        self.drag_label = QLabel(get_text("Drag and drop variables to indicate desired structure"))
        ind_layout.addWidget(self.unused_label, 1, 0)
        ind_layout.addWidget(self.cat_var_label, 1, 1)
        ind_layout.addWidget(self.cont_var_label, 1, 2)
        ind_layout.addWidget(self.unused_box, 2, 0)
        ind_layout.addWidget(self.cat_box, 2, 1)
        ind_layout.addWidget(self.cont_box, 2, 2)
        ind_layout.addWidget(self.drag_label, 3, 0, 1, 3)
        ind_group_box.setLayout(ind_layout)

        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        upper_left_layout = QVBoxLayout()
        upper_left_layout.addWidget(effect_size_label)
        upper_left_layout.addWidget(self.effect_size_box)
        upper_left_layout.addWidget(self.log_transform_box)
        upper_left_layout.addWidget(variance_label)
        upper_left_layout.addWidget(self.variance_box)
        upper_right_layout = QVBoxLayout()
        upper_right_layout.addWidget(tips_label)
        upper_right_layout.addWidget(self.tips_box)
        upper_right_layout.addStretch(1)
        upper_right_layout.addWidget(self.random_effects_checkbox)
        upper_layout = QHBoxLayout()
        upper_layout.addLayout(upper_left_layout)
        upper_layout.addLayout(upper_right_layout)
        options_layout.addLayout(upper_layout)
        options_layout.addWidget(ind_group_box)
        # self.click_ind_box()

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Phylogenetic GLM Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_ok_button(self):
        e = self.columns[self.effect_size_box.currentIndex()]
        cats = [self.cat_box.item(i).column for i in range(self.cat_box.count())]
        conts = [self.cont_box.item(i).column for i in range(self.cont_box.count())]
        if (e in cats) or (e in conts):
            report_warning(self, get_text("Invalid Choices"), get_text("effect_size_ind_error"))
        else:
            self.accept()

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        for i in range(self.cat_box.count()):
            options.categorical_vars.append(self.cat_box.item(i).column)
        for i in range(self.cont_box.count()):
            options.continuous_vars.append(self.cont_box.item(i).column)
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.log_transformed = self.log_transform_box.isChecked()
        options.tip_names = self.columns[self.tips_box.currentIndex()]


class MetaAnalysisPhylogeneticStructureExtraDialog(QDialog):
    """
    Dialog for choosing extra options for a phylogenetic meta-analysis
    """
    def __init__(self):
        super().__init__()
        self.randomize_checkbox = None
        self.randomize_n_label = None
        self.randomize_n_box = None
        self.randomize_phylogeny_checkbox = None
        self.randomize_phylogeny_n_label = None
        self.randomize_phylogeny_n_box = None
        self.help = MetaWinConstants.help_index["phylogenetic_glm"]
        self.init_ui()

    def init_ui(self):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        options_label = QLabel(get_text("Additional Options"))
        options_label.setStyleSheet(MetaWinConstants.title_label_style)

        randomization_group = QGroupBox(get_text("Resampling Procedures"))
        randomization_layout = QVBoxLayout()

        self.randomize_checkbox = QCheckBox(get_text("Randomization Test for Model Structure"))
        self.randomize_checkbox.clicked.connect(self.click_randomize_checkbox)
        randomization_layout.addWidget(self.randomize_checkbox)
        self.randomize_n_label = QLabel(get_text("Number of Iterations"))
        randomization_layout.addWidget(self.randomize_n_label)
        self.randomize_n_box = QLineEdit()
        self.randomize_n_box.setText("999")
        self.randomize_n_box.setValidator(QIntValidator(99, 999999))
        randomization_layout.addWidget(self.randomize_n_box)
        self.click_randomize_checkbox()

        self.randomize_phylogeny_checkbox = QCheckBox(get_text("Randomization Test for Phylogenetic Structure"))
        self.randomize_phylogeny_checkbox.clicked.connect(self.click_randomize_phylogeny_checkbox)
        randomization_layout.addWidget(self.randomize_phylogeny_checkbox)
        self.randomize_phylogeny_n_label = QLabel(get_text("Number of Iterations"))
        randomization_layout.addWidget(self.randomize_phylogeny_n_label)
        self.randomize_phylogeny_n_box = QLineEdit()
        self.randomize_phylogeny_n_box.setText("999")
        self.randomize_phylogeny_n_box.setValidator(QIntValidator(99, 999999))
        randomization_layout.addWidget(self.randomize_phylogeny_n_box)
        self.click_randomize_phylogeny_checkbox()

        randomization_group.setLayout(randomization_layout)

        options_layout = QVBoxLayout()
        options_layout.addWidget(randomization_group)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(options_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Phylogenetic GLM Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_randomize_checkbox(self):
        if self.randomize_checkbox.isChecked():
            self.randomize_n_label.setEnabled(True)
            self.randomize_n_box.setEnabled(True)
        else:
            self.randomize_n_label.setEnabled(False)
            self.randomize_n_box.setEnabled(False)

    def click_randomize_phylogeny_checkbox(self):
        if self.randomize_phylogeny_checkbox.isChecked():
            self.randomize_phylogeny_n_label.setEnabled(True)
            self.randomize_phylogeny_n_box.setEnabled(True)
        else:
            self.randomize_phylogeny_n_label.setEnabled(False)
            self.randomize_phylogeny_n_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        if self.randomize_checkbox.isChecked():
            options.randomize_model = int(self.randomize_n_box.text())
        else:
            options.randomize_model = None
        if self.randomize_phylogeny_checkbox.isChecked():
            options.randomize_phylogeny = int(self.randomize_phylogeny_n_box.text())
        else:
            options.randomize_phylogeny = None


class MetaAnalysisJackknifeDialog(QDialog):
    """
    Dialog for choosing options for a jaccknife (leave one out) meta-analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["jackknife_analysis"]
        self.effect_size_box = None
        self.variance_box = None
        self.columns = None
        self.random_effects_checkbox = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Jackknife Meta-Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(self.log_transform_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(self.random_effects_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Jackknife Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.log_transformed = self.log_transform_box.isChecked()


class MetaAnalysisJackknifeExtraDialog(QDialog):
    """
    Dialog for choosing extra options for a simple meta-analysis
    """
    def __init__(self):
        super().__init__()
        self.bootstrap_checkbox = None
        self.bootstrap_n_label = None
        self.bootstrap_n_box = None
        self.graph_checkbox = None
        self.help = MetaWinConstants.help_index["basic_analysis"]
        self.init_ui()

    def init_ui(self):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        options_label = QLabel(get_text("Additional Options"))
        options_label.setStyleSheet(MetaWinConstants.title_label_style)

        randomization_group = add_resampling_options_to_dialog(self, False)

        self.graph_checkbox = QCheckBox(get_text("Graph Jackknife Means (Forest Plot)"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(randomization_group)
        options_layout.addWidget(self.graph_checkbox)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(options_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Jackknife Meta-Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_bootstrap_checkbox(self):
        if self.bootstrap_checkbox.isChecked():
            self.bootstrap_n_label.setEnabled(True)
            self.bootstrap_n_box.setEnabled(True)
        else:
            self.bootstrap_n_label.setEnabled(False)
            self.bootstrap_n_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        if self.bootstrap_checkbox.isChecked():
            options.bootstrap_mean = int(self.bootstrap_n_box.text())
        else:
            options.bootstrap_mean = None
        options.create_graph = self.graph_checkbox.isChecked()


class MetaAnalysisRankCorrelationDialog(QDialog):
    """
    Dialog for choosing options for a rank correlation analysis
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["rank_correlation"]
        self.effect_size_box = None
        self.variance_box = None
        self.sample_size_box = None
        self.columns = None
        # self.random_effects_checkbox = None
        self.kendall_button = None
        self.spearman_button = None
        self.n_button = None
        self.v_button = None
        self.randomize_n_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Rank Correlation Analysis"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)

        self.sample_size_box = QComboBox()
        for col in self.columns:
            self.sample_size_box.addItem(col.label)

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)

        cor_box = QGroupBox(get_text("Correlate Effect Size with"))
        cor_layout = QVBoxLayout()
        self.n_button = QRadioButton(get_text("Sample Size"))
        self.v_button = QRadioButton(get_text("Variance"))
        self.n_button.clicked.connect(self.click_correlation_variable)
        self.v_button.clicked.connect(self.click_correlation_variable)
        cor_layout.addWidget(self.v_button)
        cor_layout.addWidget(self.n_button)
        cor_layout.addWidget(self.sample_size_box)
        cor_box.setLayout(cor_layout)
        self.v_button.setChecked(True)
        self.click_correlation_variable()

        test_box = QGroupBox(get_text("Rank Correlation Method"))
        test_box_layout = QVBoxLayout()
        test_layout = QHBoxLayout()
        self.kendall_button = QRadioButton("Kendall's τ")
        self.spearman_button = QRadioButton("Spearman's ρ")
        test_layout.addWidget(self.kendall_button)
        test_layout.addWidget(self.spearman_button)
        test_box_layout.addLayout(test_layout)

        randomize_n_label = QLabel(get_text("Number of Iterations"))
        test_box_layout.addWidget(randomize_n_label)
        self.randomize_n_box = QLineEdit()
        self.randomize_n_box.setText("999")
        self.randomize_n_box.setValidator(QIntValidator(99, 999999))
        test_box_layout.addWidget(self.randomize_n_box)

        test_box.setLayout(test_box_layout)
        self.kendall_button.setChecked(True)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addWidget(cor_box)
        main_layout.addWidget(test_box)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Rank Correlation Analysis"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_correlation_variable(self):
        if self.n_button.isChecked():
            self.sample_size_box.setEnabled(True)
        else:
            self.sample_size_box.setEnabled(False)

    def set_options(self, options: MetaAnalysisOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.randomize_model = int(self.randomize_n_box.text())
        if self.spearman_button.isChecked():
            options.cor_test = "rho"
        else:
            options.cor_test = "tau"
        if self.n_button.isChecked():
            options.sample_size = self.columns[self.sample_size_box.currentIndex()]
        else:
            options.sample_size = None


def add_resampling_options_to_dialog(sender, test_model: bool = False):
    """
    function to add standard resampling test options to a dialog

    this includes bootstrapping, with or without randomization
    """
    # resampling tests
    randomization_group = QGroupBox(get_text("Resampling Procedures"))
    randomization_layout = QVBoxLayout()
    sender.bootstrap_checkbox = QCheckBox(get_text("Bootstrap Mean Effect Size(s)"))
    sender.bootstrap_checkbox.clicked.connect(sender.click_bootstrap_checkbox)
    randomization_layout.addWidget(sender.bootstrap_checkbox)
    sender.bootstrap_n_label = QLabel(get_text("Number of Iterations"))
    randomization_layout.addWidget(sender.bootstrap_n_label)
    sender.bootstrap_n_box = QLineEdit()
    sender.bootstrap_n_box.setText("999")
    sender.bootstrap_n_box.setValidator(QIntValidator(99, 999999))
    randomization_layout.addWidget(sender.bootstrap_n_box)
    sender.click_bootstrap_checkbox()

    if test_model:
        sender.randomize_checkbox = QCheckBox(get_text("Randomization Test for Model Structure"))
        sender.randomize_checkbox.clicked.connect(sender.click_randomize_checkbox)
        randomization_layout.addWidget(sender.randomize_checkbox)
        sender.randomize_n_label = QLabel(get_text("Number of Iterations"))
        randomization_layout.addWidget(sender.randomize_n_label)
        sender.randomize_n_box = QLineEdit()
        sender.randomize_n_box.setText("999")
        sender.randomize_n_box.setValidator(QIntValidator(99, 999999))
        randomization_layout.addWidget(sender.randomize_n_box)
        sender.click_randomize_checkbox()

    randomization_group.setLayout(randomization_layout)
    return randomization_group


def do_meta_analysis(data, options, decimal_places: int = 4, alpha: float = 0.05, tree: Optional = None,
                     norm_ci: bool = True, sender=None):
    """
    primary function controlling the execution of an analysis

    based on specific options, farms out analysis to computational functions, then collects and returns
    results
    """
    output_blocks = [["<h2>{}</h2>".format(get_text("Analysis"))]]
    options.norm_ci = norm_ci
    output, all_citations = options.report_choices()
    output_blocks.extend(output)
    if options.structure == SIMPLE_MA:
        (output, chart_data, analysis_values,
         citations) = MetaWinAnalysisFunctions.simple_meta_analysis(data, options, decimal_places, alpha, norm_ci,
                                                                    sender=sender)
    elif options.structure == GROUPED_MA:
        (output, chart_data, analysis_values,
         citations) = MetaWinAnalysisFunctions.grouped_meta_analysis(data, options, decimal_places, alpha, norm_ci,
                                                                     sender=sender)
    elif options.structure == CUMULATIVE_MA:
        output, chart_data = MetaWinAnalysisFunctions.cumulative_meta_analysis(data, options, decimal_places, alpha,
                                                                               norm_ci, sender=sender)
        analysis_values = None
        citations = []
    elif options.structure == REGRESSION_MA:
        (output, chart_data, analysis_values,
         citations) = MetaWinAnalysisFunctions.regression_meta_analysis(data, options, decimal_places, alpha, norm_ci,
                                                                        sender=sender)
    elif options.structure == COMPLEX_MA:
        output, analysis_values, citations = MetaWinAnalysisFunctions.complex_meta_analysis(data, options,
                                                                                            decimal_places, alpha,
                                                                                            norm_ci, sender=sender)
        chart_data = None
    elif options.structure == NESTED_MA:
        (output, chart_data, analysis_values,
         citations) = MetaWinAnalysisFunctions.nested_meta_analysis(data, options, decimal_places, alpha, norm_ci,
                                                                    sender=sender)
    elif options.structure == TRIM_FILL:
        (output, chart_data, analysis_values,
         citations) = MetaWinAnalysisFunctions.trim_and_fill_analysis(data, options, decimal_places, alpha, norm_ci)
    elif options.structure == JACKKNIFE:
        (output, chart_data,
         citations) = MetaWinAnalysisFunctions.jackknife_meta_analysis(data, options, decimal_places, alpha, norm_ci,
                                                                       sender=sender)
        analysis_values = None
    elif options.structure == PHYLOGENETIC_MA:
        output, citations = MetaWinAnalysisFunctions.phylogenetic_meta_analysis(data, options, tree, decimal_places,
                                                                                alpha, norm_ci, sender=sender)
        analysis_values = None
        chart_data = None
    elif options.structure == RANKCOR:
        output, citations = MetaWinAnalysisFunctions.rank_correlation_analysis(data, options, decimal_places,
                                                                               sender=sender)
        chart_data = None
        analysis_values = None
    else:
        output = []
        analysis_values = None
        chart_data = None
        citations = []
    all_citations.extend(citations)
    output_blocks.extend(output)
    output_blocks.extend(create_reference_list(all_citations))
    return output_blocks, chart_data, analysis_values


def meta_analysis(sender, data, last_effect, last_var, decimal_places: int = 4, alpha: float = 0.05,
                  tree: Optional = None, norm_ci: bool = True):
    """
    primary function for calling various dialogs to retrieve user choices about how to run various analyses
    """
    meta_analysis_options = MetaAnalysisOptions()
    sender.meta_analysis_dialog = MetaAnalysisStructureDialog(meta_analysis_options, tree)
    if sender.meta_analysis_dialog.exec():
        if meta_analysis_options.structure == SIMPLE_MA:
            sender.meta_analysis_structure_dialog = MetaAnalysisSimpleStructureDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = MetaAnalysisSimpleStructureExtraDialog()
        elif meta_analysis_options.structure == GROUPED_MA:
            sender.meta_analysis_structure_dialog = MetaAnalysisGroupedStructureDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = MetaAnalysisGroupStructureExtraDialog()
        elif meta_analysis_options.structure == CUMULATIVE_MA:
            sender.meta_analysis_structure_dialog = MetaAnalysisCumulativeStructureDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = MetaAnalysisCumulativeStructureExtraDialog()
        elif meta_analysis_options.structure == NESTED_MA:
            sender.meta_analysis_structure_dialog = MetaAnalysisNestedStructureDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = MetaAnalysisNestedStructureExtraDialog()
        elif meta_analysis_options.structure == REGRESSION_MA:
            sender.meta_analysis_structure_dialog = MetaAnalysisLinearStructureDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = MetaAnalysisLinearStructureExtraDialog()
        elif meta_analysis_options.structure == COMPLEX_MA:
            sender.meta_analysis_structure_dialog = MetaAnalysisComplexStructureDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = MetaAnalysisComplexStructureExtraDialog()
        elif meta_analysis_options.structure == TRIM_FILL:
            sender.meta_analysis_structure_dialog = MetaAnalysisTrimFillDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = None
        elif meta_analysis_options.structure == PHYLOGENETIC_MA:
            sender.meta_analysis_structure_dialog = MetaAnalysisPhylogeneticStructureDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = MetaAnalysisPhylogeneticStructureExtraDialog()
        elif meta_analysis_options.structure == JACKKNIFE:
            sender.meta_analysis_structure_dialog = MetaAnalysisJackknifeDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = MetaAnalysisJackknifeExtraDialog()
        elif meta_analysis_options.structure == RANKCOR:
            sender.meta_analysis_structure_dialog = MetaAnalysisRankCorrelationDialog(data, last_effect, last_var)
            sender.meta_analysis_extra_dialog = None
        else:
            meta_analysis_options.structure = None

        if meta_analysis_options.structure is not None:
            if sender.meta_analysis_structure_dialog.exec():
                sender.meta_analysis_structure_dialog.set_options(meta_analysis_options)
                if sender.meta_analysis_extra_dialog is not None:
                    if sender.meta_analysis_extra_dialog.exec():
                        sender.meta_analysis_extra_dialog.set_options(meta_analysis_options)
                    else:
                        meta_analysis_options.structure = None
            else:
                meta_analysis_options.structure = None

        if meta_analysis_options.structure is not None:
            output, chart_data, _ = do_meta_analysis(data, meta_analysis_options, decimal_places, alpha, tree, norm_ci,
                                                     sender=sender)
            sender.last_effect = meta_analysis_options.effect_data
            sender.last_var = meta_analysis_options.effect_vars
            return output, chart_data
    return None, None, None
