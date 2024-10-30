from typing import Collection
from htmlspecializer import Specializer
from table import Table
from tag import Tag, TextNode
import html


class TableHTMLMaker:
    def __init__(self, table: "Table", specializers: list[Specializer] | None = None):
        self.table = table
        self.specializers = (
            Specializer.default_speciailizers()
            if specializers is None
            else specializers
        )

    def add_speciailization(self, *specializers: Specializer):
        self.specializers.extend(specializers)

    def get_special_html(self, content):
        for specializer in self.specializers:
            if specializer.matches(content):
                return specializer.parse(content)
        return html.escape(content)

    def html(self):
        table = Tag("table", cellspacing="0", cellpadding="0", Class="tbldis-gen")
        thead = Tag("thead")
        tr = Tag("tr")

        thead.appendChild(tr)
        table.appendChild(thead)

        for item in self.table.headers:
            tr.appendChild(Tag("th", children=[TextNode(item)], Class="tbldis-gen"))

        tbody = Tag("tbody")
        for row in self.table.rows:
            tr = Tag("tr", Class="tbldis-gen")
            for content in row:
                td = Tag(
                    "td",
                    Class="tbldis-gen",
                    children=[TextNode(self.get_special_html(content))],
                )
                tr.appendChild(td)
            tbody.appendChild(tr)

        table.appendChild(tbody)
        return table.html()
