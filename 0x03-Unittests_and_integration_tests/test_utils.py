#!/usr/bin/env python3
"""
Unit tests for the utils.access_nested_map function, get_json function,
and the memoize decorator.
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from typing import Mapping, Sequence, Any # Import for type hints
from utils import access_nested_map, get_json, memoize

class TestAccessNestedMap(unittest.TestCase):
    """
    Tests for the access_nested_map function.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: Mapping, path: Sequence,
                               expected: Any) -> None:
        """
        Test that access_nested_map returns the expected result for various inputs.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map: Mapping,
                                         path: Sequence,
                                         expected_message: str) -> None:
        """
        Test that access_nested_map raises KeyError with the expected message.
        """
        with self.assertRaisesRegex(KeyError, expected_message):
            access_nested_map(nested_map, path)

class TestGetJson(unittest.TestCase):
    """
    Tests for the get_json function.
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url: str, test_payload: Mapping,
                       mock_requests_get: Mock) -> None:
        """
        Test that get_json returns the expected result and calls requests.get correctly.
        """
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_requests_get.return_value = mock_response

        result = get_json(test_url)

        mock_requests_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)

class TestMemoize(unittest.TestCase):
    """
    Tests for the memoize decorator.
    """
    # Moved TestClass definition outside the method for more stable patching.
    class TestClass:
        """Helper class for memoize testing."""
        def a_method(self) -> int:
            """A simple method."""
            return 42

        @memoize
        def a_property(self) -> int:
            """A memoized property."""
            return self.a_method()

    def test_memoize(self) -> None:
        """
        Test that a_property returns the correct result and a_method is called once.
        """
        # Patch the 'a_method' on the nested TestClass
        with patch.object(self.TestClass, 'a_method') as mock_a_method:
            mock_a_method.return_value = 42

            test_instance = self.TestClass()

            # Call a_property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Assertions
            mock_a_method.assert_called_once()
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
