import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import zambian_law_scraper as zls
from zambian_law_scraper import fetch_parliament_acts, fetch_parliament_detail

class TestParliamentScraper(unittest.TestCase):
    def setUp(self):
        # Setup a temp lawdata dir for test isolation
        self.temp_dir = tempfile.mkdtemp()
        self.old_data_dir = zls.DATA_DIR
        zls.DATA_DIR = self.temp_dir
        if not os.path.exists(zls.DATA_DIR):
            os.makedirs(zls.DATA_DIR)
        self.checkpoint_file = os.path.join(self.temp_dir, 'scraper_checkpoint.json')
        self.old_checkpoint_file = zls.CHECKPOINT_FILE
        zls.CHECKPOINT_FILE = self.checkpoint_file

    def tearDown(self):
        # Clean up temp directory and restore original paths
        shutil.rmtree(self.temp_dir)
        zls.DATA_DIR = self.old_data_dir
        zls.CHECKPOINT_FILE = self.old_checkpoint_file

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_parliament_acts_html(self, mock_get):
        # Simulate a Parliament acts page with two links
        html = '''<a href="/uploads/documents/act1.pdf">Act 1</a>\n<a href="/uploads/documents/act2.pdf">Act 2</a>'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        processed_ids = set()
        with patch('zambian_law_scraper.fetch_parliament_detail', return_value={'title': 'Act', 'content': 'Law', 'type': 'act', 'source': 'url', 'related_files': [], 'citations': []}):
            fetch_parliament_acts(processed_ids)
        self.assertEqual(len(processed_ids), 2)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_parliament_detail_pdf(self, mock_get):
        # Simulate a PDF download
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'%PDF-1.4 test pdf content'
        result = fetch_parliament_detail('https://www.parliament.gov.zm/uploads/documents/act1.pdf', 'act')
        self.assertIn('content', result)
        self.assertEqual(result['type'], 'act')
        self.assertEqual(result['source'], 'https://www.parliament.gov.zm/uploads/documents/act1.pdf')

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_parliament_detail_html(self, mock_get):
        # Simulate an HTML law detail page
        html = '<h1>Test Parliament Law</h1><div class="field-item">Law content here.</div>'
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        result = fetch_parliament_detail('https://www.parliament.gov.zm/bills/acts-parliament/123', 'act')
        self.assertIn('Test Parliament Law', result['title'])
        self.assertIn('Law content here.', result['content'])
        self.assertEqual(result['type'], 'act')

if __name__ == '__main__':
    unittest.main()
