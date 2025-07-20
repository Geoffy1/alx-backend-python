#!/usr/bin/env python3

"""Unit testing for access_nested_map"""

import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):
    """Tests for access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns correct value"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Tests that KeyError is raised for invalid paths"""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), repr(path[-1]))


class TestGetJson(unittest.TestCase):
    """Testing for get_json"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch("utils.requests.get")
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test get_json returns expected payload & calls requests.get once"""
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        result = get_json(test_url)
        self.assertEqual(result, test_payload)
        mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Test class for memoize decorator."""

    def test_memoize(self):
        """Test that memoize caches the result properly."""
        # Define a test class inside the test method
        class TestClass:
            """Test class for memoization."""
            def a_method(self):
                """Method to be memoized."""
                return 42

            @memoize
            def a_property(self):
                """Memoized property that calls a_method."""
                return self.a_method()

        # Patch a_method to track calls and return value
        with patch.object(TestClass, 'a_method', return_value=42) as mock:
            # Create an instance of TestClass
            test_instance = TestClass()

            # First call to a_property
            result1 = test_instance.a_property
            # Second call to a_property
            result2 = test_instance.a_property

            # Assert the results are correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Assert a_method was called only once
            mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
