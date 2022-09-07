"""
Module for creating figures using the matplotlib backend for Qt
"""

import math
from typing import Optional, Tuple, Union

from matplotlib import patches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy
import scipy.stats

from MetaWinUtils import exponential_label, get_citation, create_reference_list
from MetaWinLanguage import get_text
import MetaWinWidgets


# weighting options for the histograms
WEIGHT_NONE = 0
WEIGHT_INVVAR = 1
WEIGHT_N = 2

LINE_STYLES = ("solid", "dashed", "dotted", "dashdot")
# MARKER_STYLES = {"point": ".", "circle": "o", "downward triangle": "v", "upward triangle": "^",
#                  "left triangle": "<", "right triangle": ">", "downard tri": "1", "upward tri": "2", "left tri": "3",
#                  "right tri": "4", "octagon": "8", "square": "s", "pentagon": "p", "filled plus": "P",
#                  "star": "*", "upward hexagon": "h", "sideways hexagon": "H", "plus": "+", "X": "x", "filled X": "X",
#                  "diamond": "D", "thin diamond": "d", "vertical line": "|", "horizontal line": "_", "tick left": 0,
#                  "tick right": 1, "tick up": 2, "tick down": 3, "upward caret": 6, "downward caret": 7,
#                  "left caret": 4, "right caret": 5, "centered upward caret": 10, "centered downward caret": 11,
#                  "centered left caret": 8, "centered right caret": 9}
MARKER_STYLES = {"point": ".", "circle": "o", "downward triangle": "v", "upward triangle": "^",
                 "left triangle": "<", "right triangle": ">", "octagon": "8", "square": "s", "pentagon": "p",
                 "filled plus": "P", "star": "*", "upward hexagon": "h", "sideways hexagon": "H", "plus": "+",
                 "X": "x", "filled X": "X", "diamond": "D", "thin diamond": "d", "vertical line": "|",
                 "horizontal line": "_", "tick left": 0, "tick right": 1, "tick up": 2, "tick down": 3,
                 "upward caret": 6, "downward caret": 7, "left caret": 4, "right caret": 5,
                 "centered upward caret": 10, "centered downward caret": 11, "centered left caret": 8,
                 "centered right caret": 9}


# ---------- Chart Data Classes ---------- #
class BaseChartData:
    def __init__(self):
        self.name = ""
        self.visible = True


class ScatterData(BaseChartData):
    """
    an object to contain scatter plot data
    """
    def __init__(self):
        super().__init__()
        self.x = []
        self.y = []
        # scatter point style
        self.marker = "o"
        self.color = "#1f77b4"
        self.edgecolors = "#1f77b4"
        self.size = 36
        self.linewidths = 1.5
        self.linestyle = "dotted"
        self.label = ""
        self.zorder = 0
        self.edit_panel = None
        self.edgecolor_button = None
        self.linewidth_box = None
        self.linestyle_box = None
        self.color_button = None
        self.size_box = None
        self.marker_box = None
        self.no_fill_box = None

    def export_to_list(self) -> list:
        outlist = ["Scatter Plot Data\n",
                   "Name\t{}\n".format(self.name),
                   "x\ty\n"]
        for i in range(len(self.x)):
            outlist.append("{}\t{}\n".format(self.x[i], self.y[i]))
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)

        self.color_button, color_label, self.no_fill_box = MetaWinWidgets.add_chart_color_button(get_text("Color"),
                                                                                                 self.color,
                                                                                                 self.edgecolors)
        self.no_fill_box.clicked.connect(self.no_fill_clicked)
        self.no_fill_clicked()
        edit_layout.addWidget(color_label, 0, 0)
        edit_layout.addWidget(self.color_button, 1, 0)
        edit_layout.addWidget(self.no_fill_box, 2, 0)
        self.marker_box, marker_label = MetaWinWidgets.add_chart_marker_style(get_text("Shape"), self.marker,
                                                                              MARKER_STYLES)
        edit_layout.addWidget(marker_label, 0, 1)
        edit_layout.addWidget(self.marker_box, 1, 1)

        self.size_box, size_label = MetaWinWidgets.add_chart_marker_size("Size", self.size)
        edit_layout.addWidget(size_label, 0, 2)
        edit_layout.addWidget(self.size_box, 1, 2)

        (self.edgecolor_button, edgecolor_label, self.linewidth_box, width_label,
         self.linestyle_box, style_label) = MetaWinWidgets.add_chart_line_edits(get_text("Edge Color"), self.edgecolors,
                                                                                get_text("Edge Width"), self.linewidths,
                                                                                get_text("Edge Style"), self.linestyle,
                                                                                LINE_STYLES)
        edit_layout.addWidget(edgecolor_label, 0, 3)
        edit_layout.addWidget(self.edgecolor_button, 1, 3)
        edit_layout.addWidget(width_label, 0, 4)
        edit_layout.addWidget(self.linewidth_box, 1, 4)
        edit_layout.addWidget(style_label, 0, 5)
        edit_layout.addWidget(self.linestyle_box, 1, 5)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def no_fill_clicked(self):
        if self.no_fill_box.isChecked():
            self.color_button.setEnabled(False)
        else:
            self.color_button.setEnabled(True)

    def update_style(self):
        self.linestyle = self.linestyle_box.currentText()
        self.linewidths = float(self.linewidth_box.text())
        self.edgecolors = self.edgecolor_button.color
        if self.no_fill_box.isChecked():
            self.color = "none"
        else:
            self.color = self.color_button.color
        self.size = float(self.size_box.text())
        self.marker = MARKER_STYLES[self.marker_box.currentText()]


class HistogramData(BaseChartData):
    """
    an object to contain histogram bins
    """
    def __init__(self):
        super().__init__()
        self.counts = None
        self.bins = None
        # style
        self.color = "#1f77b4"
        self.linewidth = 1
        self.linestyle = "solid"
        self.edgecolor = "black"
        # style editing
        self.edit_panel = None
        self.edgewidth_box = None
        self.edgestyle_box = None
        self.bar_color_button = None
        self.edge_color_button = None

    def export_to_list(self) -> list:
        outlist = ["Histogram Data\n",
                   "Name\t{}\n".format(self.name),
                   "count\tlower\tupper\n"]
        for i in range(len(self.counts)):
            outlist.append("{}\t{}\t{}\n".format(self.counts[i], self.bins[i], self.bins[i+1]))
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        self.bar_color_button, label, _ = MetaWinWidgets.add_chart_color_button(get_text("Bar Color"), self.color)
        edit_layout.addWidget(label, 0, 0)
        edit_layout.addWidget(self.bar_color_button, 1, 0)
        (self.edge_color_button, color_label, self.edgewidth_box, width_label,
         self.edgestyle_box, style_label) = MetaWinWidgets.add_chart_line_edits(get_text("Edge Color"),
                                                                                self.edgecolor,
                                                                                get_text("Edge Width"),
                                                                                self.linewidth,
                                                                                get_text("Edge Style"),
                                                                                self.linestyle,
                                                                                LINE_STYLES)
        edit_layout.addWidget(color_label, 0, 1)
        edit_layout.addWidget(self.edge_color_button, 1, 1)
        edit_layout.addWidget(width_label, 0, 2)
        edit_layout.addWidget(self.edgewidth_box, 1, 2)
        edit_layout.addWidget(style_label, 0, 3)
        edit_layout.addWidget(self.edgestyle_box, 1, 3)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.linestyle = self.edgestyle_box.currentText()
        self.linewidth = float(self.edgewidth_box.text())
        self.color = self.bar_color_button.color
        self.edgecolor = self.edge_color_button.color


class LabelData(BaseChartData):
    """
    an object to contain a list of labels
    """
    def __init__(self):
        super().__init__()
        self.labels = None
        self.y_pos = None
        self.edit_panel = None

    def export_to_list(self) -> list:
        outlist = ["Data Labels\n",
                   "Name\t{}\n".format(self.name),
                   "Y-position\tLabel\n"]
        for i in range(len(self.labels)):
            outlist.append("{}\t{}\n".format(self.y_pos[i], self.labels[i]))
        return outlist

    def create_edit_panel(self):
        return self.edit_panel


class ForestCIData(BaseChartData):
    """
    an object to contain confidence intervals for a forest plot
    """
    def __init__(self):
        super().__init__()
        self.min_x = None
        self.max_x = None
        self.y = None
        # style
        self.linestyle = "solid"
        self.color = "#1f77b4"
        self.linewidth = 1.5
        self.zorder = 0
        self.edit_panel = None
        self.color_button = None
        self.linestyle_box = None
        self.linewidth_box = None

    def export_to_list(self) -> list:
        outlist = ["Forest Plot CI Data\n",
                   "Name\t{}\n".format(self.name),
                   "lower\tupper\ty\n"]
        for i in range(len(self.y)):
            outlist.append("{}\t{}\t{}\n".format(self.min_x[i], self.max_x[i], self.y[i]))
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        (self.color_button, color_label, self.linewidth_box, width_label,
         self.linestyle_box, style_label) = MetaWinWidgets.add_chart_line_edits(get_text("Color"), self.color,
                                                                                get_text("Width"), self.linewidth,
                                                                                get_text("Style"), self.linestyle,
                                                                                LINE_STYLES)
        edit_layout.addWidget(color_label, 0, 0)
        edit_layout.addWidget(self.color_button, 1, 0)
        edit_layout.addWidget(width_label, 0, 1)
        edit_layout.addWidget(self.linewidth_box, 1, 1)
        edit_layout.addWidget(style_label, 0, 2)
        edit_layout.addWidget(self.linestyle_box, 1, 2)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.linestyle = self.linestyle_box.currentText()
        self.linewidth = float(self.linewidth_box.text())
        self.color = self.color_button.color


class LineData(BaseChartData):
    """
    an object to contain a line with one or more segments
    """
    def __init__(self):
        super().__init__()
        self.x_values = None
        self.y_values = None
        # style
        self.linestyle = "solid"
        self.color = "silver"
        self.linewidth = 1.5
        self.zorder = 0
        self.edit_panel = None
        self.color_button = None
        self.linewidth_box = None
        self.linestyle_box = None

    def export_to_list(self) -> list:
        outlist = ["Line Data\n",
                   "Name\t{}\n".format(self.name),
                   "x\ty\n"]
        for i in range(len(self.x_values)):
            outlist.append("{}\t{}\n".format(self.x_values[i], self.y_values[i]))
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        (self.color_button, color_label, self.linewidth_box, width_label,
         self.linestyle_box, style_label) = MetaWinWidgets.add_chart_line_edits(get_text("Color"), self.color,
                                                                                get_text("Width"), self.linewidth,
                                                                                get_text("Style"), self.linestyle,
                                                                                LINE_STYLES)
        edit_layout.addWidget(color_label, 0, 0)
        edit_layout.addWidget(self.color_button, 1, 0)
        edit_layout.addWidget(width_label, 0, 1)
        edit_layout.addWidget(self.linewidth_box, 1, 1)
        edit_layout.addWidget(style_label, 0, 2)
        edit_layout.addWidget(self.linestyle_box, 1, 2)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.linestyle = self.linestyle_box.currentText()
        self.linewidth = float(self.linewidth_box.text())
        self.color = self.color_button.color


class ArcData(BaseChartData):
    """
    an object to contain an arc
    """
    def __init__(self):
        super().__init__()
        self.x_center = 0
        self.y_center = 0
        self.height = 0
        self.width = 0
        self.start_angle = 0
        self.end_angle = 0
        # style
        self.color = "silver"
        self.linestyle = "solid"
        self.linewidth = 1.5
        self.zorder = 0
        self.edit_panel = None
        self.color_button = None
        self.linewidth_box = None
        self.linestyle_box = None

    def export_to_list(self) -> list:
        outlist = ["Arc Data\n",
                   "Name\t{}\n".format(self.name),
                   "x\ty\twidth\theight\tstart angle\tend angle\n",
                   "{}\t{}\t{}\t{}\t{}\t{}\n".format(self.x_center, self.y_center, self.width, self.height,
                                                     self.start_angle, self.end_angle)]
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        (self.color_button, color_label, self.linewidth_box, width_label,
         self.linestyle_box, style_label) = MetaWinWidgets.add_chart_line_edits(get_text("Color"), self.color,
                                                                                get_text("Width"), self.linewidth,
                                                                                get_text("Style"), self.linestyle,
                                                                                LINE_STYLES)
        edit_layout.addWidget(color_label, 0, 0)
        edit_layout.addWidget(self.color_button, 1, 0)
        edit_layout.addWidget(width_label, 0, 1)
        edit_layout.addWidget(self.linewidth_box, 1, 1)
        edit_layout.addWidget(style_label, 0, 2)
        edit_layout.addWidget(self.linestyle_box, 1, 2)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.linestyle = self.linestyle_box.currentText()
        self.linewidth = float(self.linewidth_box.text())
        self.color = self.color_button.color


class AnnotationData(BaseChartData):
    """
    an object to contain figure annotations
    """
    def __init__(self):
        super().__init__()
        self.annotations = []
        self.x = None
        self.y = None
        self.edit_panel = None

    def export_to_list(self) -> list:
        outlist = ["Annotation Data\n",
                   "Name\t{}\n".format(self.name),
                   "x\ty\tAnnotation\n"]
        for i in range(len(self.annotations)):
            outlist.append("{}\t{}\t{}\n".format(self.x[i], self.y[i], self.annotations[i]))
        return outlist

    def create_edit_panel(self):
        return self.edit_panel


# ---------- Chart Caption Classes ---------- #
class NormalQuantileCaption:
    def __init__(self):
        self.upper_limit = None
        self.lower_limit = None
        self.horizontal_mean = None
        self.vertical_mean = None
        self.regression = None
        self.regression_scatter = None

    def __str__(self):
        "Normal Quantile plot following {}. The "
        "standardized effect size is the effect size divided by the "
        "square-root of its variance. The solid line represents the "
        "regression and the dashed lines the 95% prediction envelope."

        return get_text("normal_quantile_caption").format(get_citation("Wang_and_Bushman_1998")) + \
               create_reference_list(["Wang_and_Bushman_1998"], True)


class ScatterCaption:
    def __init__(self):
        self.x_label = ""
        self.y_label = ""

    def __str__(self):
        return get_text("Scatter plot of {} vs. {}.").format(self.y_label, self.x_label)


class HistogramCaption:
    def __init__(self):
        self.e_label = ""
        self.weight_type = WEIGHT_NONE

    def __str__(self):
        caption = get_text("Histogram of {} from individual studies.").format(self.e_label)
        if self.weight_type == WEIGHT_INVVAR:
            caption += get_text(" Counts were weighted by the inverse of the variance of each effect size.")
        elif self.weight_type == WEIGHT_N:
            caption += get_text(" Counts were weighted by a sample size associated with each effect size.")
        return caption


class RadialCaption:
    def __init__(self):
        self.e_label = ""

    def __str__(self):
        return get_text("Radial_chart_caption").format(self.e_label)


class ForestPlotBaseCaption:
    def __init__(self):
        self.e_label = ""
        self.alpha = 0.05
        self.bootstrap_n = None


class ForestPlotCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("Forest plot of individual effect sizes for each study.") + \
               common_forest_plot_caption(self.e_label, self.alpha, inc_median=False)


class RegressionCaption:
    def __init__(self):
        self.e_label = ""
        self.i_label = ""
        self.model = ""
        self.ref_list = ""
        self.citations = []

    def __str__(self):
        return get_text("regression_caption").format(self.e_label, self.i_label, self.model, self.ref_list) + \
                create_reference_list(self.citations, True)


class TrimAndFillCaption:
    def __init__(self):
        self.e_label = ""
        self.original_scatter = None
        self.inferred_scatter = None
        self.original_mean = None
        self.inferred_mean = None

    def __str__(self):
        "Funnel plot of {} vs. precision, showing the results of a Trim and "
        "Fill Analysis ({}). Solid black circles represent the original data; "
        "open red circles represent inferred \"missing\" data. The dashed line "
        "represents the mean effect size of the original data, the dotted line "
        "the mean effect size including the inferred data."
        new_cites = ["Duval_Tweedie_2000a", "Duval_Tweedie_2000b"]
        return get_text("trim_fill_caption").format(self.e_label, "Duval and Tweedie 2000a, b") + \
               create_reference_list(new_cites, True)


class BasicAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("Forest plot of individual effect sizes for each study, as well as the overall mean.") + \
               common_forest_plot_caption(self.e_label, self.alpha, self.bootstrap_n)


class GroupedAnalysisCaption(ForestPlotBaseCaption):
    def __init__(self):
        super().__init__()
        self.group_label = ""

    def __str__(self):
        return get_text("group_forest_plot").format(self.group_label) + \
               common_forest_plot_caption(self.e_label, self.alpha, self.bootstrap_n)


class NestedAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("nest_caption") + common_forest_plot_caption(self.e_label, self.alpha, self.bootstrap_n)


class CumulativeAnalysisCaption(ForestPlotBaseCaption):
    def __init__(self):
        super().__init__()
        self.order_label = ""

    def __str__(self):
        return get_text("cumulative_forest_plot").format(self.order_label) + \
               common_forest_plot_caption(self.e_label, self.alpha, self.bootstrap_n)


class JackknifeAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("jackknife_forest_plot") + common_forest_plot_caption(self.e_label, self.alpha,
                                                                              self.bootstrap_n)


def common_forest_plot_caption(effect_name: str, alpha: float = 0.05, bootstrap_n: Optional[int] = None,
                               inc_median: bool = True) -> str:
    # " Effect size measured as {}. The dotted vertical line "
    # "represents no effect, or a mean of zero. Circles represent "
    # "mean effect size, with the corresponding line "
    # "the {:0.0%} confidence interval."
    #
    text = get_text("forest_plot_common_caption").format(effect_name, 1 - alpha)
    if inc_median:
        text += get_text("forest_plot_median_caption")
    if bootstrap_n is not None:
        citation = "Adams_et_1997"
        text += get_text("bootstrap_caption").format(bootstrap_n, get_citation(citation)) + \
                create_reference_list([citation], True)
    return text


# ---------- Main Chart Data Class ---------- #
class ChartData:
    """
    an object to contain all data that appears on charts

    this will allow chart data exporting, as well as open up the possibility of figure editing
    """
    def __init__(self, caption_type):
        self.x_label = ""
        self.y_label = ""
        self.data = []
        # special adjustments
        self.suppress_y = False
        self.rescale_x = None
        # caption
        if caption_type == "normal quantile":
            self.caption = NormalQuantileCaption()
        elif caption_type == "scatter plot":
            self.caption = ScatterCaption()
        elif caption_type == "histogram":
            self.caption = HistogramCaption()
        elif caption_type == "radial":
            self.caption = RadialCaption()
        elif caption_type == "regression":
            self.caption = RegressionCaption()
        elif caption_type == "trim and fill":
            self.caption = TrimAndFillCaption()
        elif caption_type == "basic analysis":
            self.caption = BasicAnalysisCaption()
        elif caption_type == "grouped analysis":
            self.caption = GroupedAnalysisCaption()
        elif caption_type == "nested analysis":
            self.caption = NestedAnalysisCaption()
        elif caption_type == "cumulative analysis":
            self.caption = CumulativeAnalysisCaption()
        elif caption_type == "jackknife analysis":
            self.caption = JackknifeAnalysisCaption()
        elif caption_type == "forest plot":
            self.caption = ForestPlotCaption()
        else:
            self.caption = ""

    def caption_text(self):
        return str(self.caption)

    def add_scatter(self, name: str, x_data, y_data, marker: Union[str, int] = "o", label="", zorder=0, color="#1f77b4",
                    edgecolors="#1f77b4", size=36, linewidths=1.5, linestyle="solid"):
        new_scatter = ScatterData()
        new_scatter.name = name
        new_scatter.x = x_data
        new_scatter.y = y_data
        new_scatter.marker = marker
        new_scatter.label = label
        new_scatter.zorder = zorder
        new_scatter.color = color
        new_scatter.size = size
        new_scatter.edgecolors = edgecolors
        new_scatter.linewidths = linewidths
        new_scatter.linestyle = linestyle
        self.data.append(new_scatter)
        return new_scatter

    def add_line(self, name: str, x_min, y_min, x_max, y_max, linestyle="solid", color="silver", zorder=0,
                 linewidth=1.5):
        new_line = LineData()
        new_line.name = name
        new_line.x_values = [x_min, x_max]
        new_line.y_values = [y_min, y_max]
        new_line.linestyle = linestyle
        new_line.color = color
        new_line.zorder = zorder
        new_line.linewidth = linewidth
        self.data.append(new_line)
        return new_line

    def add_histogram(self, name, cnts, bins, linewidth=1, edgecolor="black", color="#1f77b4", linestyle="solid"):
        new_hist = HistogramData()
        new_hist.name = name
        new_hist.counts = cnts
        new_hist.bins = bins
        new_hist.linewidth = linewidth
        new_hist.linestyle = linestyle
        new_hist.edgecolor = edgecolor
        new_hist.color = color
        self.data.append(new_hist)
        return new_hist

    def add_arc(self, name, xc, yc, height, width, start_angle, end_angle, zorder=0, edgecolor="silver",
                linestyle="solid", linewidth=1.5):
        new_arc = ArcData()
        new_arc.name = name
        new_arc.x_center = xc
        new_arc.y_center = yc
        new_arc.width = width
        new_arc.height = height
        new_arc.start_angle = start_angle
        new_arc.end_angle = end_angle
        new_arc.zorder = zorder
        new_arc.color = edgecolor
        new_arc.linestyle = linestyle
        new_arc.linewidth = linewidth
        self.data.append(new_arc)
        return new_arc

    def add_multi_line(self, name, x_values, y_values, linestyle="solid", color="silver", zorder=0, linewidth=1.5):
        new_ml = LineData()
        new_ml.name = name
        new_ml.x_values = x_values
        new_ml.y_values = y_values
        new_ml.linestyle = linestyle
        new_ml.color = color
        new_ml.zorder = zorder
        new_ml.linewidth = linewidth
        self.data.append(new_ml)
        return new_ml

    def add_ci(self, name, min_x, max_x, y, zorder=0, color="#1f77b4", linestyle="solid", linewidth=1.5):
        new_ci = ForestCIData()
        new_ci.name = name
        new_ci.min_x = min_x
        new_ci.max_x = max_x
        new_ci.y = y
        new_ci.zorder = zorder
        new_ci.color = color
        new_ci.linestyle = linestyle
        new_ci.linewidth = linewidth
        self.data.append(new_ci)
        return new_ci

    def add_labels(self, name, labels, y_data):
        new_labels = LabelData()
        new_labels.name = name
        new_labels.labels = labels
        new_labels.y_pos = y_data
        self.data.append(new_labels)
        return new_labels

    def add_annotations(self, name, annotations, x_data, y_data):
        new_annotation = AnnotationData()
        new_annotation.name = name
        new_annotation.x = x_data
        new_annotation.y = y_data
        new_annotation.annotations = annotations
        self.data.append(new_annotation)
        return new_annotation

    def export_to_list(self):
        outlist = ["X-axis label\t{}\n".format(self.x_label),
                   "Y-axis label\t{}\n\n\n".format(self.y_label)]
        for dat in self.data:
            outlist.extend(dat.export_to_list())
            outlist.append("\n\n")
        return outlist


def base_figure():
    """
    create the baseline figure used for all plots
    """
    figure_canvas = FigureCanvasQTAgg(Figure(figsize=(8, 6)))
    faxes = figure_canvas.figure.subplots()
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    return figure_canvas, faxes


def create_figure(chart_data):
    """
    create a figure given pre-determined chart data

    this function allows complete separation of the generation of the plot values and the creation of the figure,
    which subsequently can allow user modification of plot styles and redrawing of the figure w/o needing to
    recalculate anything
    """
    figure_canvas, faxes = base_figure()
    faxes.set_ylabel(chart_data.y_label)
    faxes.set_xlabel(chart_data.x_label)
    for data in chart_data.data:
        if data.visible:
            if isinstance(data, ScatterData):
                faxes.scatter(data.x, data.y, marker=data.marker, label=data.label, zorder=data.zorder,
                              color=data.color, edgecolors=data.edgecolors, s=data.size, linewidths=data.linewidths,
                              linestyle=data.linestyle)
            elif isinstance(data, LineData):
                faxes.plot(data.x_values, data.y_values, linestyle=data.linestyle, color=data.color, zorder=data.zorder,
                           linewidth=data.linewidth)
            elif isinstance(data, ForestCIData):
                faxes.hlines(data.y, data.min_x, data.max_x, zorder=data.zorder, colors=data.color,
                             linestyles=data.linestyle, linewidth=data.linewidth)
            elif isinstance(data, LabelData):
                faxes.set_yticks([y for y in data.y_pos])
                faxes.set_yticklabels(data.labels)
                faxes.get_yaxis().set_tick_params(length=0)
            elif isinstance(data, ArcData):
                arc = patches.Arc((data.x_center, data.y_center), width=data.width, height=data.height,
                                  theta1=data.start_angle, theta2=data.end_angle, edgecolor=data.color,
                                  linestyle=data.linestyle, zorder=data.zorder, linewidth=data.linewidth)
                faxes.add_patch(arc)
            elif isinstance(data, AnnotationData):
                for i in range(len(data.annotations)):
                    faxes.annotate(data.annotations[i], (data.x[i], data.y[i]))
            elif isinstance(data, HistogramData):
                faxes.hist(data.bins[:-1], data.bins, weights=data.counts, edgecolor=data.edgecolor, color=data.color,
                           linewidth=data.linewidth, linestyle=data.linestyle)

    if chart_data.suppress_y:
        faxes.spines["left"].set_visible(False)
    if chart_data.rescale_x is not None:
        faxes.set_xlim(chart_data.rescale_x[0], chart_data.rescale_x[1])

    return figure_canvas


def chart_forest_plot(analysis_type: str, effect_name, forest_data, alpha: float = 0.05,
                      bootstrap_n: Optional[int] = None,
                      extra_name: Optional[str] = None) -> Tuple[FigureCanvasQTAgg, ChartData]:
    chart_data = ChartData(analysis_type)
    chart_data.caption.e_label = effect_name
    chart_data.caption.alpha = alpha
    chart_data.caption.bootstrap_n = bootstrap_n
    if analysis_type == "grouped analysis":
        chart_data.caption.group_label = extra_name
    elif analysis_type == "cumulative analysis":
        chart_data.caption.order_label = extra_name

    chart_data.x_label = effect_name
    chart_data.suppress_y = True

    if bootstrap_n is None:
        bootstrap = False
    else:
        bootstrap = True

    n_effects = len(forest_data)

    y_data = [-d.order for d in forest_data]
    ci_y_data = [y for y in y_data for _ in range(2)]
    labels = [d.name for d in forest_data]

    mean_data = [d.mean for d in forest_data]
    is_data = False
    for d in forest_data:
        if d.median is not None:
            is_data = True
    if is_data:
        median_data = [d.median for d in forest_data]
    else:
        median_data = None

    cis = []
    bs_cis = []
    bias_cis = []
    for d in forest_data:
        cis.extend([d.lower_ci, d.upper_ci])
    min_cis = [d.lower_ci for d in forest_data]
    max_cis = [d.upper_ci for d in forest_data]
    if bootstrap:
        bs_cis = []
        bias_cis = []
        for i, d in enumerate(forest_data):
            bs_cis.extend([d.lower_bs_ci, d.upper_bs_ci])
            bias_cis.extend([d.lower_bias_ci, d.upper_bias_ci])

    chart_data.add_line(get_text("Line of No Effect"), 0, 0, 0, -(n_effects+1), color="silver", linestyle="dotted",
                        zorder=1)
    chart_data.add_ci(get_text("Confidence Intervals"), min_cis, max_cis, y_data, zorder=3)
    chart_data.add_scatter(get_text("Means"), mean_data, y_data, marker="o", zorder=5,
                           label="mean and {:0.0%} CI (t-dist)".format(1-alpha))
    if median_data is not None:
        chart_data.add_scatter(get_text("Medians"), median_data, y_data, marker="x", label="median", zorder=5,
                               color="#ff7f0e")
    chart_data.add_labels(get_text("Vertical Axis Tick Labels"), labels, y_data)

    if bootstrap:
        chart_data.add_scatter(get_text("Bootstrap Confidence Limits"), bs_cis, ci_y_data, marker=6, zorder=4,
                               color="#2ca02c", label="{:0.0%} CI (bootstrap)".format(1-alpha))

        chart_data.add_scatter(get_text("Bias-corrected Bootstrap Confidence Limits"), bias_cis, ci_y_data, marker=7,
                               zorder=4, color="#d62728", label="{:0.0%} CI (bias-corrected bootstrap)".format(1-alpha))

    figure_canvas = create_figure(chart_data)
    return figure_canvas, chart_data


def add_regression_to_chart(x_name: str, y_name: str, x_data, y_data, slope: float, intercept: float,
                            x_min: float, x_max: float, chart_data) -> None:
    y_at_min = slope*x_min + intercept
    y_at_max = slope*x_max + intercept

    chart_data.x_label = x_name
    chart_data.y_label = y_name
    chart_data.caption.regression_scatter = chart_data.add_scatter(get_text("Point Data"), x_data, y_data, zorder=10)
    chart_data.caption.regression = chart_data.add_line(get_text("Regression Line"), x_min, y_at_min, x_max, y_at_max,
                                                        zorder=8, color="silver")


def chart_regression(x_name, y_name, x_data, y_data, slope, intercept, model, ref_list,
                     citations) -> Tuple[FigureCanvasQTAgg, ChartData]:
    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    chart_data = ChartData("regression")
    chart_data.caption.e_label = y_name
    chart_data.caption.i_label = x_name
    chart_data.caption.model = model
    chart_data.caption.ref_list = ref_list
    chart_data.caption.citations = citations

    add_regression_to_chart(x_name, y_name, x_data, y_data, slope, intercept, x_min, x_max, chart_data)

    figure_canvas = create_figure(chart_data)
    return figure_canvas, chart_data


def add_quantile_axes_to_chart(x_data, y_data, slope: float, intercept: float, chart_data, alpha: float = 0.05) -> None:
    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    y_min = numpy.min(y_data)
    y_max = numpy.max(y_data)
    n = len(x_data)
    x_mean = numpy.sum(x_data)/n
    y_mean = numpy.sum(y_data)/n

    y_pred = [slope*x + intercept for x in x_data]
    mse = numpy.sum(numpy.square(y_data - y_pred))/(n - 2)  # mean square error
    ss_x = numpy.sum(numpy.square(x_data - x_mean))  # sum of squares of x

    t_score = -scipy.stats.t.ppf(alpha/2, n-2)
    nsteps = 100
    p = [(i + 0.5)/nsteps for i in range(nsteps)]
    x_pos = [scipy.stats.norm.ppf(i) for i in p]
    y_pos = [x*slope + intercept for x in x_pos]
    y_lower = [y_pos[i] - t_score*math.sqrt(mse*(1 + 1/n + ((x_pos[i] - x_mean)**2)/ss_x)) for i in range(nsteps)]
    y_upper = [y_pos[i] + t_score*math.sqrt(mse*(1 + 1/n + ((x_pos[i] - x_mean)**2)/ss_x)) for i in range(nsteps)]

    chart_data.caption.lower_limit = chart_data.add_multi_line(get_text("Lower Prediction Limit"), x_pos, y_lower,
                                                               linestyle="dashed", color="silver", zorder=3)
    chart_data.caption.upper_limit = chart_data.add_multi_line(get_text("Upper Prediction Limit"), x_pos, y_upper,
                                                               linestyle="dashed", color="silver", zorder=3)

    # draw center lines
    chart_data.caption.horizontal_mean = chart_data.add_line(get_text("Horizontal Axis Mean Line"), 0,
                                                             min(y_min, min(y_lower)), 0, max(y_max, max(y_upper)),
                                                             linestyle="dotted", color="silver")
    chart_data.caption.vertical_mean = chart_data.add_line(get_text("Vertical Axis Mean Line"), x_min, y_mean, x_max,
                                                           y_mean, linestyle="dotted", color="silver")


def chart_normal_quantile(x_name, y_name, x_data, y_data, slope, intercept,
                          alpha: float = 0.05) -> Tuple[FigureCanvasQTAgg, ChartData]:
    chart_data = ChartData("normal quantile")
    add_quantile_axes_to_chart(x_data, y_data, slope, intercept, chart_data, alpha)
    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    add_regression_to_chart(x_name, y_name, x_data, y_data, slope, intercept, x_min, x_max, chart_data)

    figure_canvas = create_figure(chart_data)
    return figure_canvas, chart_data


def add_radial_curve_to_chart(effect_label: str, r: float, min_e: float, max_e: float, chart_data,
                              is_log: bool = False) -> None:
    start_a = math.atan(min_e)
    end_a = math.atan(max_e)
    chart_data.add_arc(get_text("Radial Arc"), 0, 0, 2*r, 2*r, math.degrees(start_a), math.degrees(end_a), zorder=2,
                       edgecolor="silver", linestyle="dotted")

    if is_log:
        start_label = math.ceil(math.exp(min_e))
        end_label = math.floor(math.exp(max_e))
        curve_label = exponential_label(effect_label)
    else:
        start_label = math.ceil(min_e)
        end_label = math.floor(max_e)
        curve_label = effect_label

    annotation_list = []
    annotation_x = []
    annotation_y = []

    xadj = 0.25
    for s in range(start_label, end_label+1):
        if not is_log:
            slope = s
            label = str(s)
            if s < 0:
                yadj = -0.25
            elif s > 0:
                yadj = 0.25
            else:
                yadj = 0
        else:
            if -1 > s > -10:
                slope = math.log(1/abs(s))
                label = "1/{}".format(abs(s))
                yadj = -0.25
            elif 1 < s < 10:
                slope = math.log(s)
                label = str(s)
                yadj = 0.25
            elif s == 1:
                slope = 0
                label = "1"
                yadj = 0
            else:
                continue
        annotation_list.append(label)
        annotation_x.append(r*math.cos(math.atan(slope)) + xadj)
        annotation_y.append(r*math.sin(math.atan(slope)) + yadj)
    if is_log:
        if min_e < 2/3 < max_e:
            annotation_list.append("2/3")
            annotation_x.append(r*math.cos(math.atan(math.log(2/3))) + xadj)
            annotation_y.append(r*math.sin(math.atan(math.log(2/3))) - 0.25)
        if min_e < 3/2 < max_e:
            annotation_list.append("3/2")
            annotation_x.append(r * math.cos(math.atan(math.log(3/2))) + xadj)
            annotation_y.append(r * math.sin(math.atan(math.log(3/2))) + 0.25)
    else:
        if min_e < 1/2 < max_e:
            annotation_list.append("1/2")
            annotation_x.append(r * math.cos(math.atan(1/2)) + xadj)
            annotation_y.append(r * math.sin(math.atan(1/2)) - 0.25)
        if min_e < -1/2 < max_e:
            annotation_list.append("-1/2")
            annotation_x.append(r * math.cos(math.atan(-1/2)) + xadj)
            annotation_y.append(r * math.sin(math.atan(-1/2)) + 0.25)
    annotation_list.append(curve_label)
    annotation_x.append(r)
    annotation_y.append(2)
    chart_data.add_annotations(get_text("Radial Arc Labels"), annotation_list, annotation_x, annotation_y)

    chart_data.add_line(get_text("Vertical Axis Zero Line"), 0, 0, r+1, 0, color="silver", linestyle="dotted")


def chart_radial(e_name, x_data, y_data, slope, min_e, max_e, is_log: bool = False) -> Tuple[FigureCanvasQTAgg,
                                                                                             ChartData]:
    chart_data = ChartData("radial")
    chart_data.caption.e_label = e_name
    max_d = numpy.max(numpy.sqrt(numpy.square(x_data) + numpy.square(y_data)))+1
    x_min = 0
    x_max = (max_d + 1)*math.cos(math.atan(slope))
    add_regression_to_chart(get_text("Precision"), get_text("Standardized") + " " + e_name, x_data, y_data,
                            slope, 0, x_min, x_max, chart_data)
    add_radial_curve_to_chart(e_name, max_d, min_e, max_e, chart_data, is_log)
    chart_data.rescale_x = (0, max_d+2)

    figure_canvas = create_figure(chart_data)
    return figure_canvas, chart_data


def chart_histogram(e_data, w_data, n_bins, e_label,
                    weighted: int = WEIGHT_NONE) -> Tuple[FigureCanvasQTAgg, ChartData]:
    if weighted == WEIGHT_NONE:
        cnts, bins = numpy.histogram(e_data, n_bins)
        y_label = get_text("Count")
    else:
        cnts, bins = numpy.histogram(e_data, n_bins, weights=w_data)
        y_label = get_text("Weighted Count")
    # if weighted:
    #     cnts, bins = numpy.histogram(e_data, n_bins, weights=w_data)
    #     y_label = get_text("Weighted Count")
    # else:
    #     cnts, bins = numpy.histogram(e_data, n_bins)
    #     y_label = get_text("Count")

    chart_data = ChartData("histogram")
    chart_data.caption.e_label = e_label
    chart_data.caption.weight_type = weighted

    chart_data.x_label = e_label
    chart_data.y_label = y_label
    chart_data.add_histogram("Bin Counts", cnts, bins, edgecolor="black", linewidth=1)

    figure_canvas = create_figure(chart_data)
    return figure_canvas, chart_data


def draw_tree(faxes, tree, minx, maxx, miny, maxy, scale, draw_labels: bool = False, draw_branch_lengths: bool = False):
    """
    minx, maxx, miny, and maxy represent the drawing bounds for the target node, with minx representing the
    horizontal position of the ancestor of the node, maxx representing the right hand edge of the entire tree,
    miny and maxy representing the vertical positioning of the node and all of its descendants.

    scale is a precalculated value that converts branch lengths to the coordinate system
    """

    """
    the following calculates the horizontal area necessary for the horizontal line connecting the node to it's 
    ancestor
    """
    x = tree.branch_length * scale

    """
    if the node has descendants, first draw all of the descendants in the box which goes from the right edge of 
    the horizontal line for this node to the right hand edge of the drawing window, and the vertical box defined 
    for the entire node
    """
    if tree.n_descendants() > 0:  # this is an internal node
        top_vert_line = 0
        bottom_vert_line = 0
        nd = tree.n_tips()
        top_y = miny
        for i, d in enumerate(tree.descendants):
            """
            divide the vertical plotting area for each descendant proportional to the number of tips contained 
            within that descendant
            """
            ndd = d.n_tips()
            bottom_y = top_y + (ndd / nd) * (maxy - miny)
            # draw the descendant in its own smaller bounded box
            y = draw_tree(faxes, d, minx + x, maxx, top_y, bottom_y, scale, draw_labels, draw_branch_lengths)

            """
            the vertical position of the first and last descendants represent the positions to draw the vertical 
            line connecting all of the descendants
            """
            if i == 0:
                bottom_vert_line = y
            elif i == tree.n_descendants() - 1:
                top_vert_line = y
            top_y = bottom_y
        """
        draw the vertical line connecting the descendants at the horizontal position of the node
        """
        faxes.plot([minx+x, minx+x], [bottom_vert_line, top_vert_line], color="black")

        """
        the vertical position of the node should be the midpoint of the
        vertical line connecting the descendants
        """
        y = ((top_vert_line - bottom_vert_line) / 2) + bottom_vert_line
    else:  # this is a tip node
        """
        if the node has no descendants, figure out the vertical position as the
        midpoint of the vertical bounds
        """
        y = (maxy - miny)/2 + miny
        if draw_labels:  # if desired, label the node
            faxes.annotate(tree.name, (minx + x + 5, y - 5))

    # draw the horizontal line connecting the node to its ancestor
    faxes.plot([minx, minx + x], [y, y], color="black")

    # add branch lengths
    if draw_branch_lengths:
        pass
        # not enabled

    return y


def chart_phylogeny(root) -> FigureCanvasQTAgg:
    # set up drawing space
    figure_canvas, faxes = base_figure()
    faxes.spines["bottom"].set_visible(False)
    faxes.spines["left"].set_visible(False)
    faxes.get_xaxis().set_visible(False)
    faxes.get_yaxis().set_visible(False)

    xwidth = 1000
    yheight = 1000
    maxbranch = root.max_node_tip_length()
    scale = (xwidth - 100) / maxbranch
    draw_tree(faxes, root, 0, xwidth, 0, yheight, scale, True, False)
    faxes.set_xlim(0, xwidth+100)
    figure_canvas.figure.tight_layout()

    return figure_canvas


def chart_scatter(x_data, y_data, x_label: str = "x", y_label: str = "y") -> Tuple[FigureCanvasQTAgg, ChartData]:
    chart_data = ChartData("scatter plot")
    chart_data.caption.x_label = x_label
    chart_data.caption.y_label = y_label
    chart_data.x_label = x_label
    chart_data.y_label = y_label
    chart_data.add_scatter(get_text("Point Data"), x_data, y_data)

    figure_canvas = create_figure(chart_data)
    return figure_canvas, chart_data


def chart_trim_fill_plot(effect_label, data, n, original_mean, new_mean) -> Tuple[FigureCanvasQTAgg, ChartData]:
    chart_data = ChartData("trim and fill")
    chart_data.caption.e_label = effect_label
    chart_data.x_label = effect_label
    chart_data.y_label = "{} (1/SE)".format(get_text("Precision"))

    # plot original points
    x_data = data[:n, 0]
    y_data = numpy.reciprocal(numpy.sqrt(data[:n, 2]))
    chart_data.caption.original_scatter = chart_data.add_scatter(get_text("Original Data"), x_data, y_data,
                                                                 color="black", edgecolors="black")
    y_min = numpy.min(y_data)
    y_max = numpy.max(y_data)

    # plot inferred points
    x_data = data[n:, 0]
    y_data = numpy.reciprocal(numpy.sqrt(data[n:, 2]))
    chart_data.caption.inferred_scatter = chart_data.add_scatter(get_text("Inferred Data"), x_data, y_data,
                                                                 edgecolors="red", color="none")

    # draw original and new mean
    chart_data.caption.original_mean = chart_data.add_line(get_text("Original Mean"), original_mean, y_min,
                                                           original_mean, y_max, color="silver", linestyle="dashed",
                                                           zorder=1)
    chart_data.caption.inferred_mean = chart_data.add_line(get_text("Inferred Mean"), new_mean, y_min, new_mean, y_max,
                                                           color="red", linestyle="dashed", zorder=1)

    figure_canvas = create_figure(chart_data)
    return figure_canvas, chart_data
