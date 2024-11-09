import unittest
from unittest.mock import patch, MagicMock
import gradio as gr
from src.gradio_server import export_progress_by_date_range, demo

class TestGradioServer(unittest.TestCase):
    def setUp(self):
        self.patches = [
            patch('src.gradio_server.Config'),
            patch('src.gradio_server.GitHubClient'),
            patch('src.gradio_server.ReportGenerator'),
            patch('src.gradio_server.SubscriptionManager')
        ]
        self.mocks = [p.start() for p in self.patches]
        self.mock_github = self.mocks[1].return_value
        self.mock_report = self.mocks[2].return_value
        self.mock_sub_manager = self.mocks[3].return_value

        # 设置模拟返回值
        self.mock_github.export_progress_by_date_range.return_value = 'test.md'
        self.mock_report.generate_report_by_date_range.return_value = ('Test Report', 'report.md')
        self.mock_sub_manager.list_subscriptions.return_value = ['repo1', 'repo2']

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_export_progress_success(self):
        result = export_progress_by_date_range('owner/repo', 7)
        self.assertEqual(result, ('Test Report', 'report.md'))
        self.mock_github.export_progress_by_date_range.assert_called_once()
        self.mock_report.generate_report_by_date_range.assert_called_once()

    def test_export_progress_github_error(self):
        self.mock_github.export_progress_by_date_range.side_effect = Exception('GitHub error')
        result = export_progress_by_date_range('owner/repo', 7)
        self.assertEqual(result, (None, None))

    def test_export_progress_report_error(self):
        self.mock_report.generate_report_by_date_range.side_effect = Exception('Report error')
        result = export_progress_by_date_range('owner/repo', 7)
        self.assertEqual(result, (None, None))

    def test_demo_interface_creation(self):
        self.assertIsInstance(demo, gr.Interface)
        self.assertEqual(len(demo.inputs), 2)
        self.assertEqual(len(demo.outputs), 2)

    @patch('gradio.Interface.launch')
    def test_demo_launch(self, mock_launch):
        demo.launch(share=True)
        mock_launch.assert_called_once_with(share=True)