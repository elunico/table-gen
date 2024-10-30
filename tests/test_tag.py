import unittest
import os

# os.chdir('..')
from tag import _find_by_tag, Tag


class TestFindByTag(unittest.TestCase):
    def setUp(self):
        self.root = Tag("html")
        self.body = Tag("body")
        self.head = Tag("head")
        self.title = Tag("title")
        self.h1 = Tag("h1")
        self.p = Tag("p")

        self.root.appendChild(self.head)
        self.root.appendChild(self.body)
        self.head.appendChild(self.title)
        self.body.appendChild(self.h1)
        self.body.appendChild(self.p)

    def test_find_by_tag(self):
        found_tags = _find_by_tag("h1", self.root)
        self.assertEqual(len(found_tags), 1)
        self.assertEqual(found_tags[0].name, "h1")

    def test_find_by_tag_ignore_case(self):
        found_tags = _find_by_tag("Title", self.root)
        self.assertEqual(len(found_tags), 1)
        self.assertEqual(found_tags[0].name, "title")

    def test_find_by_tag_no_result(self):
        found_tags = _find_by_tag("div", self.root)
        self.assertEqual(len(found_tags), 0)

    def test_find_duplicate_tag_names(self):
        paragraph = Tag("p")
        self.body.appendChild(paragraph)
        found_tags = _find_by_tag("p", self.root)
        self.assertEqual(len(found_tags), 2)


if __name__ == "__main__":
    unittest.main()
