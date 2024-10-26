import spllib

# with open("support/valid-tags.json") as g:
# valids = json.load(g)

with open("support/valid-tags.spl") as g:
    valids = spllib.load(g)


class Tag:
    def __init__(
        self,
        name: str,
        *,
        content: list["Tag"] | None = None,
        self_closing: bool = False,
        **kwargs,
    ):
        self.name = name
        self.content = content if content is not None else []
        self.self_closing = self_closing
        self.attributes = kwargs

        for attr in kwargs:
            attr = attr.lower()
            if attr.startswith("data-"):
                continue  # valid on all tags no matter what comes after
            if (
                attr not in valids
                or valids[attr][0] != "*"
                and self.name.lower() not in valids[attr]
            ):
                raise ValueError(
                    f"The attribute {attr!r} is not valid for the tag <{name}>"
                )

    def appendChild(self, child: "Tag"):
        self.content.append(child)

    def html(self) -> str:
        attrs = " ".join(
            '{}="{}"'.format(k.lower(), v) for (k, v) in self.attributes.items()
        )
        if_self_closing = "/" if self.self_closing else ""
        close_tag = "</{}>".format(self.name) if not self.self_closing else ""
        content = "\n".join(i.html() for i in self.content)

        return """<{name} {if_self_closing} {attrs}>{content}{close_tag}""".format(
            name=self.name,
            if_self_closing=if_self_closing,
            close_tag=close_tag,
            attrs=attrs,
            content=content,
        )


class TextNode(Tag):
    def __init__(self, data: str):
        super().__init__("", content=[], self_closing=True)
        self.data = data

    def html(self) -> str:
        return self.data


class TagGroup(Tag):
    def __init__(self, *tags: Tag):
        super().__init__("Invisible", content=list(tags), self_closing=True)

    def html(self) -> str:
        return "\n".join(i.html() for i in self.content)
