"""
Module containing dialog for filtering by values within columns
"""

import webbrowser

from PyQt6.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QCheckBox, QScrollArea, QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon

import MetaWinConstants
from MetaWinWidgets import add_ok_cancel_help_button_layout
from MetaWinLanguage import get_text


class FilterWithinColumnDialog(QDialog):
    def __init__(self, data, column):
        super().__init__()
        self.help = MetaWinConstants.help_index["filtering_data"]
        self.checkbox_list = []
        self.group_names = []
        self.init_ui(data, column)

    def init_ui(self, data, column):
        group_box = QWidget()
        group_layout = QVBoxLayout()
        group_data = []
        c = data.col_number(column)
        for r in range(data.nrows()):
            g = data.value(r, c)
            if g is not None:
                group_data.append(str(g.value))
        self.group_names = sorted(set(group_data))
        for group in self.group_names:
            new_check_box = QCheckBox(group)
            group_layout.addWidget(new_check_box)
            self.checkbox_list.append(new_check_box)
            if group in column.group_filter:
                new_check_box.setChecked(False)
            else:
                new_check_box.setChecked(True)
        group_layout.addStretch()
        group_box.setLayout(group_layout)
        scroll_box = QScrollArea()
        scroll_box.setWidget(group_box)
        scroll_box.setWidgetResizable(True)
        scroll_box.setFixedHeight(200)

        select_button = QPushButton(get_text("Select All"))
        select_button.clicked.connect(self.select_all)
        deselect_button = QPushButton(get_text("Deselect All"))
        deselect_button.clicked.connect(self.deselect_all)
        select_layout = QHBoxLayout()
        select_layout.addWidget(select_button)
        select_layout.addWidget(deselect_button)

        button_layout, _ = add_ok_cancel_help_button_layout(self)

        column_label = QLabel(column.label)
        column_label.setStyleSheet(MetaWinConstants.title_label_style)
        analysis_label = QLabel(get_text("Select Groups to Include in Analyses"))

        main_layout = QVBoxLayout()
        main_layout.addWidget(column_label)
        main_layout.addWidget(analysis_label)
        main_layout.addWidget(scroll_box)
        main_layout.addLayout(select_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Filter within Column"))

    def show_help(self):
        webbrowser.open(self.help)

    def select_all(self):
        for box in self.checkbox_list:
            box.setChecked(True)

    def deselect_all(self):
        for box in self.checkbox_list:
            box.setChecked(False)


def filter_within_column(sender, data, column) -> bool:
    """
    primary function for filtering by values within a column, this uses the dialog to determine the choices
    and stores those choices in the appropriate place

    it returns False if the procedure was canceled
    """
    sender.filter_within_col_dialog = FilterWithinColumnDialog(data, column)
    if sender.filter_within_col_dialog.exec():
        column.group_filter = []
        for i, name in enumerate(sender.filter_within_col_dialog.group_names):
            if not sender.filter_within_col_dialog.checkbox_list[i].isChecked():
                column.group_filter.append(name)
        return True
    return False
