"""
Module describing the data container
"""

from typing import Tuple, Optional, Union

from MetaWinUtils import format_number
from MetaWinConstants import VALUE_STRING, VALUE_NUMBER


class MetaWinValue:
    def __init__(self, r=None, c=None, v=None):
        self.value = v
        self.row = r
        self.col = c

    def position(self) -> Tuple[int, int]:
        return self.row.position(), self.col.position()

    def row_number(self) -> int:
        return self.row.position()

    def col_number(self) -> int:
        return self.col.position()

    def is_none(self) -> bool:
        return self.value is None

    def is_number(self) -> bool:
        try:
            float(self.value)
            return True
        except ValueError:
            return False


class MetaWinCol:
    def __init__(self):
        self.label = ""
        self.values = []
        self.data = None
        self.effect_size = None  # effect size function used to create this column, if any
        self.effect_var = None  # column with matching variance if this column contains an effect size
        self.group_filter = []

    def position(self) -> int:
        return self.data.col_number(self)

    def log_transformed(self) -> bool:
        if self.effect_size is None:
            return False
        else:
            return self.effect_size.log_transformed

    def z_transformed(self) -> bool:
        if self.effect_size is None:
            return False
        else:
            return self.effect_size.z_transformed


class MetaWinRow:
    def __init__(self):
        self.label = ""
        self.values = []
        self.data = None
        self.include_row = True

    def position(self) -> int:
        return self.data.row_number(self)

    def not_filtered(self) -> bool:
        if not self.include_row:
            return False
        for c, col in enumerate(self.data.cols):
            d = self.data.value(self.position(), c)
            if d is not None:
                d = d.value
            if str(d) in col.group_filter:
                return False
        return True


class MetaWinData:
    def __init__(self):
        self.rows = []
        self.cols = []
        self.data = {}

    def nrows(self) -> int:
        return len(self.rows)

    def ncols(self) -> int:
        return len(self.cols)

    def add_row(self, label=None) -> MetaWinRow:
        new_row = MetaWinRow()
        new_row.data = self
        self.rows.append(new_row)
        if label is None:
            new_row.label = "Row {}".format(self.nrows())
        else:
            new_row.label = label
        return new_row

    def add_col(self, label=None) -> MetaWinCol:
        new_col = MetaWinCol()
        new_col.data = self
        self.cols.append(new_col)
        if label is None:
            new_col.label = "Column {}".format(self.ncols())
        else:
            new_col.label = label
        return new_col

    def row_number(self, row: MetaWinRow) -> int:
        return self.rows.index(row)

    def col_number(self, col: MetaWinCol) -> int:
        return self.cols.index(col)

    def value(self, r: int, c: int) -> Optional[MetaWinValue]:
        return self.data.get((self.rows[r], self.cols[c]), None)

    def check_value(self, r: int, c: int, value_type: int = VALUE_NUMBER):
        x = self.value(r, c)
        if x is not None:
            if value_type == VALUE_NUMBER:
                if x.is_number():
                    return x.value
            elif value_type == VALUE_STRING:
                return str(x.value)
            else:
                return x.value
        return None

    def add_value(self, r: int, c: int, v: Union[int, float, str]) -> MetaWinValue:
        row = self.rows[r]
        col = self.cols[c]
        new_value = MetaWinValue(row, col, v)
        row.values.append(new_value)
        col.values.append(new_value)
        self.data[row, col] = new_value
        return new_value

    def delete_value(self, r: int, c: int) -> None:
        value = self.value(r, c)
        if value is not None:
            value.row.values.remove(value)
            value.col.values.remove(value)
            self.data.pop((value.row, value.col))

    def replace_value(self, r: int, c: int, v: Union[int, float, str]) -> MetaWinValue:
        self.delete_value(r, c)
        return self.add_value(r, c, v)

    def export_to_list(self, separator: str = "\t", decimals: int = 4) -> list:
        headers = [""]
        headers.extend([c.label for c in self.cols])
        output = [separator.join(headers) + "\n"]
        for r, row in enumerate(self.rows):
            row_out = [row.label]
            for c in range(self.ncols()):
                d = self.value(r, c)
                if d is None:
                    row_out.append("")
                elif d.is_number():
                    row_out.append(format_number(d.value, decimals=decimals))
                else:
                    row_out.append(d.value)
            output.append(separator.join(row_out) + "\n")
        return output

    def column_labels(self) -> list:
        return [c.label for c in self.cols]
