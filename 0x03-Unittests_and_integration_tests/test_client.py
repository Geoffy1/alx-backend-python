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

    @patch.object(GithubOrgClient, "_public_repos_url", new_callable=PropertyMock)
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json, mock_public_repos_url):
        """Tests the `public_repos` method."""
        test_payload = [
            {
                "id": 7697149,
                "name": "episodes.dart",
                "private": False,
                "owner": {"login": "google", "id": 1342004},
                "fork": False,
                "url": "https://api.github.com/repos/google/episodes.dart",
                "created_at": "2013-01-19T00:31:37Z",
                "updated_at": "2019-09-23T11:53:58Z",
                "has_issues": True,
                "forks": 22,
                "default_branch": "master",
            },
            {
                "id": 8566972,
                "name": "kratu",
                "private": False,
                "owner": {"login": "google", "id": 1342004},
                "fork": False,
                "url": "https://api.github.com/repos/google/kratu",
                "created_at": "2013-03-04T22:52:33Z",
                "updated_at": "2019-11-15T22:22:16Z",
                "has_issues": True,
                "forks": 32,
                "default_branch": "master",
            },
        ]
        mock_get_json.return_value = test_payload
        mock_public_repos_url.return_value = "https://api.github.com/users/google/repos"
        self.assertEqual(
            GithubOrgClient("google").public_repos(),
            ["episodes.dart", "kratu"],
        )
        mock_public_repos_url.assert_called_once()
        mock_get_json.assert_called_once()


if __name__ == '__main__':
    unittest.main()
