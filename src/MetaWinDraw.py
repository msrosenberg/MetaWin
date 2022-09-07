"""
Module for directly creating figures (as opposed to those that come out of specific analyses).

Each figure  type has a function which calls the dialog and a separate function which sets up the figures based on
choices from the dialog (or which have been programmatically created), allowing one to skip the dialogs to
directly create an instance of a figure

The actual plotting of the figures is done by the MetaWinCharts module
"""
import webbrowser
import math
from typing import Tuple

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QFrame, QComboBox, QGroupBox, QLineEdit, QRadioButton, \
    QGridLayout
from PyQt6.QtGui import QIcon, QIntValidator
import numpy
import scipy.stats

import MetaWinMessages
from MetaWinData import MetaWinData
import MetaWinConstants
from MetaWinConstants import mean_data_tuple
from MetaWinWidgets import add_ok_cancel_help_button_layout, add_effect_choice_to_dialog
import MetaWinCharts
from MetaWinLanguage import get_text


class MetaAnalysisDrawScatterDialog(QDialog):
    def __init__(self, data: MetaWinData):
        super().__init__()
        self.help = MetaWinConstants.help_index["scatter_plot"]
        self.x_box = None
        self.y_box = None
        self.columns = None
        self.init_ui(data)

    def init_ui(self, data: MetaWinData):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        draw_label = QLabel(get_text("Scatter/Funnel Plot"))
        draw_label.setStyleSheet(MetaWinConstants.title_label_style)

        self.columns = data.cols
        self.x_box = QComboBox()
        self.y_box = QComboBox()
        self.columns = data.cols
        for col in self.columns:
            self.x_box.addItem(col.label)
            self.y_box.addItem(col.label)
        x_label = QLabel(get_text("Data for X-axis"))
        y_label = QLabel(get_text("Data for Y-axis"))
        info_label = QLabel(get_text("note_funnel_plot"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(x_label)
        options_layout.addWidget(self.x_box)
        options_layout.addWidget(y_label)
        options_layout.addWidget(self.y_box)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(draw_label)
        main_layout.addWidget(main_frame)
        main_layout.addWidget(info_label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Scatter/Funnel Plot"))

    def show_help(self):
        webbrowser.open(self.help)


class MetaAnalysisDrawNormalQuantileDialog(QDialog):
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["normal_quantile_plot"]
        self.effect_size_box = None
        self.variance_box = None
        self.columns = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        draw_label = QLabel(get_text("Normal Quantile Plot"))
        draw_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var,
                                                                        include_log=False)

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(draw_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Normal Quantile Plot"))

    def show_help(self):
        webbrowser.open(self.help)


class MetaAnalysisDrawRadialDialog(QDialog):
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["galbraith_plot"]
        self.effect_size_box = None
        self.variance_box = None
        self.columns = None
        self.log_transform_box = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        draw_label = QLabel(get_text("Galbraith (Radial) Plot"))
        draw_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var)

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)
        options_layout.addWidget(self.log_transform_box)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(draw_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Galbraith (Radial) Plot"))

    def show_help(self):
        webbrowser.open(self.help)


class MetaAnalysisDrawHistogramDialog(QDialog):
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["weighted_histogram"]
        self.effect_size_box = None
        self.weight_box = None
        self.columns = None
        self.weight_none = None
        self.weight_n = None
        self.weight_var = None
        self.bin_edit = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        draw_label = QLabel(get_text("Weighted Histogram"))
        draw_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label = QLabel(get_text("Effect Size"))
        self.effect_size_box = QComboBox()
        self.weight_box = QComboBox()
        self.columns = data.cols
        for col in self.columns:
            self.effect_size_box.addItem(col.label)
            self.weight_box.addItem(col.label)
        if last_effect is not None:
            if last_var is None:
                last_var = last_effect.effect_var
            for c, col in enumerate(self.columns):
                if col == last_effect:
                    self.effect_size_box.setCurrentIndex(c)
                elif col == last_var:
                    self.weight_box.setCurrentIndex(c)

        w_group_box = QGroupBox(get_text("Weighting"))
        weight_layout = QVBoxLayout()
        self.weight_none = QRadioButton(get_text("No Weighting"))
        self.weight_none.clicked.connect(self.change_weight)
        self.weight_var = QRadioButton(get_text("Inverse Variance"))
        self.weight_var.clicked.connect(self.change_weight)
        self.weight_n = QRadioButton(get_text("Sample Size"))
        self.weight_n.clicked.connect(self.change_weight)
        weight_layout.addWidget(self.weight_none)
        weight_layout.addWidget(self.weight_var)
        weight_layout.addWidget(self.weight_n)
        weight_layout.addWidget(self.weight_box)
        w_group_box.setLayout(weight_layout)
        self.weight_none.setChecked(True)
        self.change_weight()

        self.bin_edit = QLineEdit()
        self.bin_edit.setText("10")
        self.bin_edit.setValidator(QIntValidator(1, 1000))
        bin_label = QLabel(get_text("Number of Bins"))

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(bin_label)
        options_layout.addWidget(self.bin_edit)
        options_layout.addWidget(w_group_box)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(draw_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Weighted Histogram"))

    def show_help(self):
        webbrowser.open(self.help)

    def change_weight(self):
        if self.weight_none.isChecked():
            self.weight_box.setEnabled(False)
        else:
            self.weight_box.setEnabled(True)


class MetaAnalysisDrawForestDialog(QDialog):
    def __init__(self, data: MetaWinData, last_effect, last_var):
        super().__init__()
        self.help = MetaWinConstants.help_index["forest_plot"]
        self.effect_size_box = None
        self.variance_box = None
        self.columns = None
        self.init_ui(data, last_effect, last_var)

    def init_ui(self, data: MetaWinData, last_effect, last_var):
        button_layout, _ = add_ok_cancel_help_button_layout(self)

        draw_label = QLabel(get_text("Forest Plot"))
        draw_label.setStyleSheet(MetaWinConstants.title_label_style)

        effect_size_label, variance_label = add_effect_choice_to_dialog(self, data, last_effect, last_var,
                                                                        include_log=False)

        options_layout = QVBoxLayout()
        options_layout.addWidget(effect_size_label)
        options_layout.addWidget(self.effect_size_box)
        options_layout.addWidget(variance_label)
        options_layout.addWidget(self.variance_box)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(options_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(draw_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Forest Plot"))

    def show_help(self):
        webbrowser.open(self.help)


class MetaAnalysisEditFigure(QDialog):
    def __init__(self, chart_data):
        super().__init__()
        self.help = "graph_edit"
        self.chart_data = None
        self.x_box = None
        self.y_box = None
        self.panel_list = []
        self.init_ui(chart_data)

    def init_ui(self, chart_data):
        self.chart_data = chart_data
        button_layout, ok_button = add_ok_cancel_help_button_layout(self)
        ok_button.clicked.connect(self.ok_clicked)
        main_layout = QVBoxLayout()

        title_groupbox = QGroupBox(get_text("Axes Titles"))
        title_layout = QGridLayout()
        x_label = QLabel(get_text("Horizontal Axis"))
        self.x_box = QLineEdit()
        self.x_box.setText(chart_data.x_label)
        title_layout.addWidget(x_label, 0, 0)
        title_layout.addWidget(self.x_box, 1, 0)
        if not chart_data.suppress_y:
            y_label = QLabel(get_text("Vertical Axis"))
            self.y_box = QLineEdit()
            self.y_box.setText(chart_data.y_label)
            title_layout.addWidget(y_label, 0, 1)
            title_layout.addWidget(self.y_box, 1, 1)
        title_groupbox.setLayout(title_layout)
        main_layout.addWidget(title_groupbox)

        for data in chart_data.data:
            edit_panel = data.create_edit_panel()
            if edit_panel is not None:
                main_layout.addWidget(edit_panel)
                self.panel_list.append(edit_panel)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Edit Figure"))

    def show_help(self):
        webbrowser.open(self.help)

    def ok_clicked(self):
        self.chart_data.x_label = self.x_box.text()
        if not self.chart_data.suppress_y:
            self.chart_data.y_label = self.y_box.text()
        for edit_panel in self.panel_list:
            if edit_panel.isChecked():
                edit_panel.data.visible = True
                edit_panel.data.update_style()
            else:
                edit_panel.data.visible = False
        self.accept()


def draw_scatter_plot(data, x_data_col, y_data_col):
    x_data = []
    y_data = []
    bad_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            x = data.check_value(r, x_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            y = data.check_value(r, y_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if (x is not None) and (y is not None):
                x_data.append(x)
                y_data.append(y)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)

    if len(x_data) > 0:
        x_data = numpy.array(x_data)
        y_data = numpy.array(y_data)
        figure, chart_data = MetaWinCharts.chart_scatter(x_data, y_data, x_data_col.label, y_data_col.label)
        # fig_caption = get_text("Scatter plot of {} vs. {}.").format(y_data_col.label, x_data_col.label)
        return figure, chart_data
    return None, None


def draw_scatter_dialog(sender, data):
    sender.draw_dialog = MetaAnalysisDrawScatterDialog(data)
    if sender.draw_dialog.exec():
        x_data_col = sender.draw_dialog.columns[sender.draw_dialog.x_box.currentIndex()]
        y_data_col = sender.draw_dialog.columns[sender.draw_dialog.y_box.currentIndex()]
        figure, chart_data = draw_scatter_plot(data, x_data_col, y_data_col)
        if figure is not None:
            return figure, chart_data
        else:
            MetaWinMessages.report_critical(sender, "Error", "No valid data found for given options.")
    return None, None


def calculate_regression(x: numpy.array, y: numpy.array) -> Tuple[float, float]:
    """
    Basic linear regression of y vs x, returning slope and intercept
    """
    n = len(x)
    sum_y = numpy.sum(y)
    sum_x = numpy.sum(x)
    mean_y = sum_y/n
    mean_x = sum_x/n
    sum_x2 = numpy.sum(numpy.square(x))
    sum_xy = numpy.sum(x*y)
    slope = (n*sum_xy - sum_x*sum_y)/(n*sum_x2 - sum_x**2)
    intercept = mean_y - slope*mean_x
    return slope, intercept


def draw_normal_quantile_plot(data, e_data_col, v_data_col, alpha: float = 0.05):
    y_data = []
    bad_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, e_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, v_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if (e is not None) and (v is not None) and (v > 0):
                y_data.append(e/math.sqrt(v))
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)

    n = len(y_data)
    if n > 0:
        y_data.sort()
        x_data = [scipy.stats.norm.ppf((i + 0.5)/n) for i in range(n)]

        x_data = numpy.array(x_data)
        y_data = numpy.array(y_data)
        slope, intercept = calculate_regression(x_data, y_data)

        figure, chart_data = MetaWinCharts.chart_normal_quantile(get_text("Normal Quantile"),
                                                                 get_text("Standardized Effect Size"),
                                                                 x_data, y_data, slope, intercept, alpha)
        # fig_caption = get_text("normal_quantile_caption").format(get_citation("Wang_and_Bushman_1998")) + \
        #               create_reference_list(["Wang_and_Bushman_1998"], True)

        return figure, chart_data
    return None, None


def draw_normal_quantile_dialog(sender, data, last_effect, last_var, alpha: float = 0.05):
    sender.draw_dialog = MetaAnalysisDrawNormalQuantileDialog(data, last_effect, last_var)
    if sender.draw_dialog.exec():
        e_data_col = sender.draw_dialog.columns[sender.draw_dialog.effect_size_box.currentIndex()]
        v_data_col = sender.draw_dialog.columns[sender.draw_dialog.variance_box.currentIndex()]
        figure, chart_data = draw_normal_quantile_plot(data, e_data_col, v_data_col, alpha)
        if figure is not None:
            return figure, chart_data
        else:
            MetaWinMessages.report_critical(sender, "Error", "No valid data found for given options.")
    return None, None


def draw_radial_plot(data, e_data_col, v_data_col, is_log: bool = False):
    x_data = []
    y_data = []
    tmp_e = []
    bad_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, e_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, v_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if (e is not None) and (v is not None) and (v > 0):
                x_data.append(math.sqrt(1/v))
                y_data.append(e*math.sqrt(1/v))
                tmp_e.append(e)
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)

    if len(x_data) > 0:
        x_data = numpy.array(x_data)
        y_data = numpy.array(y_data)
        max_e = max(tmp_e)
        min_e = min(tmp_e)

        # calculate a regression through the origin, rather than with an intercept
        slope_through_origin = numpy.sum(x_data*y_data)/numpy.sum(numpy.square(x_data))

        figure, chart_data = MetaWinCharts.chart_radial(e_data_col.label, x_data, y_data, slope_through_origin, min_e,
                                                        max_e, is_log)
        # fig_caption = get_text("Radial_chart_caption").format(e_data_col.label)
        # fig_caption += create_reference_list(["Galbraith_1988", "Galbraith_1994"], True)
        return figure, chart_data
    return None, None


def draw_radial_dialog(sender, data, last_effect, last_var):
    sender.draw_dialog = MetaAnalysisDrawRadialDialog(data, last_effect, last_var)
    if sender.draw_dialog.exec():
        e_data_col = sender.draw_dialog.columns[sender.draw_dialog.effect_size_box.currentIndex()]
        v_data_col = sender.draw_dialog.columns[sender.draw_dialog.variance_box.currentIndex()]
        is_log = sender.draw_dialog.log_transform_box.isChecked()
        figure, chart_data = draw_radial_plot(data, e_data_col, v_data_col, is_log)
        if figure is not None:
            return figure, chart_data
        else:
            MetaWinMessages.report_critical(sender, "Error", "No valid data found for given options.")
    return None, None


def draw_histogram_plot(data, e_data_col, w_data_col, weight_type, n_bins: int):
    e_data = []
    w_data = []
    bad_data = []
    filtered = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, e_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if weight_type != MetaWinCharts.WEIGHT_NONE:
                w = data.check_value(r, w_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
                if (e is not None) and (w is not None):
                    if weight_type == MetaWinCharts.WEIGHT_INVVAR:
                        if w > 0:
                            w_data.append(1/w)
                            e_data.append(e)
                        else:
                            bad_data.append(row.label)
                    else:
                        w_data.append(w)
                        e_data.append(e)
                else:
                    bad_data.append(row.label)
            elif e is not None:
                e_data.append(e)
                w_data.append(1)
        else:
            filtered.append(row.label)

    if len(e_data) > 0:
        e_data = numpy.array(e_data)
        w_data = numpy.array(w_data)
        figure, chart_data = MetaWinCharts.chart_histogram(e_data, w_data, n_bins, e_data_col.label, weight_type)
        return figure, chart_data
    return None, None


def draw_histogram_dialog(sender, data, last_effect, last_var):
    sender.draw_dialog = MetaAnalysisDrawHistogramDialog(data, last_effect, last_var)
    if sender.draw_dialog.exec():
        e_data_col = sender.draw_dialog.columns[sender.draw_dialog.effect_size_box.currentIndex()]
        w_data_col = sender.draw_dialog.columns[sender.draw_dialog.weight_box.currentIndex()]
        if sender.draw_dialog.weight_var.isChecked():
            weight_type = MetaWinCharts.WEIGHT_INVVAR
        elif sender.draw_dialog.weight_n.isChecked():
            weight_type = MetaWinCharts.WEIGHT_N
        else:
            weight_type = MetaWinCharts.WEIGHT_NONE
        n_bins = int(sender.draw_dialog.bin_edit.text())
        figure, chart_data = draw_histogram_plot(data, e_data_col, w_data_col, weight_type, n_bins)
        if figure is not None:
            return figure, chart_data
        else:
            MetaWinMessages.report_critical(sender, "Error", "No valid data found for given options.")
    return None, None


def draw_forest_plot(data, e_data_col, v_data_col, alpha: float = 0.05):
    bad_data = []
    filtered = []
    y = 0
    data_list = []
    for r, row in enumerate(data.rows):
        if row.not_filtered():
            e = data.check_value(r, e_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            v = data.check_value(r, v_data_col.position(), value_type=MetaWinConstants.VALUE_NUMBER)
            if (e is not None) and (v is not None) and (v > 0):
                y += 1
                tmp_lower, tmp_upper = scipy.stats.norm.interval(alpha=1 - alpha, loc=e, scale=math.sqrt(v))
                data_list.append(mean_data_tuple(row.label, y, 0, e, None, 0, 0, tmp_lower, tmp_upper, 0, 0, 0, 0))
            else:
                bad_data.append(row.label)
        else:
            filtered.append(row.label)

    figure, chart_data = MetaWinCharts.chart_forest_plot("forest plot", e_data_col.label, data_list, alpha, None)

    # fig_caption = get_text("Forest plot of individual effect sizes for each study.") + \
    #               MetaWinCharts.common_forest_plot_caption(e_data_col.label, alpha, inc_median=False)
    return figure, chart_data


def draw_forest_dialog(sender, data, last_effect, last_var, alpha: float = 0.05):
    sender.draw_dialog = MetaAnalysisDrawForestDialog(data, last_effect, last_var)
    if sender.draw_dialog.exec():
        e_data_col = sender.draw_dialog.columns[sender.draw_dialog.effect_size_box.currentIndex()]
        v_data_col = sender.draw_dialog.columns[sender.draw_dialog.variance_box.currentIndex()]
        figure, chart_data = draw_forest_plot(data, e_data_col, v_data_col, alpha)
        if figure is not None:
            return figure, chart_data
        else:
            MetaWinMessages.report_critical(sender, "Error", "No valid data found for given options.")
    return None, None


def edit_figure(sender, chart_data):
    sender.edit_fig_dialog = MetaAnalysisEditFigure(chart_data)
    if sender.edit_fig_dialog.exec():
        return MetaWinCharts.create_figure(chart_data)
    return None
