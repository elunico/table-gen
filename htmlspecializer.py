import abc
import uuid
import datetime
from tag import TagGroup, Tag, TextNode
import locale
import typing


class Specializer(abc.ABC):
    @staticmethod
    def default_speciailizers() -> list["Specializer"]:
        return [
            ImgSpecializer(),
            ColorSpecializer(),
            PyDateSpecializer(),
            RandomNumberSpecializer(),
            HTMLDataSpecializer(),
            SelectElementSpecializer(),
        ]

    def __init__(self, keyword: str, indicator="@", delimiter=":"):
        self.keyword = keyword
        self.indicator = indicator
        self.delimiter = delimiter

    @property
    def prefix_string(self) -> str:
        """
        The special tag indicator for this specialization
        """
        return "{}{}{}".format(self.indicator, self.keyword, self.delimiter)

    def matches(self, content: str) -> bool:
        """
        Determine if the cell content matches this specializer. Done by checking the prefix string tag
        """
        return content.startswith(self.prefix_string)

    def extract_data(self, content: str) -> str:
        """
        Return the data of the cell after cutting out the special tag
        """
        return content[len(self.prefix_string) :]

    @abc.abstractmethod
    def raw_parse(self, data: str) -> str:
        """
        Parse the data exactly as given without attempting to extract the prefix
        """

    def parse(self, content: str) -> str:
        """
        Parse the argument in the CSV column, removing the prefix specialization indicator first
        """
        return self.raw_parse(content[len(self.prefix_string) :])


class ColorSpecializer(Specializer):
    def __init__(self, keyword="color", indicator="@", delimiter=":"):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data):
        return self.parse(self.prefix_string + data)

    def parse(self, content):
        u = uuid.uuid4()
        data = self.extract_data(content)

        tooltip = Tag(
            "div",
            children=[TextNode(data)],
            hidden="true",
            id=f"sub-{u}",
            Class="tbldis-gen-tooltop",
        )
        main = Tag(
            "div",
            children=[TextNode("&nbsp;")],
            id=str(u),
            Class="tbldis-gen-color-component",
            style=f"background-color: {data}; width: 45px; height: 45px",
        )

        script_content = """
        p = document.getElementById('{id}');
        p.onmouseenter = (event) => {{
            let q = document.getElementById('sub-{id}')
            q.removeAttribute('hidden')
            q.style.left = `${{event.x + 10}}px`
            q.style.top = `${{event.y - 20}}px`
        }}
        p.onmouseleave = () => {{
            let q = document.getElementById('sub-{id}')
            q.setAttribute('hidden', true)
        }}
        """.format(
            id=str(u)
        )

        script = Tag("script")
        script.appendChild(TextNode(script_content))

        group = TagGroup(tooltip, main, script)

        return group.html()


class ImgSpecializer(Specializer):
    def __init__(self, keyword="img", indicator="@", delimiter=":"):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data):
        if "$$" in data:
            url, dimensions = data.split("$$")
            if "x" in dimensions:
                w, h = dimensions.split("x")
            else:
                w = dimensions
                h = None
        else:
            url = data
            w, h = None, None

        attrs = {"src": url}
        if w:
            attrs["width"] = w
        if h:
            attrs["height"] = h

        return Tag("img", children=[], self_closing=True, **attrs).html()


class PyDateSpecializer(Specializer):
    def __init__(self, keyword: str = "pydate", indicator="@", delimiter=""):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> str:
        d = datetime.datetime.now()
        return d.strftime("%A, %B %d, %Y")


class RandomNumberSpecializer(Specializer):
    def __init__(self, keyword: str = "rand", indicator="@", delimiter=""):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> str:
        u = uuid.uuid4()
        div = Tag("div", Class="tbldis-gen", id=f"{u}")
        script = Tag(
            "script",
            children=[
                TextNode(
                    f"element = document.getElementById('{u}');\n"
                    "element.textContent = Math.random().toFixed(4);"
                )
            ],
        )

        return TagGroup(div, script).html()


class HTMLDataSpecializer(Specializer):
    def __init__(self, keyword: str = "html", indicator="@", delimiter=":"):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> str:
        return data  # no html.escape()


class SelectElementSpecializer(Specializer):
    def __init__(
        self,
        keyword: str = "select",
        indicator="@",
        delimiter=":",
        support_srcs: list[str] | None = None,
        support_scripts: list[str] | None = None,
    ):
        super().__init__(keyword, indicator, delimiter)
        self.support_srcs: list[str] = support_srcs or list()
        self.support_scripts: list[str] = support_scripts or list()

    def raw_parse(self, data: str) -> str:
        if "$$" in data:
            data, src = data.split("$$")
            self.support_srcs.append(src)

        options = ((i, i) if "=" not in i else (i.split("=")) for i in data.split(";"))

        i = uuid.uuid4()

        div = Tag("div", id=f"{i}-holder", Class="tbldis-gen-select-holder")
        select = Tag("select", id=f"{i}-select")
        for value, text in options:
            option = Tag("option", value=value, children=[TextNode(text)])
            select.appendChild(option)

        div.appendChild(select)

        group = TagGroup(div)

        if self.support_srcs:
            for src in self.support_srcs:
                group.appendChild(Tag("script", src=src))

        if self.support_scripts:
            for script in self.support_scripts:
                group.appendChild(Tag("script", children=[TextNode(script)]))

        return group.html()


class SimpleSpecializer(Specializer):
    def __init__(self, keyword: str, parser: typing.Callable[[str], str]):
        super().__init__(keyword)
        self.parser = parser

    def raw_parse(self, data: str) -> str:
        return self.parser(data)
