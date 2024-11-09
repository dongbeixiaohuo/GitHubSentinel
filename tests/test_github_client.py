import unittest
from unittest.mock import patch, MagicMock
from src.github_client import GitHubClient
from datetime import datetime
import os

class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        self.client = GitHubClient('test_token')

    @patch('requests.get')
    def test_fetch_commits(self, mock_get):
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = [{'sha': '123', 'commit': {'message': 'test commit'}}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.fetch_commits('owner/repo')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['sha'], '123')

    @patch('requests.get')
    def test_fetch_issues(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{'number': 1, 'title': 'test issue'}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.fetch_issues('owner/repo')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['number'], 1)

    def test_export_daily_progress(self):
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            result = self.client.export_daily_progress('owner/repo')
            self.assertTrue(os.path.exists(result))

    def test_export_progress_by_date_range(self):
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            result = self.client.export_progress_by_date_range('owner/repo', 7)
            self.assertTrue(os.path.exists(result))