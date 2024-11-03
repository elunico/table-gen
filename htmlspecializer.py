import abc
import uuid
import datetime
from tag import TagGroup, Tag, TextNode
import typing


class Specializer(abc.ABC):
    """
    Accepts text data and returns a DOM tree rooted at a single Tag instance
    which is a Python representation of the HTML which will be output into the
    HTML table when using TableHTMLMaker
    """

    @staticmethod
    def default_speciailizers() -> list["Specializer"]:
        return [
            ImgSpecializer(),
            ColorSpecializer(),
            PyDateSpecializer(),
            JSDateSpecializer(),
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
    def raw_parse(self, data: str) -> Tag:
        """
        Parse the data exactly as given without attempting to extract the prefix
        """

    def parse(self, content: str) -> Tag:
        """
        Parse the argument in the CSV column, content is only the content after the prefix tag
        """
        return self.raw_parse(content[len(self.prefix_string) :])


class ColorSpecializer(Specializer):
    """
    Accepts @color: tags and returns a blank div with that background color as well as a
    tooltip that shows the color on mouse hover
    """

    def __init__(
        self, keyword="color", indicator="@", delimiter=":", show_tooltip: bool = True
    ):
        super().__init__(keyword, indicator, delimiter)
        self.show_tooltip = show_tooltip

    def raw_parse(self, data: str) -> Tag:
        return self.parse(self.prefix_string + data)

    def render_main(self, uuid: uuid.UUID, data: str) -> Tag:
        return Tag(
            "div",
            children=[TextNode("&nbsp;")],
            id=str(uuid),
            Class="tbldis-gen-color-component",
            style=f"background-color: {data}; width: 45px; height: 45px",
        )

    def render_tooltip(self, uuid: uuid.UUID, data: str) -> Tag:
        tooltip = Tag(
            "div",
            children=[TextNode(data)],
            hidden="true",
            id=f"sub-{uuid}",
            Class="tbldis-gen-tooltop",
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
            id=str(uuid)
        )
        script = Tag("script")
        script.appendChild(TextNode(script_content))
        return Tag("span", children=[tooltip, script])

    def parse(self, content: str) -> Tag:
        u = uuid.uuid4()
        data = self.extract_data(content)

        if not self.show_tooltip:
            return TagGroup(self.render_main(u, data))
        else:
            return TagGroup(self.render_main(u, data), self.render_tooltip(u, data))


class ImgSpecializer(Specializer):
    """
    @img: tag specializer. Puts an <img> element with the src given after the tag
    """

    def __init__(self, keyword="img", indicator="@", delimiter=":"):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> Tag:
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

        return Tag("img", children=[], self_closing=True, **attrs)


class PyDateSpecializer(Specializer):
    """
    Renders today in the table cell. Today being the day of render not the day of loading the webpage.
    To get the date of the page load see JSDateSpecializer
    """

    def __init__(self, keyword: str = "pydate", indicator="@", delimiter=""):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> Tag:
        d = datetime.datetime.now()
        return TextNode(d.strftime("%A, %B %d, %Y"))


class JSDateSpecializer(Specializer):
    """
    Renders today in the table cell. Today being the day of the page load
    """

    def __init__(self, keyword: str = "jsdate", indicator="@", delimiter=""):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> Tag:
        u = uuid.uuid4()
        print(u)
        div = Tag("div", id=f"{u}", Class="tbldis-gen")
        s = Tag("script")

        text = f"""
        document.getElementById('{u}').textContent = (new Date()).toLocaleDateString();
        """

        s.appendChild(TextNode(text))
        return TagGroup(div, s)


class RandomNumberSpecializer(Specializer):
    """
    Puts a random number in the table cell on each load using JavaScript
    """

    def __init__(self, keyword: str = "rand", indicator="@", delimiter=""):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> Tag:
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

        return TagGroup(div, script)


class HTMLDataSpecializer(Specializer):
    """
    Turns off santization so the CSV content is directly input into the table cell
    """

    def __init__(self, keyword: str = "html", indicator="@", delimiter=":"):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> Tag:
        return TextNode(data)  # no html.escape()


class SelectElementSpecializer(Specializer):
    """
    Creates a select element in the table cell with corresponding options.
    Optionally accepting JavaScript sources to take action when the select is interacted with
    """

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

    def raw_parse(self, data: str) -> Tag:
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

        return group


class SimpleSpecializer(Specializer):
    """
    Can be used for simple specializer use cases without having to create a new subclass
    """

    def __init__(self, keyword: str, parser: typing.Callable[[str], Tag]):
        super().__init__(keyword)
        self.parser = parser

    def raw_parse(self, data: str) -> Tag:
        return self.parser(data)
