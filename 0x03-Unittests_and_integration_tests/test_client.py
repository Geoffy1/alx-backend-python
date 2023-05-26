#!/usr/bin/env python3
"""A module for testing the client module."""
import unittest
from typing import Dict
from unittest.mock import MagicMock, Mock, PropertyMock, patch
from parameterized import parameterized, parameterized_class
from requests import HTTPError

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Tests the `GithubOrgClient` class."""
    @parameterized.expand([
        ("google", {'login': "google"}),
        ("abc", {'login': "abc"}),
    ])
    @patch("client.get_json")
    def test_org(self, org, resp, mocked_fxn):
        """Tests the `org` method."""
        mocked_fxn.return_value = resp
        gh_org_client = GithubOrgClient(org)
        self.assertEqual(gh_org_client.org(), resp)
        mocked_fxn.assert_called_once_with("https://api.github.com/orgs/{}".format(org))

    def test_public_repos_url(self):
        """Tests the `_public_repos_url` property."""
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {'repos_url': "https://api.github.com/users/google/repos"}
            self.assertEqual(
                GithubOrgClient("google")._public_repos_url,
                "https://api.github.com/users/google/repos",
            )


if __name__ == '__main__':
    unittest.main()
