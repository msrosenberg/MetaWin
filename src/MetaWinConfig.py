"""
Import and export of configuration options
"""

import os

from matplotlib.colors import is_color_like

import MetaWinLanguage
import MetaWinCharts

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "metawin.config")


def import_config() -> dict:
    """
    Attempt to import a configuration file if it exists. Return values in file,
    or defaults, as necessary

    invalid configuration options are simply ignored
    """
    config = default_config()
    try:
        with open(CONFIG_FILE, "r") as infile:
            for line in infile:
                try:
                    key, value = line.strip().split("=")
                    key, value = key.strip(), value.strip()
                    value = validate_config(key, value)
                    if value is not None:
                        config[key] = value
                except ValueError:
                    pass
    except IOError:
        pass
    return config


def default_config() -> dict:
    """
    create the default configuration
    """
    return {
        "language": "English",
        "data decimals": 2,
        "output decimals": 4,
        "filtered row color": "lightpink",
        "filtered col color": "red",
        "auto update check": True,
        "alpha": 0.05,
        "confidence interval distribution": "Normal",
        "color name space": "xkcd"
    }


def validate_config(key, value):
    """
    validate whether the imported value is valid for the specified key, including
    conversion from strings when appropriate

    if the value is invalid, return None
    if the key is not recognized, just return the value as is
    """
    if key in ("data decimals", "output decimals"):
        try:
            value = int(value)
            if (value < 0) or (value > 15):
                raise ValueError
            return value
        except ValueError:
            return None
    elif key == "language":
        if value in MetaWinLanguage.language_list():
            return value
        return None
    elif key in ("filtered row color", "filtered col color"):
        if is_color_like(value):
            return value
        return None
    elif key == "auto update check":
        if value.lower() == "true":
            return True
        return False
    elif key == "alpha":
        try:
            value = float(value)
            if (value < 0) or (value > 1):
                raise ValueError
            return value
        except ValueError:
            return None
    elif key == "confidence interval distribution":
        if value == "Students t":
            return value
        return "Normal"
    elif key == "color name space":
        if value == "X11/CSS4":
            return value
        return "xkcd"
    return value


def export_config(main_window) -> None:
    """
    export the current configuration options to the configuration file so they can be
    imported next time the program is executed
    """
    try:
        with open(CONFIG_FILE, "w") as outfile:
            outfile.write("language={}\n".format(MetaWinLanguage.current_language))
            outfile.write("output decimals={:d}\n".format(main_window.output_decimals))
            outfile.write("data decimals={:d}\n".format(main_window.data_decimals))
            outfile.write("filtered row color={}\n".format(main_window.filtered_row_color))
            outfile.write("filtered col color={}\n".format(main_window.filtered_col_color))
            outfile.write("auto update check={}\n".format(main_window.auto_update_check))
            outfile.write("alpha={}\n".format(main_window.alpha))
            outfile.write("confidence interval distribution={}".format(main_window.confidence_interval_dist))
            outfile.write("color name space={}\n".format(MetaWinCharts.color_name_space))
    except IOError:
        pass
