"""
Module containing dialogs and functions for setting options for saving data and output. These functions only return
the options, the actual writing to file is handled by the calling functions
"""

import webbrowser
from typing import Optional, Tuple

from PyQt6.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QFrame, QGroupBox, QRadioButton, QLineEdit
from PyQt6.QtGui import QIcon, QIntValidator

import MetaWinConstants
from MetaWinWidgets import add_cancel_help_button_layout, add_ok_cancel_help_button_layout
from MetaWinLanguage import get_text


class SaveOutputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.output_format = MetaWinConstants.SAVE_TEXT
        self.help = MetaWinConstants.help_index["saving_output"]
        self.init_ui()

    def init_ui(self):

        format_layout = QVBoxLayout()
        plain_button = QPushButton(get_text("Plain Text"))
        plain_button.clicked.connect(self.plain_button_click)
        format_layout.addWidget(plain_button)
        html_button = QPushButton(get_text("HTML"))
        html_button.clicked.connect(self.html_button_click)
        format_layout.addWidget(html_button)
        md_button = QPushButton(get_text("Markdown"))
        md_button.clicked.connect(self.md_button_click)
        format_layout.addWidget(md_button)

        button_layout = add_cancel_help_button_layout(self)

        format_label = QLabel(get_text("Output Format"))
        format_label.setStyleSheet(MetaWinConstants.title_label_style)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(format_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(format_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Save Output"))

    def show_help(self):
        webbrowser.open(self.help)

    def plain_button_click(self):
        self.output_format = MetaWinConstants.SAVE_TEXT
        self.accept()

    def html_button_click(self):
        self.output_format = MetaWinConstants.SAVE_HTML
        self.accept()

    def md_button_click(self):
        self.output_format = MetaWinConstants.SAVE_MD
        self.accept()


class SaveDataDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.decimals_box = None
        self.comma_button = None
        self.tab_button = None
        self.space_button = None
        self.help = MetaWinConstants.help_index["saving_data"]
        self.init_ui()

    def init_ui(self):
        format_layout = QVBoxLayout()
        separator_box = QGroupBox("Field Separator")
        separator_layout = QVBoxLayout()
        self.tab_button = QRadioButton(get_text("Tabs"))
        self.comma_button = QRadioButton(get_text("Commas"))
        self.space_button = QRadioButton(get_text("Spaces"))
        separator_layout.addWidget(self.tab_button)
        separator_layout.addWidget(self.comma_button)
        separator_layout.addWidget(self.space_button)
        self.tab_button.setChecked(True)
        separator_box.setLayout(separator_layout)

        decimals_label = QLabel(get_text("Number of decimal places"))
        self.decimals_box = QLineEdit()
        self.decimals_box.setText("4")
        self.decimals_box.setValidator(QIntValidator(0, 10))

        format_label = QLabel(get_text("Output Format"))
        format_label.setStyleSheet(MetaWinConstants.title_label_style)

        format_layout.addWidget(separator_box)
        format_layout.addWidget(decimals_label)
        format_layout.addWidget(self.decimals_box)

        button_layout, ok_button = add_ok_cancel_help_button_layout(self)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Panel)
        main_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_frame.setLineWidth(2)
        main_frame.setLayout(format_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(format_label)
        main_layout.addWidget(main_frame)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Save Data"))

    def show_help(self):
        webbrowser.open(self.help)


def save_output(sender) -> Optional[int]:
    """
    use the dialog to get the format for saving the output text
    """
    sender.save_output_format = SaveOutputDialog()
    if sender.save_output_format.exec():
        return sender.save_output_format.output_format
    else:
        return None


def save_data(sender) -> Tuple[Optional[str], int]:
    """
    use the dialog to get the separator and decimal places for saving the data matrix
    """
    sender.save_data_format = SaveDataDialog()
    if sender.save_data_format.exec():
        decimals = int(sender.save_data_format.decimals_box.text())
        if sender.save_data_format.space_button.isChecked():
            separator = " "
        elif sender.save_data_format.comma_button.isChecked():
            separator = ","
        else:
            separator = "\t"
        return separator, decimals
    else:
        return None, 4
