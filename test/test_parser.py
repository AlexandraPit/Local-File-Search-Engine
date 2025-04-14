import unittest
from controller import Controller

class TestQueryParser(unittest.TestCase):
    def setUp(self):
        self.controller = Controller()

    def test_path_and_content(self):
        query = "path:foo content:bar"
        expected = {"path": ["foo"], "content": ["bar"]}
        result = self.controller.parse_query(query)
        self.assertEqual(result, expected)

    def test_duplicate_qualifiers(self):
        query = "path:a path:b content:x content:y"
        expected = {"path": ["a", "b"], "content": ["x", "y"]}
        result = self.controller.parse_query(query)
        self.assertEqual(result, expected)

    def test_no_qualifier(self):
        query = "randomsearch terms"
        expected = {"general": ["randomsearch", "terms"]}
        result = self.controller.parse_query(query)
        self.assertEqual(result, expected)

    def test_empty_query(self):
        query = "   "
        expected = {}
        result = self.controller.parse_query(query)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
