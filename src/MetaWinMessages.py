"""
Module containing functions for eliciting common warning and error messages
"""

from PyQt6.QtWidgets import QMessageBox

MW_YES = 0
MW_NO = 1
MW_CANCEL = 2


def report_critical(sender, title: str, message: str):
    """
    Show critical error message
    """
    QMessageBox.critical(sender, title, message, QMessageBox.StandardButton.Ok)


def report_warning(sender, title: str, message: str):
    """
    Show warning message
    """
    QMessageBox.warning(sender, title, message, QMessageBox.StandardButton.Ok)


def query_yes_no_cancel(sender, title: str, message: str):
    """
    Prompt user with question, with possible responses being Yes, No, or Cancel and report which button
    was chosen
    """
    response = QMessageBox.question(sender, title, message, QMessageBox.StandardButton.Yes |
                                    QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
    if response == QMessageBox.StandardButton.Yes:
        return MW_YES
    elif response == QMessageBox.StandardButton.No:
        return MW_NO
    return MW_CANCEL


def query_yes_no(sender, title: str, message: str):
    """
    Prompt user with question, with possible responses being Yes, No, or Cancel and report which button
    was chosen
    """
    response = QMessageBox.question(sender, title, message, QMessageBox.StandardButton.Yes |
                                    QMessageBox.StandardButton.No)
    if response == QMessageBox.StandardButton.Yes:
        return MW_YES
    return MW_NO


def report_information(sender, title: str, message: str):
    """
    Show informational message
    """
    QMessageBox.information(sender, title, message, QMessageBox.StandardButton.Ok)
