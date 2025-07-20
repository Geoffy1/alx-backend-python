#!/usr/bin/env python3
"""
Unit tests and Integration tests for the client.GithubOrgClient class.
"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock
from typing import Dict, List, Any, Tuple # Import for type hints
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos

class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for the GithubOrgClient class.
    """
    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, expected_payload: Dict,
                   mock_get_json: Mock) -> None:
        """
        Test that GithubOrgClient.org returns the correct value
        and get_json is called once with the expected argument.
        """
        mock_get_json.return_value = expected_payload
        
        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self) -> None:
        """
        Test that _public_repos_url returns the expected URL
        based on a mocked org payload.
        """
        test_payload = {"repos_url": "https://api.github.com/orgs/test_org/repos"}
        
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org: # E501 fix
            mock_org.return_value = test_payload
            
            client = GithubOrgClient("test_org")
            result = client._public_repos_url

            self.assertEqual(result, test_payload["repos_url"])
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Test that public_repos returns the expected list of repositories.
        Mocks get_json and _public_repos_url.
        """
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_repos_url = "https://api.github.com/orgs/test_org/repos"

        mock_get_json.return_value = test_repos_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url: # E501 fix
            mock_public_repos_url.return_value = mock_repos_url

            client = GithubOrgClient("test_org")
            result = client.public_repos

            expected_repos_names = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos_names)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(mock_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({"license": {"key": "my_license"}, "name": "repo"}, "my_license", True),
    ])
    def test_has_license(self, repo: Dict, license_key: str,
                         expected_result: bool) -> None: # E501 fix
        """
        Test that has_license returns the correct boolean value.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class([
    {
        'org_payload': org_payload,
        'repos_payload': repos_payload,
        'expected_repos': expected_repos,
        'apache2_repos': apache2_repos
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.
    Mocks external HTTP calls using fixtures.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up class method to mock `client.get_json` using `side_effect`.
        This mocks the external HTTP calls at the point they are made by the client.
        """
        cls.get_patcher = patch('client.get_json')
        cls.mock_get_json = cls.get_patcher.start()

        # Define the side_effect function to return different payloads based on URL
        def side_effect_func(url: str) -> Dict:
            if url == cls.org_payload["repos_url"].replace("/repos", ""):
                return cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                return cls.repos_payload
            # For `test_public_repos_with_license`, the filtering happens internally,
            # so `get_json` for repos URL still returns `repos_payload`.
            return {} # Fallback for unexpected URLs

        cls.mock_get_json.side_effect = side_effect_func

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Tear down class method to stop the patcher.
        """
        cls.get_patcher.stop()

    def test_public_repos_integration(self) -> None: # Renamed for clarity vs unit test
        """
        Test that public_repos returns the expected results based on the fixtures
        in an integration context.
        """
        client = GithubOrgClient("google")
        # Ensure the mock was called correctly for the org URL first
        # Then for the repos URL
        self.assertEqual(client.public_repos, self.expected_repos)
        self.mock_get_json.assert_any_call(
            self.org_payload["repos_url"].replace("/repos", "")
        )
        self.mock_get_json.assert_any_call(self.org_payload["repos_url"])

    def test_public_repos_with_license_integration(self) -> None: # Renamed for clarity
        """
        Test public_repos with a license argument in an integration context.
        """
        client = GithubOrgClient("google")
        # The public_repos method will fetch all repos (via mock),
        # then filter them using has_license based on the provided license key.
        self.assertEqual(client.public_repos(license="apache-2.0"),
                         self.apache2_repos) # E501 fix
        self.mock_get_json.assert_any_call(
            self.org_payload["repos_url"].replace("/repos", "")
        )
        self.mock_get_json.assert_any_call(self.org_payload["repos_url"])
