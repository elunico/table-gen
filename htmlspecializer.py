import abc
import uuid
import datetime
from tag import TagGroup, Tag, TextNode
import locale


class Specializer(abc.ABC):
    @staticmethod
    def default_speciailizers() -> list["Specializer"]:
        return [
            ImgSpecializer(),
            ColorSpecializer(),
            PyDateSpecializer(),
            RandomNumberSpecializer(),
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
            content=[TextNode(data)],
            hidden="true",
            id=f"sub-{u}",
            Class="tbldis-gen-tooltop",
        )
        main = Tag(
            "div",
            content=[TextNode("&nbsp;")],
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

        # return """<div class="tbldis-gen-tooltop" hidden id='sub-{id}'>{raw_content}</div>
        # </div>
        # <div id={id} class="tbldis-gen-color-component" style="background-color: {color}; width: 45px;height: 45px">
        # &nbsp;

        # <script>
        # p = document.getElementById('{id}');
        # p.onmouseenter = (event) => {{
        #     let q = document.getElementById('sub-{id}')
        #     q.removeAttribute('hidden')
        #     q.style.left = `${{event.x + 10}}px`
        #     q.style.top = `${{event.y - 20}}px`
        # }}
        # p.onmouseleave = () => {{
        #     let q = document.getElementById('sub-{id}')
        #     q.setAttribute('hidden', true)
        # }}
        # </script>
        # """.format(
        #     id=u,
        #     raw_content=self.extract_data(content),
        #     color=self.extract_data(content),
        # )


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

        if w and h:
            return """<img src="{}" width={} height={} />""".format(url, w, h)
        if w:
            return """<img src="{}" width={}  />""".format(url, w)
        if h:
            return """<img src="{}" height={} />""".format(url, h)

        return """<img src="{}" />""".format(url)


class PyDateSpecializer(Specializer):
    def __init__(self, keyword: str = "pydate", indicator="@", delimiter=":"):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> str:
        month, day, year = (int(i) for i in data.split("-"))
        d = datetime.date(year, month, day)
        return d.strftime("%A, %B %d, %Y")


class RandomNumberSpecializer(Specializer):
    def __init__(self, keyword: str = "rand", indicator="@", delimiter=""):
        super().__init__(keyword, indicator, delimiter)

    def raw_parse(self, data: str) -> str:
        u = uuid.uuid4()
        return """
        <div class="tbldis-gen" id='{id}'></div>
        <script>
            element = document.getElementById('{id}');
            element.textContent = Math.random().toFixed(4);
        </script>
        """.format(
            id=u
        )
