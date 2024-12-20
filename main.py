import argparse
import csv
import uuid
from htmlspecializer import Specializer
from table import Table
from htmltable import TableHTMLMaker

import base64

from tag import Tag, TagGroup, TextNode


class Base64DataSpecializer(Specializer):
    def __init__(self, keyword: str = "base64", indicator="@", delimiter=":"):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> Tag:
        return TextNode(str(base64.b64decode(data), encoding="utf-8"))


def fill_template(content):
    with open("support/template.html") as f:
        template = f.read()

    with open("support/style.css") as g:
        style = g.read()

    template = template.replace("%{{ stylesheet }}", style)
    template = template.replace("%{{ table-content }}", content)

    return template


def make_partial(content):
    with open("support/style.css") as g:
        style = g.read()

    style = Tag("style", children=[TextNode(style)])
    div = Tag(
        "div",
        id="tbldis-gen-holder",
        Class="tbldis-gen-holder",
        children=[TextNode(content)],
    )

    return TagGroup(style, div).html()


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", help="input CSV file for translating")
    ap.add_argument(
        "-o",
        "--output",
        help="Filename to output HTML to. If not specified, print to stdout",
    )
    ap.add_argument(
        "-p",
        "--partial",
        action="store_true",
        help="Output only the Table HTML with styling for insertion into an existing HTML document",
    )
    return ap.parse_args()


def main():
    args = parse_args()

    with open(args.input) as f:
        data = csv.reader(f)
        f = Table.from_csv_reader(data)

    htmler = TableHTMLMaker(f)
    htmler.add_speciailization(Base64DataSpecializer())

    tree = htmler.render()

    if args.partial:
        if args.output:
            with open(args.output + "-partial", "w") as g:
                g.write(make_partial(tree.html()))
        else:
            print(make_partial(tree.html()))
    else:
        content = fill_template(tree.html())
        if args.output:
            with open(args.output, "w") as g:
                g.write(content)
        else:
            print(content)


if __name__ == "__main__":
    main()
