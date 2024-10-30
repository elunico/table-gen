import unittest
import os


from tag import _find_by_class, Tag


class TestFindByClass(unittest.TestCase):
    def setUp(self):
        self.root = Tag("div", **{"class": "root"})
        self.child1 = Tag("span", **{"class": "child1"})
        self.child2 = Tag("span", **{"class": "child2"})
        self.child1_1 = Tag("p", **{"class": "child1"})
        self.child2_1 = Tag("p", **{"class": "child2"})
        self.root.children.extend([self.child1, self.child2])
        self.child1.children.append(self.child1_1)
        self.child2.children.append(self.child2_1)

    def test__find_by_class(self):
        result = _find_by_class("child1", self.root)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].attributes["class"], "child1")
        self.assertEqual(result[1].attributes["class"], "child1")

    def test__find_by_class_no_match(self):
        result = _find_by_class("no_match", self.root)
        self.assertEqual(len(result), 0)

    def test__find_by_class_none(self):
        result = _find_by_class(None, self.root)
        self.assertEqual(len(result), 0)

    def test__find_by_class_empty_string(self):
        result = _find_by_class("", self.root)
        self.assertEqual(len(result), 0)

    def test__find_by_class_on_root(self):
        result = _find_by_class("root", self.root)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
