import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos
from client import GithubOrgClient


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test the public_repos method."""
        self.mock_get.side_effect = [
            MagicMock(json=lambda: org_payload),
            MagicMock(json=lambda: repos_payload),
        ]
        github_org_client = GithubOrgClient("test")
        repos = github_org_client.public_repos()
        self.assertEqual(repos, expected_repos)
        self.mock_get.assert_called_with('https://api.github.com/orgs/test')
        self.mock_get.assert_called_with('https://api.github.com/orgs/test/repos')

    def test_public_repos_with_license(self):
        """Test the public_repos method with license filter."""
        self.mock_get.side_effect = [
            MagicMock(json=lambda: org_payload),
            MagicMock(json=lambda: repos_payload),
        ]
        github_org_client = GithubOrgClient("test")
        repos = github_org_client.public_repos(license="apache-2.0")
        self.assertEqual(repos, apache2_repos)
        self.mock_get.assert_called_with('https://api.github.com/orgs/test')
        self.mock_get.assert_called_with('https://api.github.com/orgs/test/repos')


if __name__ == '__main__':
    unittest.main()
