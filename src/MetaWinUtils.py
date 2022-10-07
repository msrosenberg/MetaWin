"""
Module with a number of general utility functions
"""

from typing import Optional, Union
import re
import urllib.request
import math

import scipy.stats

import MetaWinConstants
from MetaWinLanguage import get_text


def inline_float(decimal_places: int) -> str:
    """
    format a floating-point number displayed within inline text with the desired number of decimal places
    """
    return "0.{}f".format(decimal_places)


def format_number(number, width: int = 0, decimals: int = 2) -> str:
    """
    optimally format a number

    if the number is an integer, format it as such, otherwise, format it as a floating point number
    """
    if isinstance(number, int):
        return format(number, "{}d".format(width))
    else:
        return format(number, "{}.{}f".format(width, decimals))


def interval_to_str(lower_value, upper_value, decimal_places: int = 4) -> str:
    """
    return a string representing an interval, formatting both the start and end values as inline
    floating point numbers
    """
    return format(lower_value, inline_float(decimal_places)) + " to " + \
           format(upper_value, inline_float(decimal_places))


def strip_html(x: str) -> str:
    """
    remove any stray html tags from within string
    """
    regex = r"<.+?>"
    return re.sub(regex, "", x)


def create_output_table(output_text: list, table_data: list, col_headers: list, col_formats: list,
                        out_dec: int = 2, sbc: int = 3, error_row: Optional[list] = None, error_msg: str = "",
                        line_after: Optional[list] = None) -> None:
    """
    Create a well-formatted set of strings representing an output table, including headers and computationally
    determined spacing of columns. The table is added to a list provided as input so can be inserted into a
    broader set of output strings.

    :param output_text: a list where the output will be appended; it can be empty or contain strings, but must
                        already have been instantiated
    :param table_data: a list of lists containing the data to appear in the table; each sublist represents a row
                       of the table and must contain the same number of columns
    :param col_headers: a list containing strings representing headers for each column in the table
    :param col_formats: a list containing basic string formatting codes, generally expected to be "f" of "d"
    :param out_dec: the number of decimal places to output floating point numbers in the table
    :param sbc: the number of spaces to use between each column in the table
    :param error_row: a boolean list designating if a particular row had generated an error in calculations
    :param error_msg: output message if data is missing from row
    :param line_after: add an extra line of hyphens after each row number in the list, if present
    """
    # determine maximum width for each column
    max_width = [len(strip_html(h)) for h in col_headers]
    for row in table_data:
        for i, x in enumerate(row):
            if col_formats[i] == "f":
                frmt = "0.{}f".format(out_dec)
            else:
                frmt = col_formats[i]
            if x is not None:
                max_width[i] = max(max_width[i], len(format(x, frmt)))

    col_spacer = " "*sbc

    # create table header
    for i, h in enumerate(col_headers):
        """
        html tags mess up the automatic centering, so when they exist, manually add spaces on either end of the
        header to account for this
        """
        if len(h) > len(strip_html(h)):
            e = max_width[i] - len(strip_html(h))
            ladj, radj = math.floor(e/2), math.ceil(e/2)
            col_headers[i] = " " * ladj + h + " " * radj
    cols = [format(h, "^{}".format(max_width[i])) for i, h in enumerate(col_headers)]
    header = col_spacer.join(cols)
    output_text.append(header)
    header_line_width = sum(max_width) + (len(cols)-1)*sbc
    output_text.append("-"*header_line_width)

    # create table data template
    cols = []
    total_width = 0
    for i, f in enumerate(col_formats):
        if i == 0:
            j = "<"  # left justify first column
        else:
            j = ">"
        if f == "f":
            frmt = "{{:{}{}.{}f}}".format(j, max_width[i], out_dec)
        else:
            frmt = "{{:{}{}{}}}".format(j, max_width[i], f)
        total_width += max_width[i]
        cols.append(frmt)
    template = col_spacer.join(cols)
    total_width += (len(col_formats) - 1) * sbc
    col_2_to_n_width = total_width - sbc - max_width[0]

    # create table data
    if error_row is None:
        error_row = [False for _ in table_data]
    for r, row in enumerate(table_data):
        if error_row[r]:
            output_text.append(format(row[0], ">{}".format(max_width[0])) + col_spacer +
                               format(error_msg, "^{}".format(col_2_to_n_width)))
        else:
            output_text.append(template.format(*row))
        if line_after is not None:
            if r in line_after:
                output_text.append("-"*header_line_width)

    # add format strings
    output_text[0] = "<code><pre>" + output_text[0]
    output_text[len(output_text)-1] = output_text[len(output_text)-1] + "</pre></code>"


def get_citation(ref: str) -> str:
    """
    Retrieve the citation for a reference based on the internal cite key
    """
    return MetaWinConstants.references[ref][1]


def get_reference(cite: str) -> str:
    """
    Retrieve the full formatted reference based on the internal cite key
    """
    return MetaWinConstants.references[cite][0]


def create_reference_list(citations: list, as_string: bool = False) -> Union[str, list]:
    """
    Return a list of formatted references based on the input citations, including a header

    The default is to return this as a list of strings, but optionally it can be returned as a
    single string with the references embedded as an unordered html list
    """
    sorted_cites = sorted(set(citations))
    refs = [get_reference(x) for x in sorted_cites]
    if as_string:
        return "<h4>{}</h4><ul><li>{}</li></ul>".format(get_text("References"), "</li><li>".join(refs))
    else:
        output = [["<h4>{}</h4>".format(get_text("References"))]]
        for r in refs:
            output.append([r])
        return output


def exponential_label(name: str) -> str:
    """
    adjust label if exponentiating a value

    if label starts with "ln " remove this, otherwise embed label within "exp()"
    """
    if name.startswith("ln "):
        return name[3:]
    else:
        return "exp(" + name + ")"


def prob_z_score(z: float) -> float:
    """
    this function returns the two-tailed probability of a z-score (normal distribution)
    """
    p = scipy.stats.norm.cdf(abs(z))
    return (1-p)*2


def get_webpage(url: str, encoding: str = "utf-8") -> list:
    """
    function to fetch the webpage specified by url and  return a list containing the contents of the page
    """
    webpage = urllib.request.urlopen(url)
    page = webpage.read()
    page = page.decode(encoding)
    lines = page.split("\n")
    return lines


def check_version() -> Optional[str]:
    """
    check metawin website to see if a new version of the software exists

    if a newer version exists, return a message stating the current and newer versions, if not return None
    """
    encoding = "utf-8"
    url = "https://www.metawinsoft.com/current_release_version.txt"
    newer_version = False
    try:
        page = get_webpage(url, encoding)
        major, minor, patch, label = page[0].strip().split(".")
        major, minor, patch = int(major), int(minor), int(patch)
        if major > MetaWinConstants.MAJOR_VERSION:
            newer_version = True
        elif (major == MetaWinConstants.MAJOR_VERSION) and (minor > MetaWinConstants.MINOR_VERSION):
            newer_version = True
        elif (major == MetaWinConstants.MAJOR_VERSION) and (minor == MetaWinConstants.MINOR_VERSION) and \
                (patch > MetaWinConstants.PATCH_VERSION):
            newer_version = True
        if newer_version:
            msg = get_text("Currently running") + " " + version_str() + "\n\n" + \
                  get_text("Version") + " {}.{}.{}".format(major, minor, patch)
            if label.strip() != "":
                msg += " " + label
            msg += " " + get_text("available")
            return msg
    except:
        pass
    return None


def version_str() -> str:
    """
    standardized text for reporting metawin version
    """
    return "{} {}.{}.{} beta".format(get_text("Version"), MetaWinConstants.MAJOR_VERSION,
                                     MetaWinConstants.MINOR_VERSION, MetaWinConstants.PATCH_VERSION)
