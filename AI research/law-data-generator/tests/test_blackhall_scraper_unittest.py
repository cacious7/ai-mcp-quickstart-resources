import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import zambian_law_scraper as zls
from zambian_law_scraper import fetch_blackhall_acts, fetch_blackhall_act_detail

class TestBlackhallScraper(unittest.TestCase):
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
    def test_fetch_blackhall_acts_html(self, mock_get):
        # Simulate a Blackhall acts page with two links on first page, empty on second
        def side_effect(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if 'start=' not in url:  # First page
                resp.text = '''<a href="/acts/act1">Act 1</a>\n<a href="/acts/act2">Act 2</a>'''
            else:  # Subsequent pages - empty
                resp.text = ''
            return resp
        mock_get.side_effect = side_effect
        processed_ids = set()
        with patch('zambian_law_scraper.fetch_blackhall_act_detail', return_value={'title': 'Act', 'content': 'Law', 'type': 'act', 'source': 'url', 'related_files': [], 'citations': []}):
            fetch_blackhall_acts(processed_ids)
        self.assertEqual(len(processed_ids), 2)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_blackhall_act_detail_html(self, mock_get):
        # Simulate an HTML law detail page
        html = '<h1>Test Blackhall Law 2024</h1><div class="item-page">Law content here.</div>'
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        result = fetch_blackhall_act_detail('https://www.zambialaws.com/acts/act1')
        self.assertIn('Test Blackhall Law', result['title'])
        self.assertIn('Law content here.', result['content'])
        self.assertEqual(result['type'], 'act')

if __name__ == '__main__':
    unittest.main()
