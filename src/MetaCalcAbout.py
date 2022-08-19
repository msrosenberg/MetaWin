from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QDialog
from PyQt6.QtGui import QIcon
import MetaWinConstants
from MetaWinWidgets import add_ok_button


class MetaCalcAbout(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        ok_button = add_ok_button(self)
        title_label = QLabel("<span style=\"font-size:20px; font-weight: bold;\">MetaWin</span>")
        subtitle_label = QLabel("<span style=\"font-size:14px; font-weight: bold;\">Statistical Calculator</span>")
        author_label = QLabel("Michael S. Rosenberg")
        version_text = "{}.{}.{}".format(MetaWinConstants.MAJOR_VERSION, MetaWinConstants.MINOR_VERSION,
                                         MetaWinConstants.PATCH_VERSION)
        version_label = QLabel(version_text)
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(version_label)
        layout.addStretch(1)
        layout.addWidget(author_label)
        layout.addStretch(1)
        blayout = QHBoxLayout()
        blayout.addStretch(1)
        blayout.addWidget(ok_button)
        layout.addLayout(blayout)
        self.setLayout(layout)
        self.setFixedSize(300, 150)
        self.setWindowIcon(QIcon(MetaWinConstants.calculator_icon))
        self.setWindowTitle("About Statistical Calculator")
