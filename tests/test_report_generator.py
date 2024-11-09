import unittest
import os
from unittest.mock import patch, MagicMock
from src.report_generator import ReportGenerator
from datetime import date

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.llm = MagicMock()
        self.generator = ReportGenerator(self.llm)
        self.test_updates = {
            'issues': [{'title': 'Test Issue', 'number': 1}],
            'pull_requests': [{'title': 'Test PR', 'number': 2}]
        }

    def tearDown(self):
        if os.path.exists('daily_progress'):
            for root, dirs, files in os.walk('daily_progress', topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir('daily_progress')

    def test_export_daily_progress(self):
        result = self.generator.export_daily_progress('owner/repo', self.test_updates)
        self.assertTrue(os.path.exists(result))
        with open(result, 'r') as f:
            content = f.read()
            self.assertIn('Test Issue #1', content)
            self.assertIn('Test PR #2', content)

    def test_export_progress_by_date_range(self):
        result = self.generator.export_progress_by_date_range('owner/repo', self.test_updates, 7)
        self.assertTrue(os.path.exists(result))

    def test_generate_daily_report(self):
        test_file = 'test_report.md'
        with open(test_file, 'w') as f:
            f.write('# Test Report')
        
        self.llm.generate_daily_report.return_value = 'Generated Report'
        
        report, path = self.generator.generate_daily_report(test_file)
        self.assertEqual(report, 'Generated Report')
        self.assertTrue(os.path.exists(path))
        
        os.remove(test_file)
        os.remove(path)

    def test_generate_report_by_date_range(self):
        test_file = 'test_range_report.md'
        with open(test_file, 'w') as f:
            f.write('# Test Range Report')
        
        self.llm.generate_daily_report.return_value = 'Generated Range Report'
        
        report, path = self.generator.generate_report_by_date_range(test_file, 7)
        self.assertEqual(report, 'Generated Range Report')
        self.assertTrue(os.path.exists(path))
        
        os.remove(test_file)
        os.remove(path) 