import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import zambian_law_scraper as zls
from zambian_law_scraper import fetch_hrc_publications, fetch_hrc_publication_detail

class TestHrcScraper(unittest.TestCase):
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
    def test_fetch_hrc_publications_html(self, mock_get):
        # Simulate a HRC publications page with relevant links
        html = '''
        <html>
        <body>
            <a href="/publications/annual-report-2023.html">Annual Report 2023</a>
            <a href="/publications/human-rights-report.html">Human Rights Report</a>
            <a href="/publications/legal-guide.html">Legal Guide for Citizens</a>
            <a href="/publications/manual-2024.pdf">Human Rights Manual 2024</a>
            <a href="/publications/guidelines.doc">Human Rights Guidelines</a>
            <a href="/other/unrelated.html">Unrelated Link</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        processed_ids = set()
        
        with patch('zambian_law_scraper.fetch_hrc_publication_detail', return_value={
            'title': 'Human Rights Publication', 
            'content': 'Human rights content here.', 
            'type': 'human_rights_report', 
            'source': 'url', 
            'related_files': [], 
            'citations': []
        }) as mock_detail:
            fetch_hrc_publications(processed_ids)
        
        # Should find links related to human rights publications
        self.assertGreaterEqual(len(processed_ids), 5)  # At least the 5 relevant links
        
        # Verify the detail function was called multiple times
        self.assertGreater(mock_detail.call_count, 0)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publication_detail_html(self, mock_get):
        # Simulate an HTML human rights publication page
        html = '''
        <html>
        <head><title>Annual Human Rights Report 2024</title></head>
        <body>
            <h1>Annual Report on Human Rights in Zambia 2024</h1>
            <div class="content">
                This annual report provides a comprehensive overview of the human rights 
                situation in Zambia during 2024. It covers civil and political rights, 
                economic and social rights, and the work of the Commission.
            </div>
            <span class="date">Published: 2024-03-15</span>
            <a href="/documents/annual-report-2024.pdf">Download Full Report PDF</a>
            <a href="/documents/executive-summary.doc">Executive Summary</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        result = fetch_hrc_publication_detail('https://www.hrc.org.zm/publications/annual-report-2024', 'human_rights_report')
        
        self.assertIn('Annual Report on Human Rights in Zambia 2024', result['title'])
        self.assertIn('comprehensive overview of the human rights situation', result['content'])
        self.assertEqual(result['type'], 'human_rights_report')
        self.assertEqual(result['year'], '2024')
        self.assertEqual(result['date'], 'Published: 2024-03-15')
        self.assertEqual(len(result['related_files']), 2)
        self.assertEqual(result['related_files'][0]['type'], 'pdf')
        self.assertEqual(result['related_files'][1]['type'], 'document')

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publication_detail_pdf(self, mock_get):
        # Simulate a PDF publication
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'%PDF-1.4 human rights report content'
        
        # Mock PDF download and extraction
        with patch('zambian_law_scraper.download_pdf', return_value='/path/to/hrc-report.pdf') as mock_download:
            with patch('zambian_law_scraper.extract_pdf_text', return_value='Human rights report content with recommendations and findings.') as mock_extract:
                result = fetch_hrc_publication_detail('https://www.hrc.org.zm/publications/report-2024.pdf', 'human_rights_report')
        
        self.assertEqual(result['title'], 'report-2024.pdf')
        self.assertIn('Human rights report content with recommendations', result['content'])
        self.assertEqual(result['type'], 'human_rights_report')
        self.assertEqual(len(result['related_files']), 1)
        self.assertEqual(result['related_files'][0]['type'], 'pdf')
        mock_download.assert_called_once()
        mock_extract.assert_called_once()

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publication_detail_with_year_extraction(self, mock_get):
        # Test year extraction from title
        html = '''
        <html>
        <body>
            <h1>Human Rights Commission Report 2023</h1>
            <div class="publication-content">
                This report covers the activities and findings of the Human Rights 
                Commission during 2023.
            </div>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        result = fetch_hrc_publication_detail('https://www.hrc.org.zm/publications/report-2023', 'human_rights_report')
        
        self.assertIn('Human Rights Commission Report 2023', result['title'])
        self.assertEqual(result['year'], '2023')
        self.assertIn('activities and findings', result['content'])

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publication_detail_with_published_date(self, mock_get):
        # Test date extraction from published div
        html = '''
        <html>
        <body>
            <h2>Special Investigation Report</h2>
            <div class="published">Date Published: 2024-02-20</div>
            <main>
                This special report investigates allegations of human rights violations 
                in detention facilities across Zambia.
            </main>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        result = fetch_hrc_publication_detail('https://www.hrc.org.zm/publications/special-report', 'human_rights_report')
        
        self.assertIn('Special Investigation Report', result['title'])
        self.assertEqual(result['date'], 'Date Published: 2024-02-20')
        self.assertIn('investigates allegations of human rights violations', result['content'])

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publication_detail_main_content_extraction(self, mock_get):
        # Test content extraction from main tag
        html = '''
        <html>
        <body>
            <nav>Navigation menu</nav>
            <main>
                <h1>Human Rights Guidelines</h1>
                <p>These guidelines provide comprehensive information about human rights protections in Zambia.</p>
                <p>They are intended for use by government officials, civil society, and citizens.</p>
            </main>
            <footer>Footer information</footer>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        result = fetch_hrc_publication_detail('https://www.hrc.org.zm/publications/guidelines', 'human_rights_report')
        
        self.assertIn('Human Rights Guidelines', result['content'])
        self.assertIn('comprehensive information about human rights protections', result['content'])
        # Should not include navigation or footer in main content
        self.assertNotIn('Navigation menu', result['content'])
        self.assertNotIn('Footer information', result['content'])

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publication_detail_network_error(self, mock_get):
        # Simulate network error
        mock_get.side_effect = Exception("Request timeout")
        
        result = fetch_hrc_publication_detail('https://www.hrc.org.zm/publications/error-page', 'human_rights_report')
        
        self.assertIsNone(result)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publication_detail_404_error(self, mock_get):
        # Simulate 404 error
        mock_get.return_value.status_code = 404
        
        result = fetch_hrc_publication_detail('https://www.hrc.org.zm/publications/missing-page', 'human_rights_report')
        
        self.assertIsNone(result)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publications_network_error(self, mock_get):
        # Simulate network error when fetching main publications page
        mock_get.side_effect = Exception("Server unreachable")
        processed_ids = set()
        
        # Should handle error gracefully and not crash
        fetch_hrc_publications(processed_ids)
        
        # No IDs should be processed due to network error
        self.assertEqual(len(processed_ids), 0)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publications_status_code_error(self, mock_get):
        # Simulate 500 server error
        mock_get.return_value.status_code = 500
        processed_ids = set()
        
        # Should handle error gracefully and not crash
        fetch_hrc_publications(processed_ids)
        
        # No IDs should be processed due to server error
        self.assertEqual(len(processed_ids), 0)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publications_keyword_filtering(self, mock_get):
        # Test that only relevant links are processed based on keywords
        html = '''
        <html>
        <body>
            <a href="/page1.html">Annual Report 2024</a>
            <a href="/page2.html">Human Rights Publication</a>
            <a href="/page3.html">Legal Guide Manual</a>
            <a href="/page4.html">Publication Guidelines</a>
            <a href="/publications/special-report.html">Special Investigation</a>
            <a href="/page5.html">Unrelated News Article</a>
            <a href="/page6.html">Weather Updates</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        processed_ids = set()
        
        with patch('zambian_law_scraper.fetch_hrc_publication_detail', return_value={
            'title': 'Human Rights Report', 
            'content': 'Human rights content.', 
            'type': 'human_rights_report', 
            'source': 'url', 
            'related_files': [], 
            'citations': []
        }) as mock_detail:
            fetch_hrc_publications(processed_ids)
        
        # Should process links with relevant keywords and /publications/ URLs
        self.assertGreaterEqual(len(processed_ids), 5)  # At least the 5 relevant links
        self.assertLess(len(processed_ids), 7)  # Should not process all 7 links

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_hrc_publication_detail_rtf_related_files(self, mock_get):
        # Test extraction of RTF files in related files
        html = '''
        <html>
        <body>
            <h1>Commission Guidelines</h1>
            <div class="content">Guidelines for human rights investigations.</div>
            <a href="/documents/guidelines.pdf">PDF Guidelines</a>
            <a href="/documents/template.rtf">RTF Template</a>
            <a href="/documents/form.docx">Application Form</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        result = fetch_hrc_publication_detail('https://www.hrc.org.zm/publications/guidelines', 'human_rights_report')
        
        self.assertEqual(len(result['related_files']), 3)
        file_types = [f['type'] for f in result['related_files']]
        self.assertIn('pdf', file_types)
        self.assertIn('document', file_types)  # RTF and DOCX both mapped to 'document'

if __name__ == '__main__':
    unittest.main()
