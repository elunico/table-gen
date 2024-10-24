import csv
import typing
from tablerow import TableRow, quote_wrap, TableColumn
import collections

Headers: typing.TypeAlias = collections.OrderedDict[str, TableColumn]


class Table:
    def __init__(self, headers: Headers):
        self.headers: Headers = collections.OrderedDict()
        for key, col in headers.items():
            self.headers[key] = col

        self.rows: list[TableRow] = []

    def __len__(self):
        return len(self.rows)

    def __str__(self):
        longest_len = 0
        for row in self.rows:
            for entry in row:
                if len(entry) > longest_len:
                    longest_len = len(entry)

        if longest_len > 40:
            longest_len = 0

        content = [",".join(quote_wrap(i).rjust(longest_len) for i in self.headers)]
        for row in self.rows:
            row_str = ""
            for entry in row:
                row_str = ",".join(quote_wrap(i).rjust(longest_len) for i in row)
            content.append(row_str)

        return "\n".join(content)

    def save_filename(self, filename):
        with open(filename, "w") as g:
            self.save_file(g)

    def save_file(self, f):
        f.write(str(self))

    @classmethod
    def from_filename(cls, filename):
        with open(filename) as f:
            data = csv.reader(f)
            return cls.from_csv_reader(data)

    @classmethod
    def from_csv_reader(
        cls, reader, with_headers=True, missing_value: str | None = None
    ):
        if with_headers:
            headers: Headers | None = collections.OrderedDict(
                (i, TableColumn.named(i)) for i in next(reader)
            )
        else:
            headers = None

        # add all headers - if no headers, deal with that later
        ret_val = cls(typing.cast(Headers, headers))  # trust me, bro
        # add all rows
        for row in reader:
            tr = TableRow(row, ret_val)
            ret_val.add_tablerow(tr)

        # missing check
        rows = iter(ret_val.rows)
        first = next(rows)

        # fill in missing cells if requested, otherwise raise an error
        for other in rows:
            if len(other) != len(first):
                if missing_value is not None:
                    while len(other) < len(first):
                        other.content.append(missing_value)
                    while len(first) < len(other):
                        first.content.append(missing_value)
                else:
                    raise ValueError(
                        f"Row value length mismatch {other} has {len(other)} values but expected {len(first)}"
                    )

        # if the headers were not provided, we will fill them in generically
        if ret_val.headers is None:
            ret_val.headers = collections.OrderedDict(
                [(str(i), TableColumn(str(i))) for i in range(len(first))]
            )

        return ret_val

    def __getitem__(self, index: int | str) -> TableRow | list[str]:
        if type(index) is int:
            return self.rows[index]
        elif type(index) is str:
            return [i[index] for i in self.rows]
        else:
            raise TypeError(f"Type {type(index)} is not a valid subscript of Table")

    def add_tablerow(self, row: TableRow):
        self.rows.append(row)

    def add_row_ordered(self, *values: str):
        """
        attempts to add a new row to the table from the values given. The values are added to columns in the
        order that they appear. There is no order inpedence, for that feature see Table.add_row
        If the length does not match the number of headers in the table, an error is raised and the table
        is unchanged
        """
        if len(values) != len(self.headers):
            raise ValueError(
                f"Table expected {len(self.headers)} values in each row but got {len(values)}"
            )

        self.add_tablerow(TableRow(list(values), self))

    def add_row(self, **values: str):
        """
        Attempts to add a new row to the table. **values is used to provide data values for each header
        If headers are not accounted for in values or if values contains keys that are not the names of
        columns, an error is raised and the Table is unchanged
        """
        content = []
        headers = list(self.headers.keys())[::-1]
        while headers:
            header = headers.pop()
            try:
                arg = str(values[header])
                content.append(arg)
                del values[header]
            except KeyError:
                raise ValueError(f"Missing value for header {header}") from None
        if len(values) != 0:
            raise ValueError(
                f"Error table does not have headers: {list(values.keys())}"
            )
        self.add_tablerow(TableRow(content, self))

    def insert_row(self, index: int, row: TableRow):
        self.rows.insert(index, row)

    def remove_row_at(self, index: int):
        del self.rows[index]
