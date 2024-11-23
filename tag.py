from os import replace
import spllib
import weakref
import enum
from pytomutil.dicts import ReplaceMode, key_merge, key_migrate
import typing

with open("support/valid-tags.spl") as g:
    valids = spllib.load(g)


def check_valid_attr(attr: str, tag: str):
    attr = attr.lower()
    if attr.startswith("data-"):
        return  # valid on all tags no matter what comes after
    if attr not in valids:
        raise ValueError(f"No such HTML attribute {attr!r}")
    if valids[attr][0] != "*" and tag.lower() not in valids[attr]:
        raise ValueError(f"The attribute {attr!r} is not valid for the tag <{tag}>")


def _find_by_id(id: str, root: "Tag") -> "Tag | None":
    if root.attributes.get("id", None) == id:
        return root
    else:
        for child in root.children:
            result = _find_by_id(id, child)
            if result is not None:
                return result
        return None


def _find_by_class(classname: str, root: "Tag", limit: int = 0) -> list["Tag"]:
    def _find_by_class_impl(
        classname: str, root: "Tag", items: list["Tag"]
    ) -> list["Tag"]:
        if root.attributes.get("class", None) == classname:
            items.append(root)
            if limit > 0 and len(items) == limit:
                return items

        for child in root.children:
            _find_by_class_impl(classname, child, items)

        return items

    return _find_by_class_impl(classname, root, [])


def _find_by_tag(tagname: str, root: "Tag", limit: int = 0) -> list["Tag"]:
    def find_tag_impl(tagname: str, root: "Tag", items: list["Tag"]) -> list["Tag"]:
        if root.name.lower() == tagname.lower():
            items.append(root)
            if limit > 0 and len(items) == limit:
                return items

        for child in root.children:
            find_tag_impl(tagname, child, items)

        return items

    return find_tag_impl(tagname, root, [])


class Tag:
    def __init__(
        self,
        name: str,
        *,
        children: list["Tag"] | None = None,
        self_closing: bool = False,
        check_attrs: bool = True,
        **kwargs,
    ):
        self.name = name
        self.children = children if children is not None else []
        self.self_closing = self_closing
        self.attributes = kwargs
        self.parent: weakref.ReferenceType[Tag] | None = None

        key_merge(
            self.attributes,
            "clazz",
            "klass",
            "classname",
            "Class",
            target="class",
            repl_mode=ReplaceMode.REPLACING,
            deleting=True,
            in_place=True,
        )

        if not check_attrs:
            return

        lname = self.name.lower()
        for attr in kwargs:
            check_valid_attr(attr, lname)

    def __str__(self):
        return f'{self.open_tag()}{"..." if self.children else ""}{self.close_tag()}'

    def __repr__(self) -> str:
        return str(self)

    def pprint(self, indent=0):
        print(" " * indent + self.open_tag())
        for child in self.children:
            child.pprint(indent + 4)
        print(" " * indent + self.close_tag())

    def appendChild(self, child: "Tag"):
        if not isinstance(child, Tag):
            raise TypeError("child must be tag")
        self.children.append(child)
        child.parent = weakref.ref(self)

    def removeChild(self, child: "Tag") -> bool:
        try:
            self.children.remove(child)
            return True
        except ValueError:
            return False

    def _get_parent_index_offset(self, offset) -> "Tag | None":
        try:
            if self.parent is None:
                return None
            if (p := self.parent()) is None:
                return None
            idx = p.children.index(self)
            return p.children[idx + offset]
        except (ValueError, IndexError):
            return None

    def nextSibling(self) -> "Tag | None":
        return self._get_parent_index_offset(1)

    def previousSibling(self) -> "Tag | None":
        return self._get_parent_index_offset(-1)

    def select(self, selector: str) -> "Tag | None":
        if selector[0] == "#":
            return _find_by_id(selector[1:], self)
        if selector[0] == ".":
            return r[0] if (r := _find_by_class(selector[1:], self, limit=1)) else None
        if selector[0].isalpha():
            return r[0] if (r := _find_by_tag(selector, self, limit=1)) else None

        raise ValueError(f"Invalid selector {selector!r}")

    def select_all(self, selector: str) -> list["Tag"]:
        if selector[0] == "#":
            return [] if (v := _find_by_id(selector[1:], self)) is None else [v]
        if selector[0] == ".":
            return _find_by_class(selector[1:], self)
        if selector[0].isalpha():
            return _find_by_tag(selector, self)

        raise ValueError(f"Invalid selector {selector!r}")

    def setAttribute(self, attr: str, value: str, check: bool = True):
        if check:
            check_valid_attr(attr, self.name.lower())

        self.attributes[attr] = value

    def removeAttribute(self, attr: str) -> bool:
        if attr in self.attributes:
            del self.attributes[attr]
            return True
        return False

    def getAttribute(self, attr: str) -> str | None:
        return self.attributes.get(attr, None)

    def open_tag(self) -> str:
        attrs = " ".join(
            '{}="{}"'.format(k.lower(), v) for (k, v) in self.attributes.items()
        ).strip()
        if_self_closing = "/" if self.self_closing else ""
        name = self.name.lower()

        content = f"{name} {attrs} {if_self_closing}".strip()
        return f"<{content}>"

    def close_tag(self) -> str:
        return "</{}>".format(self.name) if not self.self_closing else ""

    def html(self) -> str:
        children = "\n".join(i.html() for i in self.children)
        return f"{self.open_tag()}{children}{self.close_tag()}"


class TextNode(Tag):
    def __init__(self, data: str):
        super().__init__("", children=[], self_closing=True)
        self.data = data

    def appendChild(self, child: "Tag"):
        raise TypeError("TextNode cannot have children")

    def dom(self) -> Tag:
        return self

    def html(self) -> str:
        return self.data


class TagGroup(Tag):
    def __init__(self, *tags: Tag):
        super().__init__("Invisible", children=list(tags), self_closing=True)

    def html(self) -> str:
        return "\n".join(i.html() for i in self.children)
