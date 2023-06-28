"""
Module containing dialogs and functions for setting options for saving data and output. These functions only return
the options, the actual writing to file is handled by the calling functions
"""

import webbrowser
from typing import Tuple, Optional

from PyQt6.QtWidgets import QDialog, QCheckBox, QLabel, QTableWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLineEdit, QFrame, QTableWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6 import QtCore

import MetaWinMessages
from MetaWinData import MetaWinData
import MetaWinConstants
from MetaWinWidgets import add_ok_cancel_help_button_layout
import MetaWinTree
from MetaWinLanguage import get_text


class ImportTextOptions:
    def __init__(self):
        self.do_tab = True
        self.do_space = False
        self.do_comma = False
        self.do_other = False
        self.other = ""
        self.do_consecutive = False
        self.col_headers = False
        self.row_labels = False
        self.filename = ""

    def delimiters(self) -> str:
        split_chars = ""
        if self.do_comma:
            split_chars += ","
        if self.do_tab:
            split_chars += "\t"
        if self.do_space:
            split_chars += " "
        if self.do_other:
            split_chars += self.other
        return split_chars

    def delimiters_text(self) -> list:
        split_chars = []
        if self.do_comma:
            split_chars.append("commas")
        if self.do_tab:
            split_chars.append("tabs")
        if self.do_space:
            split_chars.append("spaces")
        if self.do_other:
            split_chars.extend(list(self.other))
        return split_chars

    def return_output(self) -> list:
        output_blocks = [["<h3>{}</h3>".format(get_text("Load Data"))]]
        output = [get_text("Loaded data from {}").format(self.filename),
                  "→ {}: ".format(get_text("Delimiters")) + ", ".join(self.delimiters_text())]
        if self.col_headers:
            output.append("→ {}".format(get_text("Column headers in first row")))
        if self.row_labels:
            output.append("→ {}".format(get_text("Row labels in first column")))
        output_blocks.append(output)
        return output_blocks


class ImportTextDialog(QDialog):
    def __init__(self, filename: str, rawdata: list):
        super().__init__()
        self.__tab_checkbox = None
        self.__space_checkbox = None
        self.__comma_checkbox = None
        self.__other_checkbox = None
        self.__other_edit = None
        self.__consecutive_checkbox = None
        self.__raw_data = rawdata
        self.__preview_area = None
        self.__col_header_checkbox = None
        self.__row_label_checkbox = None
        self.filename = filename
        self.help = MetaWinConstants.help_index["importing_data"]
        self.init_ui()

    def init_ui(self):
        delimiter_label = QLabel(get_text("Column Delimiters"))
        self.__space_checkbox = QCheckBox(get_text("Spaces"))
        self.__space_checkbox.clicked.connect(self.refresh_data)
        self.__tab_checkbox = QCheckBox(get_text("Tabs"))
        self.__tab_checkbox.setChecked(True)
        self.__tab_checkbox.clicked.connect(self.refresh_data)
        self.__comma_checkbox = QCheckBox(get_text("Commas"))
        self.__comma_checkbox.clicked.connect(self.refresh_data)
        self.__other_checkbox = QCheckBox(get_text("Other(s)"))
        self.__other_checkbox.clicked.connect(self.refresh_data)
        self.__other_edit = QLineEdit("")
        self.__other_edit.textChanged.connect(self.refresh_data)
        self.__consecutive_checkbox = QCheckBox(get_text("Treat Consecutive Delimiters as One"))
        self.__consecutive_checkbox.clicked.connect(self.refresh_data)
        choice_frame = QFrame()
        choice_frame.setFrameShape(QFrame.Shape.Panel)
        choice_frame.setFrameShadow(QFrame.Shadow.Sunken)
        choice_frame.setLineWidth(2)

        choice_layout = QVBoxLayout()
        choice_layout.addWidget(delimiter_label)
        options_layout = QGridLayout()
        options_layout.addWidget(self.__tab_checkbox, 0, 0)
        options_layout.addWidget(self.__space_checkbox, 0, 1)
        options_layout.addWidget(self.__comma_checkbox, 0, 2)
        options_layout.addWidget(self.__other_checkbox, 0, 3)
        options_layout.addWidget(self.__consecutive_checkbox, 1, 0, 1, 3)
        options_layout.addWidget(self.__other_edit, 1, 3)
        choice_layout.addLayout(options_layout)
        choice_frame.setLayout(choice_layout)
        top_layout = QHBoxLayout()
        top_layout.addWidget(choice_frame)

        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.Shape.Panel)
        header_frame.setFrameShadow(QFrame.Shadow.Sunken)
        header_frame.setLineWidth(2)
        header_layout = QVBoxLayout()
        self.__col_header_checkbox = QCheckBox(get_text("First Row Contains Column Headers"))
        self.__col_header_checkbox.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.__col_header_checkbox)
        self.__row_label_checkbox = QCheckBox(get_text("First Column Contains Row Labels"))
        self.__row_label_checkbox.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.__row_label_checkbox)

        header_frame.setLayout(header_layout)
        top_layout.addWidget(header_frame)
        top_layout.addStretch(1)

        button_layout, _ = add_ok_cancel_help_button_layout(self, vertical=True)
        top_layout.addLayout(button_layout)

        nrows = 5
        ncols = 5
        self.__preview_area = QTableWidget(nrows, ncols)
        self.refresh_data()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.__preview_area)
        self.setLayout(main_layout)

        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("Import Text Options"))

    def return_options(self):
        import_options = ImportTextOptions()
        import_options.do_tab = self.__tab_checkbox.isChecked()
        import_options.do_space = self.__space_checkbox.isChecked()
        import_options.do_comma = self.__comma_checkbox.isChecked()
        import_options.do_other = self.__other_checkbox.isChecked()
        import_options.other = self.__other_edit.text()
        import_options.do_consecutive = self.__consecutive_checkbox.isChecked()
        import_options.col_headers = self.__col_header_checkbox.isChecked()
        import_options.row_labels = self.__row_label_checkbox.isChecked()
        import_options.filename = self.filename
        return import_options

    def refresh_data(self):
        tmp_data = split_text_data(self.__raw_data, self.return_options())
        nrows = tmp_data.nrows()
        ncols = tmp_data.ncols()
        self.__preview_area.clearContents()
        self.__preview_area.setRowCount(nrows)
        self.__preview_area.setColumnCount(ncols)
        row_headers = [row.label for row in tmp_data.rows]
        col_headers = [col.label for col in tmp_data.cols]
        self.__preview_area.setVerticalHeaderLabels(row_headers)
        self.__preview_area.setHorizontalHeaderLabels(col_headers)
        for r in range(nrows):
            for c in range(ncols):
                data = tmp_data.value(r, c)
                if data is None:
                    new_item = QTableWidgetItem("")
                else:
                    new_item = QTableWidgetItem(data.value)
                new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.__preview_area.setItem(r, c, new_item)

    def show_help(self):
        webbrowser.open(self.help)


def strip_quotes(x: str) -> str:
    """
    strip start and end double quotes when present, usually if generated from csv file
    """
    if len(x) == 1:  # just in case input is a single " character
        return x
    elif x.startswith("\"") and x.endswith("\""):
        return x[1:len(x)-1]
    else:
        return x


def split_line(line: str, split_chars: str, consecutive: bool) -> list:
    """
    function to split a text line into columns

    this function allows for multiple possible delimiters simultaneously, as well as optionally treating
    consecutive delimiters as a single one (mostly for use in importing space aligned tables

    will also automatically strip start and end double quotes when present (usually from csv)
    """
    items = []
    temp_str = ""
    for i, c in enumerate(line):
        if c not in split_chars:
            temp_str += c
        elif consecutive:
            if i > 0:
                if line[i-1] not in split_chars:
                    items.append(strip_quotes(temp_str))
                    temp_str = ""
            else:
                items.append("")
        else:
            items.append(strip_quotes(temp_str))
            temp_str = ""
    if temp_str != "":
        items.append(strip_quotes(temp_str))
    return items


def split_text_data(raw_data: list, import_options: ImportTextOptions) -> MetaWinData:
    new_data = MetaWinData()
    nrows = 0
    ncols = 0
    split_chars = import_options.delimiters()
    if import_options.col_headers:
        r = raw_data[0]
        cols = split_line(r.rstrip(), split_chars, import_options.do_consecutive)
        if import_options.row_labels:
            i = 1
        else:
            i = 0
        for c in cols[i:]:
            new_data.add_col(c)
        ncols = len(cols)
        start_row = 1
    else:
        start_row = 0
    for r in raw_data[start_row:]:
        if r.strip() != "":
            nrows += 1
            cols = split_line(r.rstrip(), split_chars, import_options.do_consecutive)
            if import_options.row_labels:
                new_data.add_row(cols[0])
                cols = cols[1:]
            else:
                new_data.add_row("{} {}".format(get_text("Row"), nrows))
            if len(cols) > ncols:  # create new columns as needed
                for c in range(ncols, len(cols)):
                    new_data.add_col("{} {}".format(get_text("Column"), c + 1))
                ncols = len(cols)
            for c, d in enumerate(cols):
                if d.strip() != "":
                    new_data.add_value(nrows-1, c, d.strip())
    return new_data


def convert_strings_to_numbers(data: MetaWinData) -> None:
    """
    Check each imported data value and convert to int (preferred) or float if it is a number; otherwise
    leave as a string
    """
    for c in data.cols:
        for d in c.values:
            try:
                x = int(d.value)
                d.value = x
            except ValueError:
                try:
                    x = float(d.value)
                    d.value = x
                except ValueError:
                    pass


def import_data(sender, filename: str) -> Tuple[Optional[MetaWinData], Optional[list]]:
    """
    Given a filename attempt to read the data in it

    If successful, returns the data as an object and a list containing output text
    """
    try:
        with open(filename, "r") as infile:
            try:
                indata = infile.readlines()
                sender.import_text = ImportTextDialog(filename, indata)
                if sender.import_text.exec():
                    import_options = sender.import_text.return_options()
                    data = split_text_data(indata, import_options)
                    # set_column_types(data)
                    convert_strings_to_numbers(data)

                    output_blocks = import_options.return_output()
                    return data, output_blocks
            except UnicodeDecodeError:
                MetaWinMessages.report_critical(sender, get_text("Import Error"),
                                                get_text("error_not_text_file").format(filename))
    except IOError:
        MetaWinMessages.report_critical(sender, get_text("Input/Output Error"),
                                        get_text("Error reading file {}").format(filename))
    return None, None


def import_phylogeny(sender, filename: str) -> Tuple[Optional[MetaWinTree.Node], Optional[list]]:
    """
    Given a filename attempt to read the phylogeny from it

    If successful, returns the root of the phylogeny and a list containing output text
    """
    try:
        with open(filename, "r") as infile:
            newick_str = infile.read()
        try:
            new_phylogeny = MetaWinTree.read_newick_tree(newick_str)
            output_blocks = [["<h3>{}</h3>".format(get_text("Load Phylogeny"))]]
            output = [get_text("Imported phylogeny from {}").format(filename),
                      get_text("Imported phylogeny contains {} tips").format(new_phylogeny.n_tips())]
            output_blocks.append(output)
            return new_phylogeny, output_blocks
        except IndexError:
            MetaWinMessages.report_critical(sender, get_text("Import Error"),
                                            get_text("error_not_newick").format(filename))
    except IOError:
        MetaWinMessages.report_critical(sender, get_text("Input/Output Error"),
                                        get_text("Error reading file {}").format(filename))
    return None, None
