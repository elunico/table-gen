# custom format
# any line matching "^\s*#" is ignored
# Anything matching "#\s*\n" is ignored
# all other lines should begin with a tag name
# then an equal sign with optional whitespace on either side
# then either (1) a comma separated list of tags or (2) an asterisk

import re

comment_line = re.compile(r"^\s*#")
comment_area = re.compile(r"(\b|\s*)#.*?\n?$")
equal_sep = re.compile(r"\s*=\s*")
list_sep = re.compile(r"\s*,\s*")


def loads(s):
    lines = s.split("\n")
    result = {}
    for line in lines:
        if comment_line.match(line):
            continue
        line = comment_area.sub("", line)
        tag, data = equal_sep.split(line)
        if data == "*":
            others = "*"
        else:
            others = list_sep.split(data)
        result[tag] = others
    return result


def load(fp):
    return loads(fp.read())


def dumps(o):
    lines = []
    for tag, valids in o.items():
        if not isinstance(tag, str):
            raise TypeError("Tag must be str not " + str(type(tag)))
        if not isinstance(valids, list) and valids != "*":
            raise TypeError("Values must be '*' or list of str")

        if valids == "*":
            line = f"{tag}=*"
        else:
            line = f'{tag}={", ".join(valids)}'
        lines.append(line)
    return "\n".join(lines)


def dump(obj, fp):
    fp.write(dumps(obj))
