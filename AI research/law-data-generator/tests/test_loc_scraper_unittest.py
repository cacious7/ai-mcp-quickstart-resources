import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import zambian_law_scraper as zls
from zambian_law_scraper import fetch_loc_references, fetch_loc_reference_detail

class TestLocScraper(unittest.TestCase):
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
    def test_fetch_loc_references_html(self, mock_get):
        # Simulate a Law Library of Congress page with relevant links
        html = '''
        <html>
        <body>
            <a href="/law/guide/zambia-constitution.html">Zambia Constitution Guide</a>
            <a href="/law/legal-resources/zambia.pdf">Legal Resources PDF</a>
            <a href="/law/help/zambian-law-overview.html">Zambian Law Overview</a>
            <a href="https://external.com/zambia-statute.pdf">External Statute Link</a>
            <a href="/other/unrelated.html">Unrelated Link</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        processed_ids = set()
        
        with patch('zambian_law_scraper.fetch_loc_reference_detail', return_value={
            'title': 'Legal Reference', 
            'content': 'Legal content here.', 
            'type': 'reference', 
            'source': 'url', 
            'related_files': [], 
            'citations': []
        }) as mock_detail:
            fetch_loc_references(processed_ids)
        
        # Should find links related to Zambian law
        self.assertGreaterEqual(len(processed_ids), 3)  # At least the 3 relevant links
        
        # Verify the detail function was called multiple times
        self.assertGreater(mock_detail.call_count, 0)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_loc_reference_detail_html(self, mock_get):
        # Simulate an HTML legal reference page
        html = '''
        <html>
        <head><title>Zambia Legal Guide 2024</title></head>
        <body>
            <h1>Legal System of Zambia</h1>
            <div id="content">
                This guide provides an overview of the legal system in Zambia. 
                The Constitution of Zambia establishes the framework...
            </div>
            <meta name="date" content="2024-01-15">
            <a href="/documents/zambia-constitution.pdf">Download Constitution PDF</a>
            <a href="/documents/legal-guide.doc">Download Legal Guide</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        result = fetch_loc_reference_detail('https://www.loc.gov/law/help/guide/nations/zambia.php', 'reference')
        
        self.assertIn('Zambia Legal Guide', result['title'])
        self.assertIn('legal system in Zambia', result['content'])
        self.assertEqual(result['type'], 'reference')
        self.assertEqual(result['date'], '2024-01-15')
        self.assertEqual(len(result['related_files']), 2)
        self.assertEqual(result['related_files'][0]['type'], 'pdf')
        self.assertEqual(result['related_files'][1]['type'], 'document')

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_loc_reference_detail_pdf(self, mock_get):
        # Simulate a PDF reference
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'%PDF-1.4 test legal content'
        
        # Mock PDF download and extraction
        with patch('zambian_law_scraper.download_pdf', return_value='/path/to/legal-guide.pdf') as mock_download:
            with patch('zambian_law_scraper.extract_pdf_text', return_value='Legal guide content from PDF.') as mock_extract:
                result = fetch_loc_reference_detail('https://www.loc.gov/law/documents/zambia-guide.pdf', 'reference')
        
        self.assertEqual(result['title'], 'zambia-guide.pdf')
        self.assertIn('Legal guide content from PDF', result['content'])
        self.assertEqual(result['type'], 'reference')
        self.assertEqual(len(result['related_files']), 1)
        self.assertEqual(result['related_files'][0]['type'], 'pdf')
        mock_download.assert_called_once()
        mock_extract.assert_called_once()

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_loc_reference_detail_with_meta_date(self, mock_get):
        # Test extraction of date from meta tag
        html = '''
        <html>
        <head>
            <title>Zambia Legal Resources</title>
            <meta property="article:published_time" content="2023-12-01T10:00:00Z">
        </head>
        <body>
            <div class="content">Legal resources and guides for Zambia.</div>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        result = fetch_loc_reference_detail('https://www.loc.gov/law/zambia-resources', 'reference')
        
        self.assertEqual(result['date'], '2023-12-01T10:00:00Z')
        self.assertIn('Legal resources and guides', result['content'])

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_loc_reference_detail_network_error(self, mock_get):
        # Simulate network error
        mock_get.side_effect = Exception("Network timeout")
        
        result = fetch_loc_reference_detail('https://www.loc.gov/law/error-page', 'reference')
        
        self.assertIsNone(result)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_loc_reference_detail_404_error(self, mock_get):
        # Simulate 404 error
        mock_get.return_value.status_code = 404
        
        result = fetch_loc_reference_detail('https://www.loc.gov/law/missing-page', 'reference')
        
        self.assertIsNone(result)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_loc_references_network_error(self, mock_get):
        # Simulate network error when fetching main page
        mock_get.side_effect = Exception("Connection failed")
        processed_ids = set()
        
        # Should handle error gracefully and not crash
        fetch_loc_references(processed_ids)
        
        # No IDs should be processed due to network error
        self.assertEqual(len(processed_ids), 0)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_loc_references_main_content_extraction(self, mock_get):
        # Test various content div extraction scenarios
        html = '''
        <html>
        <body>
            <main>
                <h1>Zambia Legal Information</h1>
                <p>Main content in the main tag.</p>
            </main>
            <a href="/law/zambia-acts.html">Zambia Acts</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        processed_ids = set()
        
        with patch('zambian_law_scraper.fetch_loc_reference_detail', return_value={
            'title': 'Legal Reference', 
            'content': 'Main content in the main tag.', 
            'type': 'reference', 
            'source': 'url', 
            'related_files': [], 
            'citations': []
        }):
            fetch_loc_references(processed_ids)
        
        self.assertGreater(len(processed_ids), 0)

if __name__ == '__main__':
    unittest.main()
