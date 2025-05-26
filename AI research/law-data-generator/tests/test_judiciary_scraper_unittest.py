import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import zambian_law_scraper as zls
from zambian_law_scraper import fetch_judiciary_cases, fetch_judiciary_case_detail

class TestJudiciaryScraper(unittest.TestCase):
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
    def test_fetch_judiciary_cases_html(self, mock_get):
        # Simulate a Judiciary cases page with two links on first page, empty on second
        def side_effect(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if '?page=' not in url:  # First page
                resp.text = '''<a href="/case/case1">Case 1</a>\n<a href="/judgment/judgment1">Judgment 1</a>'''
            else:  # Subsequent pages - empty
                resp.text = ''
            return resp
        mock_get.side_effect = side_effect
        processed_ids = set()
        with patch('zambian_law_scraper.fetch_judiciary_case_detail', return_value={'title': 'Case', 'content': 'Judgment text', 'type': 'judgment', 'source': 'url', 'related_files': [], 'citations': []}):
            fetch_judiciary_cases(processed_ids)
        self.assertEqual(len(processed_ids), 2)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_judiciary_case_detail_html(self, mock_get):
        # Simulate an HTML case detail page
        html = '''<h1>Test Case v. State 2024</h1>
                  <div class="case-content">This is the judgment content. The court ruled...</div>
                  <span class="date">2024-01-15</span>'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        result = fetch_judiciary_case_detail('https://www.judiciaryzambia.com/case/test-case', 'judgment')
        self.assertIn('Test Case v. State', result['title'])
        self.assertIn('judgment content', result['content'])
        self.assertEqual(result['type'], 'judgment')
        self.assertEqual(result['date'], '2024-01-15')

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_judiciary_case_detail_with_pdf(self, mock_get):
        # Simulate an HTML case detail page with PDF link
        html = '''<h1>Supreme Court Case 2024</h1>
                  <div class="judgment-content">Court judgment here.</div>
                  <a href="/documents/case123.pdf">Download PDF</a>'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        # Mock PDF download and extraction
        with patch('zambian_law_scraper.download_pdf', return_value='/path/to/case123.pdf') as mock_download:
            with patch('zambian_law_scraper.extract_pdf_text', return_value='PDF judgment content here.') as mock_extract:
                result = fetch_judiciary_case_detail('https://www.judiciaryzambia.com/case/supreme-case', 'supreme_court_judgment')
        
        self.assertIn('Supreme Court Case', result['title'])
        self.assertIn('PDF judgment content', result['content'])  # PDF content should replace HTML content
        self.assertEqual(result['type'], 'supreme_court_judgment')
        self.assertEqual(len(result['related_files']), 1)
        self.assertEqual(result['related_files'][0]['type'], 'pdf')

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_judiciary_case_detail_with_citations(self, mock_get):
        # Simulate an HTML case detail page with citation links
        html = '''<h1>High Court Case 2023</h1>
                  <div class="case-body">The court considered precedent from...</div>
                  <a class="citation">Smith v. Jones [2020] HC 123</a>
                  <a class="case-ref">Brown v. State [2019] SC 456</a>'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        result = fetch_judiciary_case_detail('https://www.judiciaryzambia.com/case/high-court-case', 'high_court_judgment')
        self.assertIn('High Court Case', result['title'])
        self.assertIn('court considered precedent', result['content'])
        self.assertEqual(result['type'], 'high_court_judgment')
        self.assertGreater(len(result['citations']), 0)
        self.assertIn('Smith v. Jones [2020] HC 123', result['citations'])

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_judiciary_case_detail_network_error(self, mock_get):
        # Simulate network error
        mock_get.side_effect = Exception("Network error")
        result = fetch_judiciary_case_detail('https://www.judiciaryzambia.com/case/error-case', 'judgment')
        self.assertIsNone(result)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_judiciary_case_detail_404_error(self, mock_get):
        # Simulate 404 error
        mock_get.return_value.status_code = 404
        result = fetch_judiciary_case_detail('https://www.judiciaryzambia.com/case/missing-case', 'judgment')
        self.assertIsNone(result)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_judiciary_cases_multiple_court_types(self, mock_get):
        # Test that different court sections are processed
        def side_effect(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if 'supreme-court-cases' in url:
                resp.text = '<a href="/case/supreme1">Supreme Case 1</a>'
            elif 'high-court-cases' in url:
                resp.text = '<a href="/case/high1">High Court Case 1</a>'
            elif 'subordinate-court-cases' in url:
                resp.text = '<a href="/case/sub1">Subordinate Case 1</a>'
            elif '/cases' in url and 'court' not in url:
                resp.text = '<a href="/case/general1">General Case 1</a>'
            else:
                resp.text = ''  # Empty for pagination
            return resp
        mock_get.side_effect = side_effect
        processed_ids = set()
        with patch('zambian_law_scraper.fetch_judiciary_case_detail', return_value={'title': 'Case', 'content': 'Judgment', 'type': 'judgment', 'source': 'url', 'related_files': [], 'citations': []}):
            fetch_judiciary_cases(processed_ids)
        # Should have processed cases from all 4 court sections
        self.assertEqual(len(processed_ids), 4)

if __name__ == '__main__':
    unittest.main()
