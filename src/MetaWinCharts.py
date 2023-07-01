"""
Module for creating figures using the matplotlib backend for Qt
"""

import math
from typing import Optional, Union

from matplotlib import patches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
# the following import is necessary to force pyinstaller to include these backends for vector output when packaging
from matplotlib.backends import backend_svg, backend_ps, backend_pgf, backend_pdf
from matplotlib.colors import XKCD_COLORS, hex2color, CSS4_COLORS
import numpy
import scipy.stats

from MetaWinUtils import exponential_label, get_citation, create_reference_list
from MetaWinLanguage import get_text
import MetaWinWidgets

color_name_space = "xkcd"


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

UNFILLED_MARKERS = {"point", "plus", "X", "vertical line", "horizontal line", "tick left", "tick right", "tick up",
                    "tick down", "upward caret", "downward caret", "left caret", "right caret",
                    "centered upward caret", "centered downward caret", "centered left caret", "centered right caret"}


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

    def style_text(self) -> str:
        marker_name = list(MARKER_STYLES.keys())[list(MARKER_STYLES.values()).index(self.marker)]
        if marker_name.endswith("s"):
            s = "ses"
        else:
            s = "s"
        if marker_name in UNFILLED_MARKERS:
            if self.color == "none":
                return get_text("nothing (marker is invisible)")
            else:
                return find_color_name(self.color) + " " + marker_name + s
        else:
            if self.color == self.edgecolors:
                return find_color_name(self.color) + " " + marker_name + s
            else:
                if self.color == "none":
                    return get_text("marker_style_open_text").format(marker_name, s, find_color_name(self.edgecolors))
                else:
                    return get_text("marker_style_text").format(find_color_name(self.color), marker_name, s,
                                                                find_color_name(self.edgecolors))


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
        self.linked_style = None
        self.is_linked = False

    def link_style(self, other_line):
        self.linked_style = other_line
        other_line.is_linked = True

    def export_to_list(self) -> list:
        outlist = ["Line Data\n",
                   "Name\t{}\n".format(self.name),
                   "x\ty\n"]
        for i in range(len(self.x_values)):
            outlist.append("{}\t{}\n".format(self.x_values[i], self.y_values[i]))
        return outlist

    def create_edit_panel(self):
        if self.is_linked:
            return self.edit_panel
        else:
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
        if self.linked_style is not None:
            self.linked_style.linestyle = self.linestyle
            self.linked_style.linewidth = self.linewidth
            self.linked_style.color = self.color
            self.linked_style.visible = self.visible

    def style_text(self) -> str:
        return self.linestyle + " " + find_color_name(self.color) + " line"


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


class FillDataX(BaseChartData):
    """
    an object to contain area fills that run between two values on the x-axis
    """
    def __init__(self):
        super().__init__()
        self.x1_values = None
        self.x2_values = None
        self.y_values = None
        self.edit_panel = None
        # style
        self.color = "silver"
        self.zorder = 0
        self.alpha = 0.5
        self.color_button = None
        self.linked_style = None
        self.is_linked = False

    def link_style(self, other_fill):
        self.linked_style = other_fill
        other_fill.is_linked = True

    def export_to_list(self) -> list:
        # outlist = ["Line Data\n",
        #            "Name\t{}\n".format(self.name),
        #            "x\ty\n"]
        # for i in range(len(self.x_values)):
        #     outlist.append("{}\t{}\n".format(self.x_values[i], self.y_values[i]))
        # return outlist
        return []

    def create_edit_panel(self):
        if self.is_linked:
            return self.edit_panel
        else:
            self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
            self.color_button, color_label, _ = MetaWinWidgets.add_chart_color_button(get_text("Color"), self.color)

            edit_layout.addWidget(color_label, 0, 0)
            edit_layout.addWidget(self.color_button, 1, 0)
            for i in range(edit_layout.columnCount()):
                edit_layout.setColumnStretch(i, 1)
            return self.edit_panel

    def update_style(self):
        self.color = self.color_button.color
        if self.linked_style is not None:
            self.linked_style.color = self.color

    def style_text(self) -> str:
        return find_color_name(self.color)


class ColorGrid(BaseChartData):
    """
    an object to contain area fills that run between two values on the x-axis
    """
    def __init__(self):
        super().__init__()
        self.x_values = None
        self.y_values = None
        self.z_values = None
        self.edit_panel = None
        # style
        self.colormap = "RdYlGn"
        # self.color = "silver"
        # self.zorder = 0
        # self.alpha = 0.5
        # self.color_button = None
        # self.linked_style = None
        # self.is_linked = False

    # def link_style(self, other_fill):
    #     self.linked_style = other_fill
    #     other_fill.is_linked = True

    def export_to_list(self) -> list:
        # outlist = ["Line Data\n",
        #            "Name\t{}\n".format(self.name),
        #            "x\ty\n"]
        # for i in range(len(self.x_values)):
        #     outlist.append("{}\t{}\n".format(self.x_values[i], self.y_values[i]))
        # return outlist
        return []

    def create_edit_panel(self):
        # if self.is_linked:
        #     return self.edit_panel
        # else:
        #     self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        #     self.color_button, color_label, _ = MetaWinWidgets.add_chart_color_button(get_text("Color"), self.color)
        #
        #     edit_layout.addWidget(color_label, 0, 0)
        #     edit_layout.addWidget(self.color_button, 1, 0)
        #     for i in range(edit_layout.columnCount()):
        #         edit_layout.setColumnStretch(i, 1)
        #     return self.edit_panel
        return self.edit_panel

    def update_style(self):
        # self.color = self.color_button.color
        # if self.linked_style is not None:
        #     self.linked_style.color = self.color
        pass

    def style_text(self) -> str:
        # return find_color_name(self.color)
        return ""


# ---------- Chart Caption Classes ---------- #
class NormalQuantileCaption:
    def __init__(self):
        # self.upper_limit = None
        self.prediction_limit = None
        # self.horizontal_mean = None
        # self.vertical_mean = None
        self.means = None
        self.regression = None
        self.regression_scatter = None

    def __str__(self):
        regression_text = self.regression.style_text()
        # upper_text = self.upper_limit.style_text()
        # lower_text = self.lower_limit.style_text()
        style_text = get_text("normal_quantile_style").format(regression_text, self.prediction_limit.style_text())
        # if upper_text == lower_text:
        #     style_text = get_text("normal_quantile_style1").format(regression_text, upper_text)
        # else:
        #     style_text = get_text("normal_quantile_style2").format(regression_text, upper_text, lower_text)
        return get_text("normal_quantile_caption").format(get_citation("Wang_and_Bushman_1998")) + style_text + \
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


class MetaRegressionCaption:
    def __init__(self):
        self.e_label = ""
        self.i_label = ""
        self.model = ""
        self.ref_list = ""
        self.citations = []

    def __str__(self):
        return get_text("metaregression_caption").format(self.e_label, self.i_label, self.model, self.ref_list) + \
                create_reference_list(self.citations, True)


class StndRegressionCaption:
    def __init__(self):
        self.x_label = ""
        self.y_label = ""
        self.model = ""

    def __str__(self):
        return get_text("stndregression_caption").format(self.y_label, self.x_label, self.model)


class TrimAndFillCaption:
    def __init__(self):
        self.e_label = ""
        self.original_scatter = None
        self.inferred_scatter = None
        self.original_mean = None
        self.inferred_mean = None

    def __str__(self):
        original_mean_text = self.original_mean.style_text()
        inferred_mean_text = self.inferred_mean.style_text()
        original_marker_text = self.original_scatter.style_text()
        inferred_marker_text = self.inferred_scatter.style_text()
        new_cites = ["Duval_Tweedie_2000a", "Duval_Tweedie_2000b"]
        return get_text("trim_fill_caption").format(self.e_label, "Duval and Tweedie 2000a, b", original_marker_text,
                                                    inferred_marker_text, original_mean_text,
                                                    inferred_mean_text) + create_reference_list(new_cites, True)


class ForestPlotBaseCaption:
    def __init__(self):
        self.e_label = ""
        self.alpha = 0.05
        self.bootstrap_n = None
        self.normal_ci = True
        self.no_effect = None
        self.means = None
        self.medians = None
        self.boot = None
        self.bias = None

    def base_forest_plot_caption(self) -> str:
        """
        Basic forest plot description
        """
        return get_text("forest_plot_common_caption1").format(self.e_label, self.no_effect.style_text())

    def mid_forest_plot_caption(self) -> str:
        """
        Middle part of forest plot captions, when no study specific intervals are included
        """
        if self.normal_ci:
            dist_text = get_text("normal_ci_dist")
        else:
            dist_text = get_text("t_ci_dist")
        return get_text("mid_forest_plot_caption").format(self.means.style_text(), 1-self.alpha, dist_text)

    def extra_forest_plot_caption(self, inc_median: bool = True) -> str:
        """
        Final part of forest plot captions, to indicate median and bootstrap style markers
        """
        text = ""
        if inc_median:
            text += get_text("forest_plot_median_caption").format(self.medians.style_text())
        if self.bootstrap_n is not None:
            citation = "Adams_et_1997"
            text += get_text("bootstrap_caption").format(self.bootstrap_n, get_citation(citation),
                                                         self.boot.style_text(), self.bias.style_text()) + \
                    create_reference_list([citation], True)
        return text


class ForestPlotCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("Forest plot of individual effect sizes for each study.") + \
               self.base_forest_plot_caption() + \
               get_text("study_forest_plot_extra").format(self.means.style_text(), 1-self.alpha)


class BasicAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        if self.normal_ci:
            dist_text = get_text("normal_ci_dist")
        else:
            dist_text = get_text("mixed_ci_dist")
        return get_text("Forest plot of individual effect sizes for each study, as well as the overall mean.") + \
               self.base_forest_plot_caption() + \
               get_text("basic_analysis_forest_plot_extra").format(self.means.style_text(), 1-self.alpha, dist_text) + \
               self.extra_forest_plot_caption()


class GroupedAnalysisCaption(ForestPlotBaseCaption):
    def __init__(self):
        super().__init__()
        self.group_label = ""

    def __str__(self):
        return get_text("group_forest_plot").format(self.group_label) + \
               self.base_forest_plot_caption() + self.mid_forest_plot_caption() + self.extra_forest_plot_caption()


class NestedAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("nest_caption") + self.base_forest_plot_caption() + self.mid_forest_plot_caption() + \
               self.extra_forest_plot_caption()


class CumulativeAnalysisCaption(ForestPlotBaseCaption):
    def __init__(self):
        super().__init__()
        self.order_label = ""

    def __str__(self):
        return get_text("cumulative_forest_plot").format(self.order_label) + \
               self.base_forest_plot_caption() + self.mid_forest_plot_caption() + self.extra_forest_plot_caption()


class JackknifeAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("jackknife_forest_plot") + self.base_forest_plot_caption() + self.mid_forest_plot_caption() + \
               self.extra_forest_plot_caption()


class FunnelPlotCaption:
    def __init__(self):
        self.x_label = ""
        self.y_label = ""
        self.mean_effect = None
        self.pseudo_ci = None
        self.zone99 = None
        self.zone95 = None
        self.zone90 = None

    def __str__(self):
        mean_text = self.mean_effect.style_text()
        citations = ["Light_Pillemer_1984"]
        if self.pseudo_ci is None:
            pseudo_text = ""
        else:
            cite_text = get_citation("Sterne_Egger_2001")
            pseudo_text = get_text("funnel_pseudo_ci_style").format(self.pseudo_ci.style_text(), cite_text)
        if self.zone99 is None:
            contour_text = ""
        else:
            cite_text = get_citation("Peters_et_2008")
            citations.append("Peters_et_2008")
            contour_text = get_text("funnel_contour_style").format(self.zone99.style_text(), self.zone95.style_text(),
                                                                   self.zone90.style_text(), cite_text)

        return get_text("funnel_plot_caption").format(self.x_label, self.y_label, mean_text) + pseudo_text + \
            contour_text + create_reference_list(citations, True)


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
        self.invert_y = False
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
            self.caption = MetaRegressionCaption()
        elif caption_type == "standard regression":
            self.caption = StndRegressionCaption()
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
        elif caption_type == "funnel plot":
            self.caption = FunnelPlotCaption()
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

    def add_fill_area_x(self, name, x1, x2, y, zorder=0, color="red", alpha=0.5):
        new_fill = FillDataX()
        new_fill.name = name
        new_fill.x1_values = x1
        new_fill.x2_values = x2
        new_fill.y_values = y
        new_fill.color = color
        new_fill.zorder = zorder
        new_fill.alpha = alpha
        self.data.append(new_fill)
        return new_fill

    def add_color_grid(self, name, x, y, z, colormap: str = "inferno"):
        new_grid = ColorGrid()
        new_grid.name = name
        new_grid.x_values = x
        new_grid.y_values = y
        new_grid.z_values = z
        new_grid.colormap = colormap
        self.data.append(new_grid)
        return new_grid

    def export_to_list(self):
        outlist = ["X-axis label\t{}\n".format(self.x_label),
                   "Y-axis label\t{}\n\n\n".format(self.y_label)]
        for dat in self.data:
            outlist.extend(dat.export_to_list())
            outlist.append("\n\n")
        return outlist


def base_figure(figure_canvas):
    """
    create the baseline figure used for all plots
    """
    # figure_canvas = FIGURE_CANVAS
    figure_canvas.figure.clf()  # clean any existing figures
    faxes = figure_canvas.figure.subplots()
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    # return figure_canvas, faxes
    return faxes


def create_figure(chart_data, figure_canvas):
    """
    create a figure given pre-determined chart data

    this function allows complete separation of the generation of the plot values and the creation of the figure,
    which subsequently can allow user modification of plot styles and redrawing of the figure w/o needing to
    recalculate anything
    """
    faxes = base_figure(figure_canvas)
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
            elif isinstance(data, FillDataX):
                faxes.fill_betweenx(data.y_values, data.x1_values, data.x2_values, color=data.color,
                                    edgecolor="none", zorder=data.zorder,
                                    alpha=data.alpha)
            elif isinstance(data, ColorGrid):
                # ax2 = faxes.twinx()
                # max_z = numpy.max(data.z_values)
                # min_z = numpy.min(data.z_values)
                # ax2.set_ylim(min_z, max_z)
                # if chart_data.invert_y:
                #     ax2.invert_yaxis()
                # faxes.set_zorder(ax2.get_zorder()+1)
                # faxes.set_frame_on(False)
                cm = faxes.pcolormesh(data.x_values, data.y_values, data.z_values, shading="gouraud",
                                 cmap=data.colormap, zorder=0, vmin=0, vmax=100)
                figure_canvas.figure.colorbar(cm, ax=faxes, label="Power")

    if chart_data.suppress_y:
        faxes.spines["left"].set_visible(False)
    if chart_data.rescale_x is not None:
        faxes.set_xlim(chart_data.rescale_x[0], chart_data.rescale_x[1])
    if chart_data.invert_y:
        faxes.invert_yaxis()


def chart_forest_plot(analysis_type: str, effect_name, forest_data, alpha: float = 0.05,
                      bootstrap_n: Optional[int] = None, extra_name: Optional[str] = None,
                      normal_ci: bool = True) -> ChartData:
    chart_data = ChartData(analysis_type)
    chart_data.caption.e_label = effect_name
    chart_data.caption.alpha = alpha
    chart_data.caption.bootstrap_n = bootstrap_n
    chart_data.caption.normal_ci = normal_ci
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

    chart_data.caption.no_effect = chart_data.add_line(get_text("Line of No Effect"), 0, 0, 0, -(n_effects+1),
                                                       color="silver", linestyle="dotted", zorder=1)
    chart_data.add_ci(get_text("Confidence Intervals"), min_cis, max_cis, y_data, zorder=3)
    chart_data.caption.means = chart_data.add_scatter(get_text("Means"), mean_data, y_data, marker="o", zorder=5,
                                                      label="mean and {:0.0%} CI (t-dist)".format(1-alpha))
    if median_data is not None:
        chart_data.caption.medians = chart_data.add_scatter(get_text("Medians"), median_data, y_data, marker="x",
                                                            label="median", zorder=5, color="#ff7f0e")
    chart_data.add_labels(get_text("Vertical Axis Tick Labels"), labels, y_data)

    if bootstrap:
        chart_data.caption.boot = chart_data.add_scatter(get_text("Bootstrap Confidence Limits"), bs_cis, ci_y_data,
                                                         marker=6, zorder=4, color="#2ca02c",
                                                         label="{:0.0%} CI (bootstrap)".format(1-alpha))

        chart_data.caption.bias = chart_data.add_scatter(get_text("Bias-corrected Bootstrap Confidence Limits"),
                                                         bias_cis, ci_y_data, marker=7, zorder=4, color="#d62728",
                                                         label="{:0.0%} CI (bias-corrected bootstrap)".format(1-alpha))

    return chart_data


def add_regression_to_chart(x_name: str, y_name: str, x_data, y_data, slope: float, intercept: float,
                            x_min: float, x_max: float, chart_data) -> None:
    y_at_min = slope*x_min + intercept
    y_at_max = slope*x_max + intercept

    chart_data.x_label = x_name
    chart_data.y_label = y_name
    chart_data.caption.regression_scatter = chart_data.add_scatter(get_text("Point Data"), x_data, y_data, zorder=10)
    chart_data.caption.regression = chart_data.add_line(get_text("Regression Line"), x_min, y_at_min, x_max, y_at_max,
                                                        zorder=8, color="silver")


def chart_meta_regression(x_name, y_name, x_data, y_data, slope, intercept, model, ref_list,
                          citations) -> ChartData:
    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    chart_data = ChartData("regression")
    chart_data.caption.e_label = y_name
    chart_data.caption.i_label = x_name
    chart_data.caption.model = model
    chart_data.caption.ref_list = ref_list
    chart_data.caption.citations = citations

    add_regression_to_chart(x_name, y_name, x_data, y_data, slope, intercept, x_min, x_max, chart_data)

    return chart_data


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

    # chart_data.caption.lower_limit = chart_data.add_multi_line(get_text("Lower Prediction Limit"), x_pos, y_lower,
    #                                                            linestyle="dashed", color="silver", zorder=3)
    # chart_data.caption.upper_limit = chart_data.add_multi_line(get_text("Upper Prediction Limit"), x_pos, y_upper,
    #                                                            linestyle="dashed", color="silver", zorder=3)
    chart_data.caption.prediction_limit = chart_data.add_multi_line(get_text("Prediction Limits"), x_pos, y_lower,
                                                                    linestyle="dashed", color="silver", zorder=3)
    upper_limit = chart_data.add_multi_line("", x_pos, y_upper, linestyle="dashed", color="silver", zorder=3)
    chart_data.caption.prediction_limit.link_style(upper_limit)

    # draw center lines
    # chart_data.caption.horizontal_mean = chart_data.add_line(get_text("Horizontal Axis Mean Line"), 0,
    #                                                          min(y_min, min(y_lower)), 0, max(y_max, max(y_upper)),
    #                                                          linestyle="dotted", color="silver")
    # chart_data.caption.vertical_mean = chart_data.add_line(get_text("Vertical Axis Mean Line"), x_min, y_mean, x_max,
    #                                                        y_mean, linestyle="dotted", color="silver")
    chart_data.caption.means = chart_data.add_line(get_text("Axes Means"), 0, min(y_min, min(y_lower)), 0,
                                                   max(y_max, max(y_upper)), linestyle="dotted", color="silver")
    vertical_mean = chart_data.add_line("", x_min, y_mean, x_max, y_mean, linestyle="dotted", color="silver")
    chart_data.caption.means.link_style(vertical_mean)


def chart_normal_quantile(x_name, y_name, x_data, y_data, slope, intercept,
                          alpha: float = 0.05) -> ChartData:
    chart_data = ChartData("normal quantile")
    add_quantile_axes_to_chart(x_data, y_data, slope, intercept, chart_data, alpha)
    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    add_regression_to_chart(x_name, y_name, x_data, y_data, slope, intercept, x_min, x_max, chart_data)

    return chart_data


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


def chart_radial(e_name, x_data, y_data, slope, min_e, max_e, is_log: bool = False) -> ChartData:
    chart_data = ChartData("radial")
    chart_data.caption.e_label = e_name
    max_d = numpy.max(numpy.sqrt(numpy.square(x_data) + numpy.square(y_data)))+1
    x_min = 0
    x_max = (max_d + 1)*math.cos(math.atan(slope))
    add_regression_to_chart(get_text("Precision"), get_text("Standardized") + " " + e_name, x_data, y_data,
                            slope, 0, x_min, x_max, chart_data)
    add_radial_curve_to_chart(e_name, max_d, min_e, max_e, chart_data, is_log)
    chart_data.rescale_x = (0, max_d+2)

    return chart_data


def chart_histogram(e_data, w_data, n_bins, e_label, weighted: int = WEIGHT_NONE) -> ChartData:
    if weighted == WEIGHT_NONE:
        cnts, bins = numpy.histogram(e_data, n_bins)
        y_label = get_text("Count")
    else:
        cnts, bins = numpy.histogram(e_data, n_bins, weights=w_data)
        y_label = get_text("Weighted Count")

    chart_data = ChartData("histogram")
    chart_data.caption.e_label = e_label
    chart_data.caption.weight_type = weighted

    chart_data.x_label = e_label
    chart_data.y_label = y_label
    chart_data.add_histogram("Bin Counts", cnts, bins, edgecolor="black", linewidth=1)

    return chart_data


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
    figure_canvas = FigureCanvasQTAgg(Figure(figsize=(8, 6)))
    faxes = figure_canvas.figure.subplots()
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
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


def chart_scatter(x_data, y_data, x_label: str = "x", y_label: str = "y") -> ChartData:
    chart_data = ChartData("scatter plot")
    chart_data.caption.x_label = x_label
    chart_data.caption.y_label = y_label
    chart_data.x_label = x_label
    chart_data.y_label = y_label
    chart_data.add_scatter(get_text("Point Data"), x_data, y_data)

    return chart_data


def chart_trim_fill_plot(effect_label, data, n, original_mean, new_mean) -> ChartData:
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

    return chart_data


def chart_funnel_plot(x_data, y_data, mean_e, x_label: str = "x", y_label: str = "sample size",
                      do_pseudo: bool = False, do_contour: bool = False, do_power: False = False) -> ChartData:
    chart_data = ChartData("funnel plot")
    chart_data.caption.x_label = x_label
    chart_data.caption.y_label = y_label
    chart_data.x_label = x_label
    chart_data.y_label = y_label
    chart_data.add_scatter(get_text("Point Data"), x_data, y_data, zorder=10)

    y_min = numpy.min(y_data)
    y_max = numpy.max(y_data)

    if y_label in ("standard error", "variance"):
        y_min = min(y_min, 0.001)
    else:
        y_min = y_min*0.85
    y_max = y_max*1.15

    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    chart_data.caption.mean_effect = chart_data.add_line(get_text("Mean Effect Size"), mean_e, y_min, mean_e, y_max,
                                                         color="silver", linestyle="dotted", zorder=5)
    if y_label in ("standard error", "variance"):
        chart_data.invert_y = True

    if (y_label != "sample size") and (do_pseudo or do_contour or do_power):
        curve_y = numpy.linspace(y_min, y_max, 50)  # 50 points for a nice curve
        # if y_label in ("standard error", "variance"):
        #     curve_y = numpy.linspace(min(y_min, 0.001), y_max*1.15, 50)  # 50 points for a nice curve
        # else:
        #     curve_y = numpy.linspace(y_min*0.85, y_max*1.15, 50)  # 50 points for a nice curve
        if y_label == "standard error":
            sey = curve_y
        elif y_label == "precision":
            sey = 1/curve_y
        elif y_label == "variance":
            sey = numpy.sqrt(curve_y)
        else:
            sey = 1/numpy.sqrt(curve_y)

        if do_pseudo:
            curve_x_min, curve_x_max = scipy.stats.norm.interval(alpha=0.95, loc=mean_e, scale=sey)
            chart_data.caption.pseudo_ci = chart_data.add_multi_line(get_text("Pseudo-Confidence Limits"),
                                                                     curve_x_min, curve_y, linestyle="dashed",
                                                                     color="silver", zorder=3)
            pseudo_upper = chart_data.add_multi_line("", curve_x_max, curve_y, linestyle="dashed", color="silver",
                                                     zorder=3)
            chart_data.caption.pseudo_ci.link_style(pseudo_upper)
            x_min = min(numpy.min(curve_x_min), x_min)
            x_max = max(numpy.max(curve_x_max), x_max)

        if do_contour:
            curve_99_min, curve_99_max = scipy.stats.norm.interval(alpha=0.99, loc=0, scale=sey)
            curve_95_min, curve_95_max = scipy.stats.norm.interval(alpha=0.95, loc=0, scale=sey)
            curve_90_min, curve_90_max = scipy.stats.norm.interval(alpha=0.90, loc=0, scale=sey)
            x_min = min(numpy.min(curve_99_min), x_min)
            x_max = max(numpy.max(curve_99_max), x_max)
            chart_data.caption.zone99 = chart_data.add_fill_area_x("P <0.01% zone", x_min, curve_99_min, curve_y,
                                                                   color="#eeeeee", zorder=1)
            up_fill = chart_data.add_fill_area_x("", x_max, curve_99_max, curve_y, color="#eeeeee", zorder=1)
            chart_data.caption.zone99.link_style(up_fill)

            chart_data.caption.zone95 = chart_data.add_fill_area_x("P 0.01-0.05% zone", curve_99_min, curve_95_min,
                                                                   curve_y, color="#cccccc", zorder=1)
            up_fill = chart_data.add_fill_area_x("", curve_99_max, curve_95_max, curve_y, color="#cccccc", zorder=1)
            chart_data.caption.zone95.link_style(up_fill)

            chart_data.caption.zone90 = chart_data.add_fill_area_x("p 0.05-0.1% zone", curve_95_min, curve_90_min,
                                                                   curve_y, color="#a3a3a3", zorder=1)
            up_fill = chart_data.add_fill_area_x("", curve_95_max, curve_90_max, curve_y, color="#a3a3a3", zorder=1)
            chart_data.caption.zone90.link_style(up_fill)

        if do_power:
            z = scipy.stats.norm.ppf(0.975)
            power = 100*(1 - scipy.stats.norm.cdf(z - mean_e/sey) + scipy.stats.norm.cdf(-z - mean_e/sey))
            # x = numpy.linspace(x_min, x_max, 50)
            x = [x_min, x_max]
            xc, yc = numpy.meshgrid(x, curve_y)
            zc = numpy.array([power for _ in x]).transpose()
            chart_data.add_color_grid("", xc, yc, zc, colormap="RdYlGn")

    return chart_data


def chart_stnd_regression(x_name, y_name, x_data, y_data, slope, intercept, model, y_marker=None) -> ChartData:
    x_min = min(0, numpy.min(x_data))
    x_max = max(0, numpy.max(x_data))
    chart_data = ChartData("standard regression")
    chart_data.caption.y_label = y_name
    chart_data.caption.x_label = x_name
    chart_data.caption.model = model

    add_regression_to_chart(x_name, y_name, x_data, y_data, slope, intercept, x_min, x_max, chart_data)

    if y_marker is not None:
        chart_data.add_line(get_text("Line of No Effect"), x_min, y_marker, x_max, y_marker, color="silver",
                            linestyle="dotted", zorder=1)

    return chart_data


def find_color_name(color: str) -> str:
    """
    Given a color as a hex string, e.g., #0123A5, find the closest named color from the CSS 4 color name list
    and return that name
    """
    if color_name_space == "X11/CSS4":
        color_names = CSS4_COLORS
    else:
        color_names = XKCD_COLORS
    names = list(color_names)
    dist = 10000
    match = "None"
    r, g, b = hex2color(color)
    for n in names:
        rx, gx, bx = hex2color(color_names[n])
        # Squared Euclidean distance in RGB space should be good enough
        #  Squared is more computationally efficient than non-squared, as we skip calculating the square-root
        d = (rx-r)**2 + (gx-g)**2 + (bx-b)**2
        if d < dist:
            match = n
            dist = d
    if color_name_space == "xkcd":
        return match[5:]
    return match
