"""
Primary module for entry into MetaWin via the GUI
"""

import sys
from PyQt6.QtWidgets import QApplication
from MetaWinMain import MainWindow
import MetaWinConfig

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        import pyi_splash
        pyi_splash.close()
    except ModuleNotFoundError:
        pass

    config = MetaWinConfig.import_config()
    main_window = MainWindow(config)
    main_window.show()
    sys.exit(app.exec())
