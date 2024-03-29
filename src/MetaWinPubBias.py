"""
Module controlling choice selection for publication bias tests
"""


# from typing import Optional
import webbrowser

from PyQt6.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QFrame, QComboBox, QGroupBox, QLineEdit, \
    QRadioButton, QHBoxLayout, QCheckBox
from PyQt6.QtGui import QIcon, QIntValidator

from MetaWinData import MetaWinData
import MetaWinConstants
import MetaWinPubBiasFunctions
from MetaWinWidgets import add_ok_cancel_help_button_layout, add_cancel_help_button_layout, add_effect_choice_to_dialog
from MetaWinUtils import get_citation, create_reference_list
from MetaWinLanguage import get_text


TRIM_FILL = 1
RANKCOR = 2
FUNNEL = 3
EGGER = 4


class PubBiasOptions:
    def __init__(self):
        self.pub_bias_test = None
        self.effect_data = None
        self.effect_vars = None
        self.sample_size = None
        self.bootstrap_mean = None
        self.random_effects = False
        self.log_transformed = False
        self.randomize_model = None
        self.create_graph = False
        self.k_estimator = "L"
        self.cor_test = "tau"
        self.norm_ci = True
        self.funnel_y = None
        self.pseudo_ci = False
        self.contour_ci = False
        self.sunset_power = False

    def report_choices(self):
        output_blocks = []
        citations = []
        if self.pub_bias_test is not None:
            output = []
            if self.pub_bias_test == TRIM_FILL:
                output.append(get_text("Trim and Fill Analysis"))
                output.append("→ {}: ".format(get_text("Citations")) + get_citation("Duval_Tweedie_2000a") + ", " +
                              get_citation("Duval_Tweedie_2000b"))
                citations.append("Duval_Tweedie_2000a")
                citations.append("Duval_Tweedie_2000b")
            elif self.pub_bias_test == RANKCOR:
                output.append(get_text("Rank Correlation Analysis"))
                output.append("→ {}: ".format(get_text("Citations")) + get_citation("Begg_1994") + ", " +
                              get_citation("Begg_Mazumdar_1994"))
                citations.append("Begg_1994")
                citations.append("Begg_Mazumdar_1994")
            elif self.pub_bias_test == FUNNEL:
                output.append(get_text("Funnel Plot"))
                output.append("→ {}: ".format(get_text("Citations")) + get_citation("Light_Pillemer_1984"))
                citations.append("Light_Pillemer_1984")
            elif self.pub_bias_test == EGGER:
                output.append(get_text("Egger Regression"))
                output.append("→ {}: ".format(get_text("Citations")) + get_citation("Egger_et_1997"))
                citations.append("Egger_et_1997")
            if self.pub_bias_test in (TRIM_FILL, EGGER):
                if self.random_effects:
                    output.append("→ {}".format(get_text("Random Effects Model")))
                else:
                    output.append("→ {}".format(get_text("Fixed Effects Model")))

            output_blocks.append(output)

            output = ["→ {}: ".format(get_text("Effect Sizes")) + self.effect_data.label,
                      "→ {}: ".format(get_text("Effect Size Variances")) + self.effect_vars.label]
            if self.pub_bias_test == TRIM_FILL:
                output.append("→ {}: {}<sub>0</sub>".format(get_text("Estimator of Missing Studies"),
                                                            self.k_estimator))
            elif self.pub_bias_test == RANKCOR:
                if self.cor_test == "tau":
                    output.append("→ {}: {}".format(get_text("Rank Correlation Method"), "Kendall's &tau;"))
                    output.append("→ {}: ".format(get_text("Citation")) + get_citation("Kendall_1938"))
                    citations.append("Kendall_1938")
                else:
                    output.append("→ {}: {}".format(get_text("Estimator of Missing Studies"), "Spearman's &rho;"))
                    output.append("→ {}: ".format(get_text("Citation")) + get_citation("Spearman_1904"))
                    citations.append("Spearman_1904")
            elif self.pub_bias_test == FUNNEL:
                if self.sample_size is not None:
                    output.append("→ {}: ".format(get_text("Sample Sizes")) + self.sample_size.label)

            output_blocks.append(output)

            if self.pub_bias_test == TRIM_FILL:
                output = []
                if self.norm_ci:
                    output.append("→ {}".format(get_text("ci from norm")))
                else:
                    output.append("→ {}".format(get_text("ci from t")))
                output_blocks.append(output)

            if self.pub_bias_test == RANKCOR:
                output_blocks.append(["→ {}: {} {}".format(get_text("Randomization to test correlation"),
                                                           self.randomize_model, get_text("iterations"))])

        return output_blocks, citations


class PubBiasTestDialog(QDialog):
    """
    Dialog for choosing primary analysis to perform
    """
    def __init__(self, options: PubBiasOptions):
        super().__init__()
        self.help = MetaWinConstants.help_index["analyses"]
        self.__options = options
        self.init_ui()

    def init_ui(self):
        analysis_layout = QVBoxLayout()
        funnel_button = QPushButton(get_text("Funnel Plot"))
        funnel_button.clicked.connect(self.funnel_button_click)
        analysis_layout.addWidget(funnel_button)
        egger_button = QPushButton(get_text("Egger Regression"))
        egger_button.clicked.connect(self.egger_button_click)
        analysis_layout.addWidget(egger_button)
        trim_fill_button = QPushButton(get_text("Trim and Fill Analysis"))
        trim_fill_button.clicked.connect(self.trim_fill_button_click)
        analysis_layout.addWidget(trim_fill_button)
        rank_cor_button = QPushButton(get_text("Rank Correlation Analysis"))
        rank_cor_button.clicked.connect(self.rank_cor_button_click)
        analysis_layout.addWidget(rank_cor_button)

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
        self.setWindowTitle(get_text("Publication Bias"))

    def show_help(self):
        webbrowser.open(self.help)

    def trim_fill_button_click(self):
        self.__options.pub_bias_test= TRIM_FILL
        self.accept()

    def rank_cor_button_click(self):
        self.__options.pub_bias_test = RANKCOR
        self.accept()

    def funnel_button_click(self):
        self.__options.pub_bias_test = FUNNEL
        self.accept()

    def egger_button_click(self):
        self.__options.pub_bias_test = EGGER
        self.accept()


class PubBiasTrimFillDialog(QDialog):
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

    def set_options(self, options: PubBiasOptions):
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


class PubBiasRankCorrelationDialog(QDialog):
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

    def set_options(self, options: PubBiasOptions):
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


class PubBiasFunnelPlotDialog(QDialog):
    """
    Dialog for choosing options for a funnel plot
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["funnel_plot"]
        self.effect_size_box = None
        self.variance_box = None
        self.sample_size_box = None
        self.columns = None
        self.n_button = None
        self.v_button = None
        self.invv_button = None
        self.se_button = None
        self.prec_button = None
        self.sample_size_label = None
        self.pseudo_ci_box = None
        self.contour_box = None
        self.sunset_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Funnel Plot"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)

        self.sample_size_box = QComboBox()
        for col in self.columns:
            self.sample_size_box.addItem(col.label)
        self.sample_size_label = QLabel(get_text("Sample Size"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(self.sample_size_label)
        options_layout.addWidget(self.sample_size_box)

        y_box = QGroupBox(get_text("Correlate Effect Size with"))
        y_layout = QVBoxLayout()
        self.n_button = QRadioButton(get_text("Sample Size"))
        self.v_button = QRadioButton(get_text("Variance"))
        self.invv_button = QRadioButton(get_text("Inverse Variance"))
        self.se_button = QRadioButton(get_text("Standard Error"))
        self.prec_button = QRadioButton(get_text("Precision"))

        self.n_button.clicked.connect(self.click_y_variable)
        self.v_button.clicked.connect(self.click_y_variable)
        self.invv_button.clicked.connect(self.click_y_variable)
        self.se_button.clicked.connect(self.click_y_variable)
        self.prec_button.clicked.connect(self.click_y_variable)

        y_layout.addWidget(self.n_button)
        y_layout.addWidget(self.v_button)
        y_layout.addWidget(self.invv_button)
        y_layout.addWidget(self.se_button)
        y_layout.addWidget(self.prec_button)
        y_box.setLayout(y_layout)
        self.se_button.setChecked(True)

        self.pseudo_ci_box = QCheckBox(get_text("Include Pseudo-Confidence Limits"))
        self.contour_box = QCheckBox(get_text("Include Contour Confidence Limits"))
        self.sunset_box = QCheckBox(get_text("Include Power/Sunset Coloration"))
        self.click_y_variable()

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addWidget(y_box)
        main_layout.addWidget(self.pseudo_ci_box)
        main_layout.addWidget(self.contour_box)
        main_layout.addWidget(self.sunset_box)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Funnel Plot"))

    def show_help(self):
        webbrowser.open(self.help)

    def click_y_variable(self):
        if self.n_button.isChecked():
            self.sample_size_box.setEnabled(True)
            self.sample_size_label.setEnabled(True)
            self.pseudo_ci_box.setEnabled(False)
            self.contour_box.setEnabled(False)
            self.sunset_box.setEnabled(False)
        else:
            self.sample_size_box.setEnabled(False)
            self.sample_size_label.setEnabled(False)
            self.pseudo_ci_box.setEnabled(True)
            self.contour_box.setEnabled(True)
            self.sunset_box.setEnabled(True)

    def set_options(self, options: PubBiasOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        if self.n_button.isChecked():
            options.sample_size = self.columns[self.sample_size_box.currentIndex()]
            options.funnel_y = "sample size"
            options.pseudo_ci = False
            options.contour_ci = False
        else:
            options.sample_size = None
            if self.v_button.isChecked():
                options.funnel_y = "variance"
            elif self.invv_button.isChecked():
                options.funnel_y = "inverse variance"
            elif self.se_button.isChecked():
                options.funnel_y = "standard error"
            elif self.prec_button.isChecked():
                options.funnel_y = "precision"
            options.pseudo_ci = self.pseudo_ci_box.isChecked()
            options.contour_ci = self.contour_box.isChecked()
            options.sunset_power = self.sunset_box.isChecked()


class PubBiasEggerDialog(QDialog):
    """
    Dialog for choosing options for Egger regression
    """
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["egger_regression"]
        self.effect_size_box = None
        self.variance_box = None
        self.columns = None
        self.graph_checkbox = None
        self.random_effects_checkbox = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        analysis_label = QLabel(get_text("Egger Regression"))
        analysis_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)
        self.random_effects_checkbox = QCheckBox(get_text("Include Random Effects Variance?"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(self.random_effects_checkbox)

        self.graph_checkbox = QCheckBox(get_text("Graph Regression"))

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(main_frame)
        main_layout.addWidget(self.graph_checkbox)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Egger Regression"))

    def show_help(self):
        webbrowser.open(self.help)

    def set_options(self, options: PubBiasOptions):
        options.effect_data = self.columns[self.effect_size_box.currentIndex()]
        options.effect_vars = self.columns[self.variance_box.currentIndex()]
        options.random_effects = self.random_effects_checkbox.isChecked()
        options.create_graph = self.graph_checkbox.isChecked()


def do_pub_bias(data, options, decimal_places: int = 4, alpha: float = 0.05,  norm_ci: bool = True, sender=None):
    """
    primary function controlling the execution of publication biases

    based on specific options, farms out analysis to computational functions, then collects and returns
    results
    """
    output_blocks = [["<h2>{}</h2>".format(get_text("Publication Bias"))]]
    options.norm_ci = norm_ci
    output, all_citations = options.report_choices()
    output_blocks.extend(output)
    if options.pub_bias_test == TRIM_FILL:
        (output, chart_data, analysis_values,
         citations) = MetaWinPubBiasFunctions.trim_and_fill_analysis(data, options, decimal_places, alpha, norm_ci)
    elif options.pub_bias_test == RANKCOR:
        output, citations = MetaWinPubBiasFunctions.rank_correlation_analysis(data, options, decimal_places,
                                                                              sender=sender)
        chart_data = None
        analysis_values = None
    elif options.pub_bias_test == FUNNEL:
        output, chart_data, citations = MetaWinPubBiasFunctions.funnel_plot_setup(data, options)
        analysis_values = None
    elif options.pub_bias_test == EGGER:
        output, chart_data, citations = MetaWinPubBiasFunctions.egger_regression(data, options, decimal_places, alpha,
                                                                                 norm_ci)
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


def publication_bias(sender, data, last_effect, last_var, decimal_places: int = 4, alpha: float = 0.05,
                     norm_ci: bool = True):
    """
    primary function for calling various dialogs to retrieve user choices about how to run publication bias tests
    """
    pub_test_dialogs = {TRIM_FILL: PubBiasTrimFillDialog,
                        RANKCOR: PubBiasRankCorrelationDialog,
                        FUNNEL: PubBiasFunnelPlotDialog,
                        EGGER: PubBiasEggerDialog}

    pub_bias_options = PubBiasOptions()
    sender.pub_bias_dialog = PubBiasTestDialog(pub_bias_options)
    if sender.pub_bias_dialog.exec():
        if pub_bias_options.pub_bias_test in pub_test_dialogs:
            sender.pub_bias_test_dialog = pub_test_dialogs[pub_bias_options.pub_bias_test](data, last_effect, last_var)
        else:
            pub_bias_options.pub_bias_test = None

        if pub_bias_options.pub_bias_test is not None:
            if sender.pub_bias_test_dialog.exec():
                sender.pub_bias_test_dialog.set_options(pub_bias_options)
            else:
                pub_bias_options.pub_bias_test = None

        if pub_bias_options.pub_bias_test is not None:
            output, chart_data, _ = do_pub_bias(data, pub_bias_options, decimal_places, alpha, norm_ci, sender=sender)
            sender.last_effect = pub_bias_options.effect_data
            sender.last_var = pub_bias_options.effect_vars
            return output, chart_data
    return None, None
