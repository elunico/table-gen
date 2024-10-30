import unittest
import os


from tag import _find_by_id, Tag


class TestTag(unittest.TestCase):
    def setUp(self):
        self.root = Tag("root", **{"id": "root"})
        self.child1 = Tag("child1", **{"id": "child1"})
        self.child2 = Tag("child2", **{"id": "child2"})
        self.child1.children = [self.child2]
        self.root.children = [self.child1]

    def test__find_by_id_root(self):
        self.assertEqual(_find_by_id("root", self.root), self.root)

    def test__find_by_id_child1(self):
        self.assertEqual(_find_by_id("child1", self.root), self.child1)

    def test__find_by_id_child2(self):
        self.assertEqual(_find_by_id("child2", self.root), self.child2)

    def test__find_by_id_non_existent_id(self):
        self.assertEqual(_find_by_id("non_existent_id", self.root), None)


if __name__ == "__main__":
    unittest.main()
