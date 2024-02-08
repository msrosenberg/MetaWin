"""
Module containing the About MetaWin dialog class
"""

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QFrame, QGridLayout
from PyQt6.QtGui import QIcon, QPixmap

import MetaWinConstants
from MetaWinUtils import version_str
from MetaWinWidgets import add_ok_button
from MetaWinLanguage import get_text


class MetaWinAbout(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        ok_button = add_ok_button(self)
        version_label = QLabel(version_str())
        citation_label = QLabel(MetaWinConstants.mw3_citation)
        citation_label.setWordWrap(True)
        citation_label.setOpenExternalLinks(True)
        website_label = QLabel("<a href=\"{0}\">{0}</a>".format(MetaWinConstants.website))
        website_label.setOpenExternalLinks(True)

        splash_frame = QFrame()
        splash_frame.setFrameShape(QFrame.Shape.Panel)
        splash_frame.setFrameShadow(QFrame.Shadow.Raised)
        splash_frame.setLineWidth(1)
        splash_layout = QGridLayout()
        splash_frame.setLayout(splash_layout)
        splash_pix = QPixmap(MetaWinConstants.metawin_splash)
        splash_label = QLabel()
        splash_label.setPixmap(splash_pix)
        splash_label.resize(splash_pix.width(), splash_pix.height())
        splash_layout.addWidget(splash_label, 0, 0, 4, 4)

        splash_layout.addWidget(version_label, 3, 3)

        bottom_frame = QFrame()
        bottom_layout = QGridLayout()
        bottom_layout.setColumnStretch(0, 1)
        bottom_layout.setColumnStretch(1, 1)
        bottom_layout.setColumnStretch(2, 1)
        bottom_layout.setColumnStretch(3, 1)
        bottom_frame.setLayout(bottom_layout)
        bottom_layout.addWidget(ok_button, 1, 0)
        bottom_layout.addWidget(website_label, 0, 2)
        bottom_layout.addWidget(citation_label, 1, 2, 1, 2)
        self.setFixedSize(684, 424)

        main_layout = QVBoxLayout()
        main_layout.addWidget(splash_frame)
        main_layout.addWidget(bottom_frame)
        self.setLayout(main_layout)
        self.setWindowIcon(QIcon(MetaWinConstants.metawin_icon))
        self.setWindowTitle(get_text("About MetaWin"))
