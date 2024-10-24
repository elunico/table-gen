import typing
from htmlspecializer import ColorSpecializer


def quote_wrap(s):
    if "," in s:
        if '"' in s:
            s = s.replace('"', '\\"')
        return '"{}"'.format(s)
    return s


def color_column_transform(arg):
    ColorSpecializer().raw_parse(arg)


class TableColumn:
    @classmethod
    def named(cls, name: str):
        return cls(name)

    def __init__(self, name: str):
        self.name = name

    def matches(self, column_name: str) -> bool:
        return self.name == column_name

    def __str__(self) -> str:
        return "Column[{}]".format(self.name)

    def __repr__(self) -> str:
        return "TableColumn({!r})".format(self.name)


class TableRow:
    def __init__(self, data: list[str], owner: "Table"):
        # self.headers = list(data.keys())
        self.content = data
        self.owner = owner

    def __iter__(self):
        return iter(self.content)

    def __getitem__(self, col_name):
        try:
            return self.content[self.owner.headers.index(col_name)]
        except IndexError as e:
            raise KeyError(f"No such header {col_name}") from e

    def __len__(self):
        return len(self.content)

    def __repr__(self):
        return ",".join(quote_wrap(i) for i in self.content)
