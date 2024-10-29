# custom format
# any line matching "^\s*#" is ignored
# Anything matching "#\s*\n" is ignored
# all other lines should begin with a tag name
# then an equal sign with optional whitespace on either side
# then either (1) a comma separated list of tags or (2) an asterisk

import re
import typing

comment_line = re.compile(r"^\s*#")
comment_area = re.compile(r"(\b|\s*)#.*?\n?$")
equal_sep = re.compile(r"\s*=\s*")
list_sep = re.compile(r"\s*,\s*")


def _load_line(line: str) -> tuple[str, list[str] | str] | None:
    line = line.strip()
    if not line:
        return None
    if comment_line.match(line):
        return None
    line = comment_area.sub("", line)
    tag, data = equal_sep.split(line)
    if data == "*":
        others = "*"
    else:
        others = list_sep.split(data)
    return tag, others


def loads(s: str) -> dict[str, str | list[str]]:
    lines = s.split("\n")
    return load(lines)


def load(fp: typing.Iterable[str]) -> dict[str, str | list[str]]:
    result = {}
    for line in fp:
        parsed = _load_line(line)
        if parsed is not None:
            tag, others = parsed
            result[tag] = others
    return result


def _dump_line(tag: str, valids: list[str] | str):
    if not isinstance(tag, str):
        raise TypeError("Tag must be str not " + str(type(tag)))
    if not isinstance(valids, list) and valids != "*":
        raise TypeError("Values must be '*' or list of str")

    if valids == "*":
        line = f"{tag}=*"
    else:
        line = f'{tag}={", ".join(valids)}'
    return line


class Writeable(typing.Protocol):
    def write(self, content: str):
        ...


class _ListFile:
    def __init__(self):
        self.lines: list[str] = []

    def write(self, content: str):
        self.lines.append(content)

    def str(self) -> str:
        return "".join(self.lines)


def dumps(o: dict[str, list[str] | str]) -> str:
    lines = []
    f = _ListFile()
    dump(o, f)
    return f.str()


def dump(obj: dict[str, str | list[str]], fp: Writeable):
    for tag, valids in obj.items():
        line = _dump_line(tag, valids)
        fp.write(line)
        fp.write("\n")
