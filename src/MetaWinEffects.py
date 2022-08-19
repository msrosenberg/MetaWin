"""
Dialogs and control elements for the calculation of effect sizes
"""

import webbrowser

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QComboBox, \
    QGroupBox, QRadioButton, QCheckBox
from PyQt6.QtGui import QIcon

from MetaWinData import MetaWinData
from MetaWinUtils import create_output_table, get_citation, create_reference_list
import MetaWinConstants
import MetaWinEffectFunctions
from MetaWinWidgets import add_ok_cancel_help_button_layout
from MetaWinLanguage import get_text


class EffectSizeOptions:
    def __init__(self):
        self.effect_size = None
        self.control_means = None
        self.treatment_means = None
        self.control_n = None
        self.treatment_n = None
        self.control_sd = None
        self.treatment_sd = None
        self.control_response = None
        self.control_no_response = None
        self.treatment_response = None
        self.treatment_no_response = None
        self.correlation = None
        self.correlation_n = None
        self.probability = None
        self.probability_n = None
        self.polarity = None

    def report_choices(self):
        output_blocks = [["<h3>{}</h3>".format(get_text("Calculate Effect Sizes"))]]
        if self.effect_size is not None:
            output = ["{}".format(self.effect_size.name)]

            cite_list = []
            for c in self.effect_size.citations:
                cite_list.append(get_citation(c))
            if len(self.effect_size.citations) > 1:
                s = get_text("Citations")
            else:
                s = get_text("Citation")
            output.append("→ {}: ".format(s) + ", ".join(cite_list))
            output_blocks.append(output)
            output = [get_text("Data obtained from columns:")]
            if self.effect_size.name in ("Hedges\' d", "ln Response Ratio"):
                output.append("→ {}: ".format(get_text("Control Means")) + self.control_means.label)
                output.append("→ {}: ".format(get_text("Control Sample Sizes")) + self.control_n.label)
                output.append("→ {}: ".format(get_text("Control Standard Deviations")) + self.control_sd.label)
                output.append("→ {}: ".format(get_text("Treatment Means")) + self.treatment_means.label)
                output.append("→ {}: ".format(get_text("Treatment Sample Sizes")) + self.treatment_n.label)
                output.append("→ {}: ".format(get_text("Treatment Standard Deviations")) + self.treatment_sd.label)
            elif self.effect_size.name in ("Rate Difference", "ln Relative Rate", "ln Odds Ratio"):
                output.append("→ {}: ".format(get_text("Control Response Count")) + self.control_response.label)
                output.append("→ {}: ".format(get_text("Control No Response Count")) + self.control_no_response.label)
                output.append("→ {}: ".format(get_text("Treatment Response Count")) + self.treatment_response.label)
                output.append("→ {}: ".format(get_text("Treatment No Response Count")) +
                              self.treatment_no_response.label)
            elif self.effect_size.name == "Fisher\'s Z-transform":
                output.append("→ {}: ".format(get_text("Correlations")) + self.correlation.label)
                output.append("→ {}: ".format(get_text("Sample Size")) + self.correlation_n.label)
            elif self.effect_size.name == "Logit":
                output.append("→ {}: ".format(get_text("Probabilities")) + self.probability.label)
                output.append("→ {}: ".format(get_text("Sample Size")) + self.probability_n.label)

            if self.polarity is not None:
                output.append("→ {}: ".format(get_text("Effect Size Polarity Indicator")) + self.polarity.label)
            output_blocks.append(output)
        return output_blocks, self.effect_size.citations


class EffectSizesDialog(QDialog):
    def __init__(self, data: MetaWinData):
        super().__init__()
        self.means_button = None
        self.twoxtwo_button = None
        self.correlation_button = None
        self.probability_button = None
        self.effect_choice1 = None
        self.effect_choice2 = None
        self.effect_choice3 = None
        self.control_label = None
        self.treatment_label = None
        self.control_box_1 = None
        self.treatment_box_1 = None
        self.control_box_2 = None
        self.treatment_box_2 = None
        self.control_box_3 = None
        self.treatment_box_3 = None
        self.box_1_label = None
        self.box_2_label = None
        self.box_3_label = None
        self.data_location_layout = None
        self.polarity_checkbox = None
        self.polarity_choice_box = None
        self.columns = None
        self.help = MetaWinConstants.help_index["effect_sizes"]
        self.init_ui(data)

    def init_ui(self, data: MetaWinData):
        data_type_box = QGroupBox(get_text("Data Type"))
        self.means_button = QRadioButton(get_text("Pairs of Means"))
        self.means_button.clicked.connect(self.data_type_change)
        self.means_button.setChecked(True)
        self.twoxtwo_button = QRadioButton(get_text("Two x Two Contingency Table"))
        self.twoxtwo_button.clicked.connect(self.data_type_change)
        self.correlation_button = QRadioButton(get_text("Correlation Coefficients"))
        self.correlation_button.clicked.connect(self.data_type_change)
        self.probability_button = QRadioButton(get_text("Probabilities"))
        self.probability_button.clicked.connect(self.data_type_change)
        data_type_layout = QVBoxLayout()
        data_type_layout.addWidget(self.means_button)
        data_type_layout.addWidget(self.twoxtwo_button)
        data_type_layout.addWidget(self.correlation_button)
        data_type_layout.addWidget(self.probability_button)
        data_type_box.setLayout(data_type_layout)

        effect_size_box = QGroupBox(get_text("Effect Size"))
        effect_size_layout = QVBoxLayout()
        self.effect_choice1 = QRadioButton("")
        self.effect_choice2 = QRadioButton("")
        self.effect_choice3 = QRadioButton("")
        effect_size_layout.addWidget(self.effect_choice1)
        effect_size_layout.addWidget(self.effect_choice2)
        effect_size_layout.addWidget(self.effect_choice3)
        effect_size_box.setLayout(effect_size_layout)

        data_location_box = QGroupBox(get_text("Data Location"))
        self.data_location_layout = QGridLayout()
        self.control_label = QLabel(get_text("Control"))
        self.treatment_label = QLabel(get_text("Treatment"))
        self.control_box_1 = QComboBox()
        self.treatment_box_1 = QComboBox()
        self.control_box_2 = QComboBox()
        self.treatment_box_2 = QComboBox()
        self.control_box_3 = QComboBox()
        self.treatment_box_3 = QComboBox()
        self.columns = data.cols
        for col in data.cols:
            self.control_box_1.addItem(col.label)
            self.treatment_box_1.addItem(col.label)
            self.control_box_2.addItem(col.label)
            self.treatment_box_2.addItem(col.label)
            self.control_box_3.addItem(col.label)
            self.treatment_box_3.addItem(col.label)

        self.box_1_label = QLabel("")
        self.box_2_label = QLabel("")
        self.box_3_label = QLabel("")
        self.data_location_layout.addWidget(self.control_label, 0, 1)
        self.data_location_layout.addWidget(self.treatment_label, 0, 2)
        self.data_location_layout.addWidget(self.box_1_label, 1, 0)
        self.data_location_layout.addWidget(self.control_box_1, 1, 1)
        self.data_location_layout.addWidget(self.treatment_box_1, 1, 2)
        self.data_location_layout.addWidget(self.box_2_label, 2, 0)
        self.data_location_layout.addWidget(self.control_box_2, 2, 1)
        self.data_location_layout.addWidget(self.treatment_box_2, 2, 2)
        self.data_location_layout.addWidget(self.box_3_label, 3, 0)
        self.data_location_layout.addWidget(self.control_box_3, 3, 1)
        self.data_location_layout.addWidget(self.treatment_box_3, 3, 2)

        data_location_box.setLayout(self.data_location_layout)

        options_layout = QHBoxLayout()
        options_layout.addWidget(data_type_box)
        options_layout.addWidget(effect_size_box)
        options_layout.addWidget(data_location_box)

        polarity_box = QGroupBox(get_text("Effect Size Polarity"))
        polarity_layout = QVBoxLayout()
        self.polarity_checkbox = QCheckBox(get_text("Indicate Polarity"))
        self.polarity_checkbox.clicked.connect(self.polarity_change)
        polarity_layout.addWidget(self.polarity_checkbox)
        self.polarity_choice_box = QComboBox()
        for col in data.cols:
            self.polarity_choice_box.addItem(col.label)
        polarity_layout.addWidget(self.polarity_choice_box)
        polarity_layout.addStretch(1)
        polarity_box.setLayout(polarity_layout)

        options_layout.addWidget(polarity_box)

        self.data_type_change()
        self.polarity_change()

        button_layout, _ = add_ok_cancel_help_button_layout(self)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Calculate Effect Sizes"))

    def show_help(self):
        webbrowser.open(self.help)

    def data_type_change(self):
        if self.means_button.isChecked():
            self.effect_choice1.setText("Hedges\' d")
            self.effect_choice2.setText("ln Response Ratio")
            self.effect_choice2.setVisible(True)
            self.effect_choice3.setVisible(False)
            self.control_label.setText(get_text("Control"))
            self.treatment_label.setText(get_text("Treatment"))
            self.control_box_2.setVisible(True)
            self.treatment_box_2.setVisible(True)
            self.control_box_3.setVisible(True)
            self.treatment_box_3.setVisible(True)
            self.box_1_label.setText(get_text("Mean"))
            self.box_2_label.setText(get_text("Standard Deviation"))
            self.box_3_label.setText(get_text("Sample Size"))
            self.box_1_label.setVisible(True)
            self.box_2_label.setVisible(True)
            self.box_3_label.setVisible(True)
            self.data_location_layout.setRowStretch(3, 0)
        elif self.twoxtwo_button.isChecked():
            self.effect_choice1.setText("ln Odds Ratio")
            self.effect_choice2.setText("Rate Difference")
            self.effect_choice3.setText("ln Relative Rate")
            self.effect_choice2.setVisible(True)
            self.effect_choice3.setVisible(True)
            self.control_label.setText(get_text("Control"))
            self.treatment_label.setText(get_text("Treatment"))
            self.control_box_2.setVisible(True)
            self.treatment_box_2.setVisible(True)
            self.control_box_3.setVisible(False)
            self.treatment_box_3.setVisible(False)
            self.box_1_label.setText(get_text("Response"))
            self.box_2_label.setText(get_text("No Response"))
            self.box_1_label.setVisible(True)
            self.box_2_label.setVisible(True)
            self.box_3_label.setVisible(False)
            self.data_location_layout.setRowStretch(3, 1)
        elif self.correlation_button.isChecked():
            self.effect_choice1.setText("Fisher\'s Z-transform")
            self.effect_choice2.setVisible(False)
            self.effect_choice3.setVisible(False)
            self.control_label.setText(get_text("Correlation"))
            self.treatment_label.setText(get_text("Sample Size"))
            self.control_box_2.setVisible(False)
            self.treatment_box_2.setVisible(False)
            self.control_box_3.setVisible(False)
            self.treatment_box_3.setVisible(False)
            self.box_1_label.setVisible(False)
            self.box_2_label.setVisible(False)
            self.box_3_label.setVisible(False)
            self.data_location_layout.setRowStretch(3, 1)
        elif self.probability_button.isChecked():
            self.effect_choice1.setText("Logit")
            self.effect_choice2.setVisible(False)
            self.effect_choice3.setVisible(False)
            self.control_label.setText(get_text("Probability"))
            self.treatment_label.setText(get_text("Sample Size"))
            self.control_box_2.setVisible(False)
            self.treatment_box_2.setVisible(False)
            self.control_box_3.setVisible(False)
            self.treatment_box_3.setVisible(False)
            self.box_1_label.setVisible(False)
            self.box_2_label.setVisible(False)
            self.box_3_label.setVisible(False)
            self.data_location_layout.setRowStretch(3, 1)
        self.effect_choice1.setChecked(True)

    def polarity_change(self):
        if self.polarity_checkbox.isChecked():
            self.polarity_choice_box.setEnabled(True)
        else:
            self.polarity_choice_box.setEnabled(False)

    def return_options(self) -> EffectSizeOptions:
        options = EffectSizeOptions()
        if self.means_button.isChecked():
            if self.effect_choice1.isChecked():
                options.effect_size = MetaWinEffectFunctions.hedges_d_function()
            elif self.effect_choice2.isChecked():
                options.effect_size = MetaWinEffectFunctions.ln_rr_function()
            options.control_means = self.columns[self.control_box_1.currentIndex()]
            options.treatment_means = self.columns[self.treatment_box_1.currentIndex()]
            options.control_sd = self.columns[self.control_box_2.currentIndex()]
            options.treatment_sd = self.columns[self.treatment_box_2.currentIndex()]
            options.control_n = self.columns[self.control_box_3.currentIndex()]
            options.treatment_n = self.columns[self.treatment_box_3.currentIndex()]
        elif self.twoxtwo_button.isChecked():
            if self.effect_choice1.isChecked():
                options.effect_size = MetaWinEffectFunctions.odds_ratio_function()
            elif self.effect_choice2.isChecked():
                options.effect_size = MetaWinEffectFunctions.rate_difference_function()
            elif self.effect_choice3.isChecked():
                options.effect_size = MetaWinEffectFunctions.relative_rate_function()
            options.control_response = self.columns[self.control_box_1.currentIndex()]
            options.control_no_response = self.columns[self.treatment_box_1.currentIndex()]
            options.treatment_response = self.columns[self.control_box_2.currentIndex()]
            options.treatment_no_response = self.columns[self.treatment_box_2.currentIndex()]
        elif self.correlation_button.isChecked():
            options.effect_size = MetaWinEffectFunctions.fishers_z_function()
            options.correlation = self.columns[self.control_box_1.currentIndex()]
            options.correlation_n = self.columns[self.treatment_box_1.currentIndex()]
        elif self.probability_button.isChecked():
            options.effect_size = MetaWinEffectFunctions.logit_function()
            options.probability = self.columns[self.control_box_1.currentIndex()]
            options.probability_n = self.columns[self.treatment_box_1.currentIndex()]
        if self.polarity_checkbox.isChecked():
            options.polarity = self.columns[self.polarity_choice_box.currentIndex()]
        return options


def do_effect_calculations(data: MetaWinData, options: EffectSizeOptions, decimal_places: int = 4):
    """
    general effect size calculation function, uses the input options to create new columns and fill them
    with calculated values
    """
    output_blocks, citations = options.report_choices()
    name = options.effect_size.name
    i = 0
    while name in data.column_labels():
        i += 1
        name = options.effect_size.name + " ({})".format(i)
    eff_col = data.add_col(name)
    eff_col.effect_size = options.effect_size
    eff_num = data.col_number(eff_col)
    var_col = data.add_col("Var({})".format(name))
    var_num = data.col_number(var_col)
    eff_col.effect_var = var_col
    tmp_output = []
    error_row = []
    for row in range(data.nrows()):
        e, v = options.effect_size.calculate(data, row, options)
        if (e is None) or (v is None):
            tmp_output.append([data.rows[row].label, None, None])
            error_row.append(True)
        else:
            data.add_value(row, eff_num, e)
            data.add_value(row, var_num, v)
            tmp_output.append([data.rows[row].label, e, v])
            error_row.append(False)
    output = []
    col_headers = [get_text("Study"), options.effect_size.name, "var({})".format(options.effect_size.name)]
    col_formats = ["", "f", "f"]
    create_output_table(output, tmp_output, col_headers, col_formats, decimal_places, error_row=error_row,
                        error_msg=get_text("No effect size could be calculated"))
    output_blocks.append(output)
    output_blocks.extend(create_reference_list(citations))

    return output_blocks, eff_col, var_col


def calculate_effect_sizes(sender, data: MetaWinData, decimal_places: int = 4):
    """
    function to call effect size options dialog, then feed those choices into the calculation function
    """
    sender.effect_size_dialog = EffectSizesDialog(data)
    if sender.effect_size_dialog.exec():
        options = sender.effect_size_dialog.return_options()
        return do_effect_calculations(data, options, decimal_places)
    return None, None, None
