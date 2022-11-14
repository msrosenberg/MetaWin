"""
Module containing visual widgets which may be used across multiple dialogs
"""

from typing import Optional

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QAbstractItemView, QListWidgetItem, \
    QLabel, QComboBox, QCheckBox, QGroupBox, QGridLayout, QLineEdit, QColorDialog, QProgressDialog
from PyQt6.QtGui import QIcon, QColor, QDoubleValidator
from PyQt6 import QtCore

import MetaWinConstants
from MetaWinLanguage import get_text


class DragDropList(QListWidget):
    """
    A specialized QListWidget designed for drag-and-drop of entries among multiple instances of this
    type of widget
    """
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropOverwriteMode(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)

    def dropEvent(self, drop_event):
        source = drop_event.source()
        items = source.selectedItems()
        for i in items:
            source.takeItem(source.indexFromItem(i).row())
            self.addItem(i)


class CustomListItem(QListWidgetItem):
    """
    This is a standard QListWidgetItem to which an extra property has been added to allow us to easily track
    which data column is associated with which item as they get moved around and rearranged
    """
    def __init__(self, col):
        super().__init__()
        self.column = col


class FigureEditPanel(QGroupBox):
    """
    This is a standard QGroupBox to which an extra property has been added to allow us to easily track
    which chart data element is associated with it
    """
    def __init__(self):
        super().__init__()
        self.data = None


class ColorButton(QPushButton):
    """
    This widget is a push button for changing colors. It stores its current color, as well as displays the
    button in that color. Pressing the button calls the color dialog and updates its color if necessary.
    """
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.setStyleSheet("background-color: " + color)
        self.clicked.connect(self.pushed)

    def pushed(self):
        new_color = QColorDialog.getColor(initial=QColor(self.color))
        if new_color.isValid():
            self.color = new_color.name()
            self.setStyleSheet("background-color: " + new_color.name())


def add_ok_button(sender) -> QPushButton:
    """
    Create an Ok button
    """
    ok_button = QPushButton(QIcon(MetaWinConstants.ok_icon), get_text("Ok"))
    ok_button.clicked.connect(sender.accept)
    return ok_button


def add_cancel_button(sender) -> QPushButton:
    """
    Create a Cancel button
    """
    cancel_button = QPushButton(QIcon(MetaWinConstants.cancel_icon), get_text("Cancel"))
    cancel_button.clicked.connect(sender.reject)
    return cancel_button


def add_help_button(sender) -> QPushButton:
    """
    Create a Help button and connect it to the show_help function in the standard dialog
    """
    help_button = QPushButton(QIcon(MetaWinConstants.help_icon), get_text("Help"))
    help_button.clicked.connect(sender.show_help)
    return help_button


def add_ok_cancel_help_button_layout(sender, vertical: bool = False):
    """
    Create a layout containing ok, cancel, and help buttons

    By default these will be laid out horizontally, but setting the vertical parameter to True will
    optionally create a vertical layout

    The function returns both the layout and the pointer to the ok button in case it's behavior
    when clicked needs to be overwritten
    """
    if vertical:
        button_layout = QVBoxLayout()
    else:
        button_layout = QHBoxLayout()
    ok_button = add_ok_button(sender)
    button_layout.addWidget(ok_button)
    button_layout.addWidget(add_cancel_button(sender))
    button_layout.addWidget(add_help_button(sender))
    return button_layout, ok_button


def add_cancel_help_button_layout(sender, vertical: bool = False):
    """
    Create a layout containing cancel and help buttons

    By default these will be laid out horizontally, but setting the vertical parameter to True will
    optionally create a vertical layout
    """
    if vertical:
        button_layout = QVBoxLayout()
    else:
        button_layout = QHBoxLayout()
    button_layout.addWidget(add_cancel_button(sender))
    button_layout.addWidget(add_help_button(sender))
    return button_layout


def add_drag_drop_list() -> DragDropList:
    return DragDropList()


def create_list_item(column):
    new_item = CustomListItem(column)
    new_item.setText(column.label)
    return new_item


def add_effect_choice_to_dialog(sender, data, last_effect: Optional = None, last_var: Optional = None,
                                include_log: bool = True):
    """
    Create and add several common items related to effect sizes and variances to the sender dialog

    These include a label and combo box for effect sizes, a label and combo box for variances, and
    an optional checkbox for whether the effect size is log-transformed. The combo boxes are
    auto-filled with all of the columns in the provided data.

    The last_effect parameter is an optional parameter that specifies the last chosen
    effect size column. If it is not None, this column is auto-selected in the combo box. If it
    has an associated variance, that variance is also auto-selected. If that
    column is known to contain a log-transformed effect size, the log-transform box (if
    included) will be auto-checked as well.
    """
    effect_size_label = QLabel(get_text("Effect Size"))
    variance_label = QLabel(get_text("Effect Size Variance"))
    sender.effect_size_box = QComboBox()
    sender.variance_box = QComboBox()
    sender.columns = data.cols
    if include_log:
        sender.log_transform_box = QCheckBox(get_text("Log Transformed Measure"))
        if last_effect is not None:
            if last_effect.log_transformed():
                sender.log_transform_box.setChecked(True)
    for col in sender.columns:
        sender.effect_size_box.addItem(col.label)
        sender.variance_box.addItem(col.label)
    if last_effect is not None:
        if last_var is None:
            last_var = last_effect.effect_var
        for c, col in enumerate(sender.columns):
            if col == last_effect:
                sender.effect_size_box.setCurrentIndex(c)
            elif col == last_var:
                sender.variance_box.setCurrentIndex(c)

    return effect_size_label, variance_label


def add_figure_edit_panel(sender):
    edit_groupbox = FigureEditPanel()
    edit_groupbox.data = sender
    edit_groupbox.setTitle(sender.name)
    edit_groupbox.setCheckable(True)
    edit_groupbox.setChecked(sender.visible)
    edit_layout = QGridLayout()
    edit_groupbox.setLayout(edit_layout)
    return edit_groupbox, edit_layout


# --- widgets for graph editing --- #
def add_chart_color_button(title, color, def_color="black"):
    label = QLabel(title)
    no_color_box = QCheckBox(get_text("No fill color"))
    if color == "none":
        no_color_box.setChecked(True)
        button = ColorButton(def_color)
    else:
        no_color_box.setChecked(False)
        button = ColorButton(color)
    return button, label, no_color_box


def add_chart_line_width(title, linewidth):
    label = QLabel(title)
    width_box = QLineEdit()
    width_box.setText(str(linewidth))
    width_box.setValidator(QDoubleValidator(0, 20, 3))
    return width_box, label


def add_chart_marker_size(title, size):
    label = QLabel(title)
    size_box = QLineEdit()
    size_box.setText(str(size))
    size_box.setValidator(QDoubleValidator(0, 1000, 3))
    return size_box, label


def add_chart_line_style(title, linestyle, options):
    label = QLabel(title)
    style_box = QComboBox()
    for s in options:
        style_box.addItem(s)
    style_box.setCurrentIndex(options.index(linestyle))
    return style_box, label


def add_chart_marker_style(title, style, options):
    label = QLabel(title)
    style_box = QComboBox()
    for s in options:
        style_box.addItem(s)
    index = list(options.values()).index(style)
    style_box.setCurrentIndex(index)
    return style_box, label


def add_chart_line_edits(color_text, color, width_text, width, style_text, style, line_styles):
    color_label, color_button, _ = add_chart_color_button(color_text, color)
    width_label, width_box = add_chart_line_width(width_text, width)
    style_label, style_box = add_chart_line_style(style_text, style, line_styles)
    return color_label, color_button, width_label, width_box, style_label, style_box


def progress_bar(sender, title: str, text: str, max_val: int):
    pb = QProgressDialog(sender)
    pb.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
    pb.setWindowTitle(title)
    pb.setLabelText(text)
    pb.setMinimum(0)
    pb.setMaximum(max_val)
    pb.setCancelButton(None)
    pb.setValue(0)
    return pb
