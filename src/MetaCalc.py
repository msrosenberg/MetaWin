import sys
import webbrowser
from PyQt6.QtWidgets import QMainWindow, QApplication, QPlainTextEdit, QPushButton, QWidget, QHBoxLayout, \
    QVBoxLayout, QLabel, QLineEdit, QInputDialog, QListWidget
from PyQt6.QtGui import QIcon, QAction
import MetaCalcFunctions
from MetaCalcAbout import MetaCalcAbout
import MetaWinMessages
import MetaWinConstants


class MetaCalc(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__decimals = 6
        self.__output_box = None
        self.__list_widget = None
        self.__labels = []
        self.__edits = []
        self.__nedits = 4
        self.about = None
        self.toolbar = None
        self.help = MetaWinConstants.help_index["metacalc"]
        self.init_ui()

    def init_ui(self):
        # define toolbar
        close_action = QAction(QIcon(MetaWinConstants.exit_icon), "Exit", self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(QApplication.quit)
        close_action.setStatusTip("Exit")
        decimal_action = QAction(QIcon(MetaWinConstants.decimal_icon), "Decimal Places", self)
        decimal_action.setShortcut("Ctrl+D")
        decimal_action.triggered.connect(self.set_decimal_places)
        decimal_action.setStatusTip("images/Decimal Places")
        about_action = QAction(QIcon(MetaWinConstants.metawin_icon), "About", self)
        about_action.triggered.connect(self.show_about)
        about_action.setStatusTip("About")
        help_action = QAction(QIcon(MetaWinConstants.help_icon), "Help", self)
        help_action.setShortcut("Ctrl+H")
        help_action.triggered.connect(self.show_help)
        help_action.setStatusTip("Help")
        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.toolbar.addAction(close_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(decimal_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(help_action)
        self.toolbar.addAction(about_action)

        # define main area
        function_widget = QListWidget()
        self.__list_widget = function_widget
        function_widget.setMinimumWidth(180)
        function_widget.currentItemChanged.connect(self.on_function_changed)
        input_layout = QVBoxLayout()
        for i in range(self.__nedits):
            label = QLabel()
            label.setMinimumWidth(180)
            edit = QLineEdit()
            edit.setMinimumWidth(180)
            edit.setObjectName("Edit" + str(i))
            label.setText("Label" + str(i))
            input_layout.addWidget(label)
            input_layout.addWidget(edit)
            self.__labels.append(label)
            self.__edits.append(edit)
        input_layout.addStretch(1)
        compute_button = QPushButton(QIcon(MetaWinConstants.gear_icon), "Compute")
        compute_button.clicked.connect(self.on_compute_clicked)
        input_layout.addWidget(compute_button)
        self.__output_box = QPlainTextEdit()
        self.__output_box.setMinimumWidth(180)

        # load functions
        function_list = MetaCalcFunctions.load_all_functions()
        first_item = None
        for f in function_list:
            new_item = MetaCalcFunctions.MetaCalcListItem()
            new_item.setText(f.name)
            new_item.mc_function = f
            if first_item is None:
                first_item = new_item
            function_widget.addItem(new_item)
        function_widget.setCurrentItem(first_item)

        main_layout = QHBoxLayout()
        main_layout.addWidget(function_widget)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.__output_box)

        main_area = QWidget()
        main_area.setLayout(main_layout)
        self.setCentralWidget(main_area)

        # general window options
        self.resize(800, 400)
        self.setWindowIcon(QIcon(MetaWinConstants.calculator_icon))
        self.setWindowTitle("Statistical Calculator")

    def set_decimal_places(self):
        x, ok_pressed = QInputDialog.getInt(self, "Decimals", "Number of Decimal Places", self.__decimals, 0, 15, 1)
        if ok_pressed:
            self.__decimals = x

    def format_str(self) -> str:
        return "0." + str(self.__decimals) + "f"

    def write_output(self, output):
        self.__output_box.appendHtml(output)

    def on_function_changed(self, current, _):
        for e in self.__edits:
            e.setText("")
        f = current.mc_function
        for i, inp in enumerate(f.input_fields):
            self.__labels[i].setText(inp.field_name)
            self.__labels[i].setEnabled(True)
            self.__edits[i].setEnabled(True)
        for i in range(f.n_inputs(), self.__nedits):
            self.__labels[i].setText("")
            self.__labels[i].setEnabled(False)
            self.__edits[i].setEnabled(False)

    def on_compute_clicked(self):
        inputs = (x.text() for x in self.__edits)
        current = self.__list_widget.currentItem()
        f = current.mc_function
        value, error_msg = f.do_calculation(f.input_fields, *inputs)
        if value is not None:
            self.write_output("<strong>{}</strong>".format(f.name))
            for i, inp in enumerate(f.input_fields):
                self.write_output("» {} = {}".format(inp.field_name, self.__edits[i].text()))
            self.write_output("→ " + f.output_text + " = " + format(value, self.format_str()))
            self.write_output("")
            # copy calculated value to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(format(value, self.format_str()))
        else:
            self.report_critical("Error", error_msg)

    def report_critical(self, title, message):
        MetaWinMessages.report_critical(self, title, message)

    def show_about(self):
        self.about = MetaCalcAbout()
        self.about.show()

    def show_help(self):
        webbrowser.open(self.help)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.processEvents()
    metacalc = MetaCalc()
    metacalc.show()
    sys.exit(app.exec())
