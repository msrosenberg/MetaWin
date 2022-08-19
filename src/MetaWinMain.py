"""
Module containing the primary GUI window for MetaWin
"""

import webbrowser
import datetime
import sys

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QTableWidget, QFileDialog, QTableWidgetItem, QMenu, QInputDialog, \
    QApplication, QTextEdit, QColorDialog, QToolBar, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QFontDialog, \
    QWidgetAction, QComboBox
from PyQt6.QtGui import QIcon, QColor, QAction, QActionGroup
from PyQt6 import QtCore
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

import MetaWinCharts
from MetaWinAbout import MetaWinAbout
from MetaCalc import MetaCalc
from MetaWinUtils import format_number, check_version, version_str
import MetaWinConstants
import MetaWinImport
import MetaWinSave
import MetaWinEffects
import MetaWinMessages
import MetaWinAnalysis
import MetaWinDraw
import MetaWinFilter
import MetaWinLanguage
from MetaWinLanguage import get_text
import MetaWinConfig


class MainWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.data = None
        self.data_area = None
        self.output_area = None
        self.graph_area = None
        self.phylogeny = None
        self.tree_area = None
        self.tree_info_label = None
        self.clicked_header = None
        MetaWinLanguage.current_language = config["language"]
        self.output_decimals = config["output decimals"]
        self.data_decimals = config["data decimals"]
        self.filtered_row_color = config["filtered row color"]
        self.filtered_col_color = config["filtered col color"]
        self.auto_update_check = config["auto update check"]
        self.alpha = config["alpha"]
        self.help = MetaWinConstants.help_index["metawin"]
        self.localization_help = MetaWinConstants.help_index["localization"]
        self.main_area = None
        self.about = None
        self.mc = None
        self.last_effect = None
        self.last_var = None
        self.show_data_toolbar = True
        self.data_toolbar_action = None
        self.data_toolbar = None
        self.graph_toolbar = None
        self.save_graph_action = None
        self.graph_layout = None
        self.show_output_toolbar = True
        self.output_toolbar_action = None
        self.output_toolbar = None
        self.show_tree_area = False
        self.tree_area_action = None
        self.tree_toolbar = None
        self.auto_update_check_action = None
        # self.language_actions = None
        self.language_box = None
        self.output_saved = True
        self.data_saved = True
        self.empty_col_num = 10
        self.empty_row_num = 15
        self.chart_data = None
        self.chart_caption = ""
        self.init_ui()

    def init_ui(self):
        # ----main menu----
        # file menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu(get_text("File"))
        load_data_action = QAction(QIcon(MetaWinConstants.open_icon), get_text("Load Data"), self)
        load_data_action.triggered.connect(self.load_data)
        file_menu.addAction(load_data_action)
        save_data_action = QAction(QIcon(MetaWinConstants.save_data_icon), get_text("Save Data"), self)
        save_data_action.setShortcut("Ctrl+S")
        save_data_action.triggered.connect(self.click_save_data)
        file_menu.addAction(save_data_action)
        clear_data_action = QAction(QIcon(MetaWinConstants.clear_icon), get_text("Clear Data"), self)
        clear_data_action.triggered.connect(self.clear_data)
        file_menu.addAction(clear_data_action)

        file_menu.addSeparator()
        save_output_action = QAction(QIcon(MetaWinConstants.save_output_icon), get_text("Save Output"), self)
        save_output_action.setShortcut("Ctrl+O")
        save_output_action.triggered.connect(self.click_save_output)
        file_menu.addAction(save_output_action)

        file_menu.addSeparator()
        close_action = QAction(QIcon(MetaWinConstants.exit_icon), get_text("Exit"), self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(QApplication.quit)
        close_action.setStatusTip(get_text("Exit"))
        file_menu.addAction(close_action)

        # analysis menu
        analysis_menu = menubar.addMenu(get_text("Compute"))
        effect_action = QAction(QIcon(MetaWinConstants.measure_icon), get_text("Effect Sizes"), self)
        effect_action.triggered.connect(self.calculate_effect_sizes)
        analysis_menu.addAction(effect_action)
        meta_analysis_action = QAction(QIcon(MetaWinConstants.analysis_icon), get_text("Analysis"), self)
        meta_analysis_action.triggered.connect(self.meta_analysis)
        analysis_menu.addAction(meta_analysis_action)
        analysis_menu.addSeparator()
        calculator_action = QAction(QIcon(MetaWinConstants.calculator_icon), get_text("Statistical Calculator"), self)
        calculator_action.triggered.connect(self.show_calculator)
        analysis_menu.addAction(calculator_action)

        # draw menu
        draw_menu = menubar.addMenu(get_text("Draw"))
        draw_scatter_action = QAction(QIcon(MetaWinConstants.scatter_icon), get_text("Scatter/Funnel Plot"), self)
        draw_scatter_action.triggered.connect(self.draw_scatter_plot)
        draw_menu.addAction(draw_scatter_action)
        draw_histogram_action = QAction(QIcon(MetaWinConstants.histogram_icon), get_text("Weighted Histogram"), self)
        draw_histogram_action.triggered.connect(self.draw_histogram)
        draw_menu.addAction(draw_histogram_action)
        draw_forest_action = QAction(QIcon(MetaWinConstants.forest_plot_icon), get_text("Forest Plot"), self)
        draw_forest_action.triggered.connect(self.draw_forest_plot)
        draw_menu.addAction(draw_forest_action)
        draw_normal_quantile_action = QAction(QIcon(MetaWinConstants.normal_quantile_icon),
                                              get_text("Normal Quantile Plot"), self)
        draw_normal_quantile_action.triggered.connect(self.draw_normal_quantile_plot)
        draw_menu.addAction(draw_normal_quantile_action)
        draw_radial_action = QAction(QIcon(MetaWinConstants.radial_plot_icon),
                                     get_text("Galbraith (Radial) Plot"), self)
        draw_radial_action.triggered.connect(self.draw_radial_plot)
        draw_menu.addAction(draw_radial_action)

        # ---filtering---
        filter_row_color_action = QAction(QIcon(MetaWinConstants.row_filter_color_icon),
                                          get_text("Filtered Row Color"), self)
        filter_row_color_action.triggered.connect(self.set_filter_row_color)
        filter_col_color_action = QAction(QIcon(MetaWinConstants.col_filter_color_icon),
                                          get_text("Filtered within Column Color"), self)
        filter_col_color_action.triggered.connect(self.set_filter_col_color)
        clear_filters_action = QAction(QIcon(MetaWinConstants.clear_filter_icon), get_text("Clear Filters"), self)
        clear_filters_action.triggered.connect(self.clear_filters)

        # options menus
        options_menu = menubar.addMenu(get_text("Options"))
        # data options submenu
        data_options_menu = QMenu(get_text("Data Options"), self)
        data_options_menu.setIcon(QIcon(MetaWinConstants.data_icon))
        data_decimal_action = QAction(QIcon(MetaWinConstants.decimal_icon), get_text("Decimal Places"), self)
        data_decimal_action.triggered.connect(self.set_data_decimal_places)
        data_options_menu.addAction(data_decimal_action)
        data_options_menu.addAction(filter_row_color_action)
        data_options_menu.addAction(filter_col_color_action)
        self.data_toolbar_action = QAction(QIcon(MetaWinConstants.hide_toolbar_icon),
                                           get_text("Hide Data Toolbar"), self)
        # self.data_toolbar_action.setCheckable(True)
        # self.data_toolbar_action.setChecked(True)
        self.data_toolbar_action.triggered.connect(self.show_data_toolbar_click)
        data_options_menu.addAction(self.data_toolbar_action)
        options_menu.addMenu(data_options_menu)
        # output options submenu
        output_options_menu = QMenu(get_text("Output Options"), self)
        output_options_menu.setIcon(QIcon(MetaWinConstants.output_icon))
        output_decimal_action = QAction(QIcon(MetaWinConstants.decimal_icon), get_text("Decimal Places"), self)
        output_decimal_action.triggered.connect(self.set_output_decimal_places)
        output_options_menu.addAction(output_decimal_action)
        output_alpha_action = QAction(QIcon(MetaWinConstants.alpha_icon), get_text("Significance Level"), self)
        output_alpha_action.triggered.connect(self.set_alpha_significance)
        output_options_menu.addAction(output_alpha_action)
        output_font_action = QAction(QIcon(MetaWinConstants.font_icon), get_text("Font"), self)
        output_font_action.triggered.connect(self.set_output_font)
        output_options_menu.addAction(output_font_action)
        self.output_toolbar_action = QAction(QIcon(MetaWinConstants.hide_toolbar_icon),
                                             get_text("Hide Output Toolbar"), self)
        # self.output_toolbar_action.setCheckable(True)
        # self.output_toolbar_action.setChecked(True)
        self.output_toolbar_action.triggered.connect(self.show_output_toolbar_click)
        output_options_menu.addAction(self.output_toolbar_action)
        options_menu.addMenu(output_options_menu)

        self.tree_area_action = QAction(QIcon(MetaWinConstants.tree_icon), get_text("Show Phylogeny Tab"), self)
        # self.tree_area_action.setCheckable(True)
        # self.tree_area_action.setChecked(False)
        self.tree_area_action.triggered.connect(self.show_tree_area_action_clicked)
        options_menu.addAction(self.tree_area_action)

        self.auto_update_check_action = QAction(get_text("Automatically check for udpates"), self)
        self.auto_update_check_action.setCheckable(True)
        self.auto_update_check_action.setChecked(self.auto_update_check)
        self.auto_update_check_action.triggered.connect(self.click_auto_update_check)
        options_menu.addAction(self.auto_update_check_action)

        # languages
        language_menu = QMenu(get_text("Language"), self)
        language_menu.setIcon(QIcon(MetaWinConstants.language_icon))

        language_box_action = QWidgetAction(self)
        self.language_box = QComboBox()
        current_lang = 0
        for i, lang in enumerate(MetaWinLanguage.language_list()):
            self.language_box.addItem(QIcon(MetaWinLanguage.LANGUAGE_FLAGS[lang]), lang)
            if lang == MetaWinLanguage.current_language:
                current_lang = i
        self.language_box.setCurrentIndex(current_lang)
        self.language_box.currentIndexChanged.connect(self.language_clicked)
        language_box_action.setDefaultWidget(self.language_box)
        language_menu.addAction(language_box_action)

        # self.language_actions = QActionGroup(self)
        # self.language_actions.setExclusive(True)
        # for lang in MetaWinLanguage.language_list():
        #     l_action = QAction(lang, self)
        #     l_action.setCheckable(True)
        #     self.language_actions.addAction(l_action)
        #     if lang == MetaWinLanguage.current_language:
        #         l_action.setChecked(True)
        #     else:
        #         l_action.setChecked(False)
        #     l_action.triggered.connect(self.language_clicked)
        #     language_menu.addAction(l_action)
        language_menu.addSeparator()
        localization_action = QAction(QIcon(MetaWinConstants.help_icon), get_text("About Localization"), self)
        localization_action.triggered.connect(self.localization)
        language_menu.addAction(localization_action)
        options_menu.addMenu(language_menu)

        # help menu
        help_menu = menubar.addMenu(get_text("Help"))
        about_action = QAction(QIcon(MetaWinConstants.metawin_icon), get_text("About MetaWin"), self)
        about_action.triggered.connect(self.show_about)
        help_action = QAction(QIcon(MetaWinConstants.help_icon), get_text("Help"), self)
        help_action.setShortcut("Ctrl+H")
        help_action.triggered.connect(self.show_help)
        update_check_action = QAction(QIcon(MetaWinConstants.update_icon), get_text("Check for updates"), self)
        update_check_action.triggered.connect(self.click_check_for_update)
        help_menu.addAction(help_action)
        help_menu.addSeparator()
        help_menu.addAction(about_action)
        help_menu.addAction(update_check_action)

        # ----toolbar----
        main_toolbar = self.addToolBar("Toolbar")
        main_toolbar.setFloatable(False)
        main_toolbar.setMovable(False)
        main_toolbar.addAction(effect_action)
        main_toolbar.addAction(meta_analysis_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(help_action)
        main_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # ----main area----
        self.main_area = QTabWidget(self)
        self.setCentralWidget(self.main_area)

        # ---data tab---
        data_frame = QFrame()
        data_frame_layout = QHBoxLayout()
        self.data_toolbar = QToolBar()
        self.data_toolbar.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.data_toolbar.addAction(load_data_action)
        self.data_toolbar.addAction(save_data_action)
        self.data_toolbar.addAction(clear_data_action)
        self.data_toolbar.addSeparator()
        self.data_toolbar.addAction(filter_row_color_action)
        self.data_toolbar.addAction(filter_col_color_action)
        self.data_toolbar.addAction(clear_filters_action)
        self.data_toolbar.addSeparator()
        self.data_toolbar.addAction(data_decimal_action)
        data_frame_layout.addWidget(self.data_toolbar)
        self.data_area = QTableWidget(self.empty_row_num, self.empty_col_num)
        self.data_area.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.data_area.setStyleSheet("QHeaderView::section {background-color: Gainsboro}"
                                     "QTableCornerButton::section {background: Gainsboro}")
        self.data_area.horizontalHeader().setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.data_area.horizontalHeader().customContextMenuRequested.connect(self.column_header_popup)
        self.data_area.verticalHeader().setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.data_area.verticalHeader().customContextMenuRequested.connect(self.row_header_popup)
        data_frame_layout.addWidget(self.data_area)
        data_frame.setLayout(data_frame_layout)
        self.main_area.addTab(data_frame, QIcon(MetaWinConstants.data_icon), "Data")
        self.refresh_data()

        # ---output tab---
        output_frame = QFrame()
        output_frame_layout = QHBoxLayout()
        self.output_toolbar = QToolBar()
        self.output_toolbar.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.output_toolbar.addAction(save_output_action)
        self.output_toolbar.addSeparator()
        self.output_toolbar.addAction(output_decimal_action)
        self.output_toolbar.addAction(output_alpha_action)
        self.output_toolbar.addAction(output_font_action)
        output_frame_layout.addWidget(self.output_toolbar)
        self.output_area = QTextEdit()
        output_frame_layout.addWidget(self.output_area)
        output_frame.setLayout(output_frame_layout)
        self.main_area.addTab(output_frame, QIcon(MetaWinConstants.output_icon), get_text("Output"))

        # initial output text
        self.write_output("<h1>MetaWin</h1>")
        self.write_output(MetaWinConstants.mw3_citation)
        self.write_output_block([version_str(),
                                 get_text("Started at ") + datetime.datetime.now().strftime("%B %d, %Y, %I:%M %p")])
        self.output_saved = True  # reset to true upon opening

        # ---graph tab---
        self.graph_area = QFrame()
        graph_master_layout = QHBoxLayout()
        self.graph_layout = QVBoxLayout()
        self.save_graph_action = QAction(QIcon(MetaWinConstants.save_graph_icon), get_text("Save Figure"))
        export_graph_data_action = QAction(QIcon(MetaWinConstants.export_graph_data_icon),
                                           get_text("Export Figure Data"), self)
        export_graph_data_action.triggered.connect(self.export_graph_data)
        edit_graph_action = QAction(QIcon(MetaWinConstants.edit_graph_icon), get_text("Edit Figure"), self)
        edit_graph_action.triggered.connect(self.edit_graph)
        self.graph_toolbar = QToolBar()
        self.graph_toolbar.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.graph_toolbar.addAction(self.save_graph_action)
        self.graph_toolbar.addAction(export_graph_data_action)
        self.graph_toolbar.addAction(edit_graph_action)
        graph_master_layout.addWidget(self.graph_toolbar)
        graph_master_layout.addLayout(self.graph_layout)
        self.graph_area.setLayout(graph_master_layout)
        self.main_area.addTab(self.graph_area, QIcon(MetaWinConstants.graph_icon), get_text("Graph"))

        # ---tree tab---
        tree_frame = QFrame()
        tree_frame_layout = QHBoxLayout()
        self.tree_toolbar = QToolBar()
        self.tree_toolbar.setOrientation(QtCore.Qt.Orientation.Vertical)
        load_tree_action = QAction(QIcon(MetaWinConstants.open_icon), get_text("Load Phylogeny"), self)
        load_tree_action.triggered.connect(self.load_phylogeny)
        self.tree_toolbar.addAction(load_tree_action)
        tree_frame_layout.addWidget(self.tree_toolbar)

        tree_info_layout = QVBoxLayout()
        tree_info_panel = QFrame()
        tree_info_panel_layout = QVBoxLayout()
        self.tree_info_label = QLabel(get_text("No phylogney has been loaded"))
        tree_info_panel_layout.addWidget(self.tree_info_label)
        tree_info_panel.setLayout(tree_info_panel_layout)
        tree_info_layout.addWidget(tree_info_panel)
        self.tree_area = QFrame()
        self.tree_area.setFrameShape(QFrame.Shape.Panel)
        self.tree_area.setFrameShadow(QFrame.Shadow.Sunken)
        self.tree_area.setLineWidth(2)
        tree_area_layout = QVBoxLayout()
        self.tree_area.setLayout(tree_area_layout)
        tree_info_layout.addWidget(self.tree_area, stretch=1)
        tree_frame_layout.addLayout(tree_info_layout)
        tree_frame.setLayout(tree_frame_layout)

        self.main_area.addTab(tree_frame, QIcon(MetaWinConstants.tree_icon), get_text("Phylogeny"))

        self.main_area.setTabVisible(2, False)
        self.main_area.setTabVisible(3, False)

        # general window options
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle("MetaWin")

        if self.auto_update_check:
            self.check_for_update(False)

    def closeEvent(self, event) -> None:
        """
        Check to see if data and output have been saved before closing program
        Save options to configuration file
        """
        do_quit = True
        if not self.output_saved:
            response = MetaWinMessages.query_yes_no_cancel(self,
                                                           get_text("Output has not been saved"),
                                                           get_text("prompt_output_save_quit"))
            if response == MetaWinMessages.MW_YES:
                do_quit = self.save_output()
            elif response == MetaWinMessages.MW_NO:
                do_quit = True
            else:
                do_quit = False

        if do_quit and not self.data_saved:
            response = MetaWinMessages.query_yes_no_cancel(self,
                                                           get_text("Data has not been saved"),
                                                           get_text("prompt_data_save_quit"))
            if response == MetaWinMessages.MW_YES:
                do_quit = self.save_data()
            elif response == MetaWinMessages.MW_NO:
                do_quit = True
            else:
                do_quit = False

        if do_quit:
            MetaWinConfig.export_config(self)
            event.accept()
        else:
            event.ignore()

    def show_calculator(self) -> None:
        self.mc = MetaCalc()
        self.mc.show()

    def show_about(self) -> None:
        self.about = MetaWinAbout()
        self.about.exec()

    def show_help(self) -> None:
        webbrowser.open(self.help)

    def load_data(self) -> None:
        inname = QFileDialog.getOpenFileName(self, get_text("Load Data"))
        if inname[0]:
            new_data, output = MetaWinImport.import_data(self, inname[0])
            if new_data is not None:
                self.data = new_data
                self.refresh_data()
                self.write_multi_output_blocks(output)

    def clear_data(self) -> None:
        """
        Erase any data already loaded into memory, checking whether it has been saved before proceeding
        """
        do_clear = True
        if not self.data_saved:
            response = MetaWinMessages.query_yes_no_cancel(self,
                                                           get_text("Data has not been saved"),
                                                           get_text("prompt_data_save_clear"))
            if response == MetaWinMessages.MW_YES:
                self.save_data()
            elif response == MetaWinMessages.MW_CANCEL:
                do_clear = False
        if do_clear:
            self.data = None
            self.refresh_data()

    def refresh_data(self) -> None:
        """
        Redraw the data table based on the current data in memory and various user specifications such as
        decimal places and colors
        """
        self.data_area.clearContents()
        if self.data is None:
            self.data_area.setRowCount(self.empty_row_num)
            self.data_area.setColumnCount(self.empty_col_num)
            row_headers = ["{} {}".format(get_text("Row"), r+1) for r in range(self.empty_row_num)]
            col_headers = ["{} {}".format(get_text("Column"), c+1) for c in range(self.empty_col_num)]
        else:
            nrows = self.data.nrows()
            ncols = self.data.ncols()
            self.data_area.setRowCount(nrows)
            self.data_area.setColumnCount(ncols)
            row_headers = [row.label for row in self.data.rows]
            col_headers = [col.label for col in self.data.cols]
            for r in range(nrows):
                not_filtered = self.data.rows[r].not_filtered()
                for c, column in enumerate(self.data.cols):
                    dat = self.data.value(r, c)
                    if dat is None:
                        new_item = QTableWidgetItem("")
                    elif dat.is_number():
                        new_item = QTableWidgetItem(format_number(dat.value, decimals=self.data_decimals))
                    else:
                        new_item = QTableWidgetItem(dat.value)
                    if not not_filtered:
                        if dat is None:
                            new_item.setBackground(QColor(self.filtered_row_color))
                        elif str(dat.value) in column.group_filter:
                            new_item.setBackground(QColor(self.filtered_col_color))
                        else:
                            new_item.setBackground(QColor(self.filtered_row_color))

                    new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                    self.data_area.setItem(r, c, new_item)
        self.data_area.setVerticalHeaderLabels(row_headers)
        self.data_area.setHorizontalHeaderLabels(col_headers)

    def calculate_effect_sizes(self) -> None:
        if self.data is not None:
            output, eff_col, var_col = MetaWinEffects.calculate_effect_sizes(self, self.data, self.output_decimals)
            if output is not None:
                self.refresh_data()
                self.write_multi_output_blocks(output)
                self.last_effect = eff_col
                self.last_var = var_col
                self.main_area.setCurrentIndex(1)
                self.data_saved = False
        else:
            MetaWinMessages.report_warning(self, get_text("Warning"), get_text("No data has been loaded."))

    def write_multi_output_blocks(self, output: list) -> None:
        """
        Given a list of lists of strings, write each sublist to the output area as a single block
        """
        for block in output:
            self.write_output_block(block)
        self.write_output("")

    def write_output_block(self, output: list) -> None:
        """
        Add a list of strings to the output area as a single string, separated by the html break
        tag <br>. This adds them to the text edit without extra spacing/blank lines in between them
        """
        self.write_output("<br>".join(output))

    def write_output(self, output: str) -> None:
        """
        Add a string to the output text box, while storing the fact that the output has not been saved.
        """
        self.output_area.append(output)
        self.output_saved = False

    def row_header_popup(self, pos) -> None:
        """
        Context menu for right-clicking on a row header in the data display
        """
        if self.data is not None:
            self.clicked_header = self.data.rows[self.data_area.verticalHeader().logicalIndexAt(pos)]
            filter_action = QAction(get_text("Toggle Row Filter"), self)
            filter_action.triggered.connect(self.toggle_row)
            menu = QMenu()
            menu.addAction(filter_action)
            menu.exec(self.data_area.mapToGlobal(pos))

    def toggle_row(self) -> None:
        self.clicked_header.include_row = not self.clicked_header.include_row
        self.refresh_data()

    def column_header_popup(self, pos) -> None:
        """
        Context menu for right-clicking on a column header in the data display
        """
        if self.data is not None:
            self.clicked_header = self.data.cols[self.data_area.horizontalHeader().logicalIndexAt(pos)]
            filter_action = QAction(get_text("Filter within Column"), self)
            filter_action.triggered.connect(self.filter_by_column)
            menu = QMenu()
            menu.addAction(filter_action)
            menu.exec(self.data_area.mapToGlobal(pos))

    def filter_by_column(self) -> None:
        if self.data is not None:
            if MetaWinFilter.filter_within_column(self, self.data, self.clicked_header):
                self.refresh_data()

    def set_data_decimal_places(self) -> None:
        x, ok_pressed = QInputDialog.getInt(self, get_text("Data Decimals"),
                                            get_text("Number of Decimal Places to Display"),
                                            self.data_decimals, 0, 15, 1)
        if ok_pressed:
            self.data_decimals = x
            self.refresh_data()

    def set_output_decimal_places(self) -> None:
        x, ok_pressed = QInputDialog.getInt(self, get_text("Output Decimals"),
                                            get_text("Number of Decimal Places to Display"),
                                            self.output_decimals, 0, 15, 1)
        if ok_pressed:
            self.output_decimals = x

    def set_alpha_significance(self) -> None:
        alpha, ok_pressed = QInputDialog.getDouble(self, get_text("Significance Level"),
                                                   get_text("sig_alpha_text"), self.alpha, 0.01, 1, 2, step=0.01)
        if ok_pressed:
            self.alpha = alpha

    def show_data_toolbar_click(self) -> None:
        """
        Hide or show data tab toolbar
        """
        if self.show_data_toolbar:
            self.show_data_toolbar = False
            self.data_toolbar_action.setIcon(QIcon(MetaWinConstants.show_toolbar_icon))
            # self.data_toolbar_action.setChecked(False)
            self.data_toolbar_action.setText(get_text("Show Data Toolbar"))
            self.data_toolbar.setVisible(False)
        else:
            self.show_data_toolbar = True
            self.data_toolbar_action.setIcon(QIcon(MetaWinConstants.hide_toolbar_icon))
            # self.data_toolbar_action.setChecked(True)
            self.data_toolbar.setVisible(True)
            self.data_toolbar_action.setText(get_text("Hide Data Toolbar"))

    def show_output_toolbar_click(self) -> None:
        """
        Hide or show output tab toolbar
        """
        if self.show_output_toolbar:
            self.show_output_toolbar = False
            # self.output_toolbar_action.setChecked(False)
            self.output_toolbar_action.setIcon(QIcon(MetaWinConstants.show_toolbar_icon))
            self.output_toolbar.setVisible(False)
            self.output_toolbar_action.setText(get_text("Show Output Toolbar"))
        else:
            self.show_output_toolbar = True
            # self.output_toolbar_action.setChecked(True)
            self.output_toolbar_action.setIcon(QIcon(MetaWinConstants.show_toolbar_icon))
            self.output_toolbar.setVisible(True)
            self.output_toolbar_action.setText(get_text("Hide Output Toolbar"))

    def show_tree_area_action_clicked(self) -> None:
        if self.show_tree_area:
            self.show_tree_area = False
            # self.tree_area_action.setChecked(False)
            self.main_area.setTabVisible(3, False)
            self.tree_area_action.setText(get_text("Show Phylogeny Tab"))
        else:
            self.show_tree_area = True
            # self.tree_area_action.setChecked(True)
            self.main_area.setTabVisible(3, True)
            self.tree_area_action.setText(get_text("Hide Phylogeny Tab"))

    def click_auto_update_check(self) -> None:
        if self.auto_update_check:
            self.auto_update_check = False
            self.auto_update_check_action.setChecked(False)
        else:
            self.auto_update_check = True
            self.auto_update_check_action.setChecked(True)

    def click_save_output(self) -> None:
        self.save_output()

    def save_output(self) -> bool:
        """
        Save the text in the output box. This function will return False if there is a problem saving the
        file or the user cancels the operation through the dialog
        """
        output_format = MetaWinSave.save_output(self)
        if output_format is not None:
            save_name = QFileDialog.getSaveFileName(self, get_text("Save Output"))
            if save_name[0]:
                if output_format == MetaWinConstants.SAVE_HTML:
                    outstr = self.output_area.toHtml()
                elif output_format == MetaWinConstants.SAVE_MD:
                    outstr = self.output_area.toMarkdown()
                else:
                    outstr = self.output_area.toPlainText()
                try:
                    with open(save_name[0], "w") as outfile:
                        outfile.writelines(outstr)
                    self.output_saved = True
                    return True
                except IOError:
                    MetaWinMessages.report_critical(self, get_text("Error writing to file"),
                                                    get_text("Unable to write to ") + save_name)
        return False

    def click_save_data(self) -> None:
        self.save_data()

    def save_data(self) -> bool:
        """
        Save the current data. This function will return False if there is a problem saving the
        file or the user cancels the operation through the dialog
        """
        if self.data is None:
            return True
        else:
            output_format, decimals = MetaWinSave.save_data(self)
            if output_format is not None:
                save_name = QFileDialog.getSaveFileName(self, get_text("Save Data"))
                if save_name[0]:
                    out_list = self.data.export_to_list(output_format, decimals)
                    try:
                        with open(save_name[0], "w") as outfile:
                            outfile.writelines(out_list)
                        self.data_saved = True
                        return True
                    except IOError:
                        MetaWinMessages.report_critical(self, get_text("Error writing to file"),
                                                        get_text("Unable to write to ") + save_name)
        return False

    def meta_analysis(self) -> None:
        if self.data is not None:
            output, figure, fig_caption, chart_data = MetaWinAnalysis.meta_analysis(self, self.data, self.last_effect,
                                                                                    self.last_var, self.output_decimals,
                                                                                    self.alpha, self.phylogeny)
            if output is not None:
                self.write_multi_output_blocks(output)
                self.main_area.setCurrentIndex(1)
                if figure is not None:
                    self.show_figure(figure, fig_caption, chart_data)
        else:
            MetaWinMessages.report_warning(self, get_text("Warning"), get_text("No data has been loaded."))

    def show_figure(self, figure, fig_caption: str, chart_data) -> None:
        """
        Replace the current figure in the graphics tab with a new figure, toolbar, and caption
        """
        self.main_area.setTabVisible(2, True)
        # erase existing figure elements
        for i in reversed(range(self.graph_layout.count())):
            self.graph_layout.itemAt(i).widget().setParent(None)

        # create new figure
        toolbar = NavigationToolbar2QT(figure, None)
        self.save_graph_action.triggered.connect(toolbar.save_figure)
        caption_box = QTextEdit()
        caption_box.setText(fig_caption)
        self.chart_caption = fig_caption
        self.graph_layout.addWidget(figure, stretch=8)
        self.graph_layout.addWidget(caption_box, stretch=1)
        self.chart_data = chart_data

    def load_phylogeny(self) -> None:
        inname = QFileDialog.getOpenFileName(self, get_text("Load Phylogeny"))
        if inname[0]:
            new_tree, output = MetaWinImport.import_phylogeny(self, inname[0])
            if new_tree is not None:
                self.phylogeny = new_tree
                self.tree_info_label.setText(get_text("Phylogeny contains {} tips").format(self.phylogeny.n_tips()))
                self.refresh_tree_panel()
                self.write_multi_output_blocks(output)

    def refresh_tree_panel(self) -> None:
        if self.phylogeny is not None:
            figure = MetaWinCharts.chart_phylogeny(self.phylogeny)
            tree_layout = self.tree_area.layout()
            tree_layout.addWidget(figure)

    def draw_scatter_plot(self) -> None:
        if self.data is not None:
            figure, fig_caption, chart_data = MetaWinDraw.draw_scatter_dialog(self, self.data)
            if figure is not None:
                self.show_figure(figure, fig_caption, chart_data)
                self.main_area.setCurrentIndex(2)

    def draw_histogram(self) -> None:
        if self.data is not None:
            figure, fig_caption, chart_data = MetaWinDraw.draw_histogram_dialog(self, self.data, self.last_effect,
                                                                                self.last_var)
            if figure is not None:
                self.show_figure(figure, fig_caption, chart_data)
                self.main_area.setCurrentIndex(2)

    def draw_normal_quantile_plot(self) -> None:
        if self.data is not None:
            figure, fig_caption, chart_data = MetaWinDraw.draw_normal_quantile_dialog(self, self.data, self.last_effect,
                                                                                      self.last_var)
            if figure is not None:
                self.show_figure(figure, fig_caption, chart_data)
                self.main_area.setCurrentIndex(2)

    def draw_radial_plot(self) -> None:
        if self.data is not None:
            figure, fig_caption, chart_data = MetaWinDraw.draw_radial_dialog(self, self.data, self.last_effect,
                                                                             self.last_var)
            if figure is not None:
                self.show_figure(figure, fig_caption, chart_data)
                self.main_area.setCurrentIndex(2)

    def draw_forest_plot(self) -> None:
        if self.data is not None:
            figure, fig_caption, chart_data = MetaWinDraw.draw_forest_dialog(self, self.data, self.last_effect,
                                                                             self.last_var, self.alpha)
            if figure is not None:
                self.show_figure(figure, fig_caption, chart_data)
                self.main_area.setCurrentIndex(2)

    def clear_filters(self) -> None:
        """
        Erase/clear/reset all data filters
        """
        if self.data is not None:
            for row in self.data.rows:
                row.include_row = True
            for col in self.data.cols:
                col.group_filter = []

            self.refresh_data()

    def set_filter_row_color(self) -> None:
        color = QColorDialog.getColor(initial=QColor(self.filtered_row_color))
        if color.isValid():
            self.filtered_row_color = color
            self.refresh_data()

    def set_filter_col_color(self) -> None:
        color = QColorDialog.getColor(initial=QColor(self.filtered_col_color))
        if color.isValid():
            self.filtered_col_color = color
            self.refresh_data()

    def set_output_font(self) -> None:
        new_font, ok = QFontDialog.getFont(self.output_area.currentFont())
        if ok:
            self.output_area.setFont(new_font)

    def language_clicked(self) -> None:
        # for lang in self.language_actions.actions():
        #     if lang.isChecked():
        #         MetaWinLanguage.current_language = lang.text()
        MetaWinLanguage.current_language = self.language_box.currentText()

    def localization(self) -> None:
        webbrowser.open(self.localization_help)

    def click_check_for_update(self):
        self.check_for_update()

    def check_for_update(self, report_none: bool = True) -> None:
        version_msg = check_version()
        if version_msg is not None:
            msg = version_msg + "\n\n" + get_text("exit_download").format("MetaWin")
            if MetaWinMessages.query_yes_no(self, get_text("Newer Version Available"), msg) == MetaWinMessages.MW_YES:
                webbrowser.open(MetaWinConstants.download_website)
                sys.exit()
        if report_none:
            MetaWinMessages.report_information(self, get_text("No Newer Version Found"),
                                               get_text("You are running the most current version available"))

    def export_graph_data(self):
        """
        Export the current chart data
        """
        save_name = QFileDialog.getSaveFileName(self, get_text("Export Figure Data"))
        if save_name[0]:
            out_list = self.chart_data.export_to_list()
            try:
                with open(save_name[0], "w") as outfile:
                    outfile.writelines(out_list)
            except IOError:
                MetaWinMessages.report_critical(self, get_text("Error writing to file"),
                                                get_text("Unable to write to ") + save_name)

    def edit_graph(self):
        if self.chart_data is not None:
            figure = MetaWinDraw.edit_figure(self, self.chart_data)
            if figure is not None:
                caption = self.chart_caption
                self.show_figure(figure, caption, self.chart_data)
