import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import zambian_law_scraper as zls
from zambian_law_scraper import fetch_globalex_references, fetch_globalex_reference_detail

class TestGlobalexScraper(unittest.TestCase):
    def setUp(self):
        # Setup a temp lawdata dir for test isolation
        self.temp_dir = tempfile.mkdtemp()
        self.old_data_dir = zls.DATA_DIR
        zls.DATA_DIR = self.temp_dir
        if not os.path.exists(zls.DATA_DIR):
            os.makedirs(zls.DATA_DIR)
        self.checkpoint_file = os.path.join(self.temp_dir, 'scraper_checkpoint.json')
        zls.CHECKPOINT_FILE = self.checkpoint_file

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        zls.DATA_DIR = self.old_data_dir
        zls.CHECKPOINT_FILE = 'scraper_checkpoint.json'
    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_references_html(self, mock_get):
        # Simulate a GlobaLex page with relevant links
        html = '''
        <html>
        <body>
            <a href="/research/zambia-legal-research.html">Zambia Legal Research Guide</a>
            <a href="/guides/zambian-law-resources.html">Zambian Law Resources</a>
            <a href="/database/zambia-legal-database.html">Legal Database</a>
            <a href="/documents/zambia-guide.pdf">Zambia Legal Guide PDF</a>
            <a href="/documents/research-manual.doc">Research Manual</a>
            <a href="/other/unrelated.html">Unrelated Link</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        processed_ids = set()
        
        with patch('zambian_law_scraper.fetch_globalex_reference_detail', return_value={
            'title': 'Legal Research Guide', 
            'content': 'Research guide content here.', 
            'type': 'reference', 
            'source': 'url', 
            'related_files': [], 
            'citations': []
        }) as mock_detail:
            fetch_globalex_references(processed_ids)
        
        # Should find links related to research and legal guides
        self.assertGreaterEqual(len(processed_ids), 4)  # At least the 4 relevant links
        
        # Verify the detail function was called multiple times
        self.assertGreater(mock_detail.call_count, 0)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_reference_detail_html(self, mock_get):
        # Simulate an HTML research guide page
        html = '''
        <html>
        <head><title>Zambia Legal Research Guide</title></head>
        <body>
            <h1>Legal Research in Zambia</h1>
            <div id="content">
                This guide provides researchers with comprehensive information about 
                accessing and researching Zambian law. It covers primary sources, 
                secondary sources, and research strategies.
            </div>
            <a href="/documents/research-supplement.pdf">Download Research Supplement</a>
            <a href="/documents/citation-guide.rtf">Citation Guide</a>
        </body>        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        result = fetch_globalex_reference_detail('https://www.nyulawglobal.org/globalex/zambia-research.html', 'reference')
        
        self.assertIn('Zambia Legal Research Guide', result['title'])
        # Handle potential whitespace and newlines in extracted content
        content_normalized = ' '.join(result['content'].split())
        self.assertIn('comprehensive information about accessing', content_normalized)
        self.assertEqual(result['type'], 'reference')
        self.assertEqual(len(result['related_files']), 2)
        self.assertEqual(result['related_files'][0]['type'], 'pdf')
        self.assertEqual(result['related_files'][1]['type'], 'document')

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_reference_detail_pdf(self, mock_get):
        # Simulate a PDF research guide
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'%PDF-1.4 research guide content'
        
        # Mock PDF download and extraction
        with patch('zambian_law_scraper.download_pdf', return_value='/path/to/research-guide.pdf') as mock_download:
            with patch('zambian_law_scraper.extract_pdf_text', return_value='Research guide content from PDF with legal citations.') as mock_extract:
                result = fetch_globalex_reference_detail('https://www.nyulawglobal.org/documents/zambia-research.pdf', 'reference')
        
        self.assertEqual(result['title'], 'zambia-research.pdf')
        self.assertIn('Research guide content from PDF', result['content'])
        self.assertEqual(result['type'], 'reference')
        self.assertEqual(len(result['related_files']), 1)
        self.assertEqual(result['related_files'][0]['type'], 'pdf')
        mock_download.assert_called_once()
        mock_extract.assert_called_once()

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_reference_detail_doc_file(self, mock_get):
        # Simulate a DOC file reference
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'Word document content'
        
        result = fetch_globalex_reference_detail('https://www.nyulawglobal.org/documents/research-manual.doc', 'reference')
        
        self.assertEqual(result['title'], 'research-manual.doc')
        self.assertEqual(result['content'], 'Document reference: research-manual.doc')
        self.assertEqual(result['type'], 'reference')
        self.assertEqual(len(result['related_files']), 1)
        self.assertEqual(result['related_files'][0]['type'], 'document')
        self.assertEqual(result['related_files'][0]['url'], 'https://www.nyulawglobal.org/documents/research-manual.doc')

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_reference_detail_docx_file(self, mock_get):
        # Simulate a DOCX file reference
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'Word XML document content'
        
        result = fetch_globalex_reference_detail('https://www.nyulawglobal.org/documents/legal-guide.docx', 'reference')
        
        self.assertEqual(result['title'], 'legal-guide.docx')
        self.assertEqual(result['content'], 'Document reference: legal-guide.docx')
        self.assertEqual(result['type'], 'reference')
        self.assertEqual(len(result['related_files']), 1)
        self.assertEqual(result['related_files'][0]['type'], 'document')

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_reference_detail_main_tag_content(self, mock_get):
        # Test content extraction from main tag
        html = '''
        <html>
        <body>
            <header>Header content</header>
            <main>
                <h1>Legal Research Resources</h1>
                <p>Main content about Zambian legal research resources.</p>
            </main>
            <footer>Footer content</footer>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        
        result = fetch_globalex_reference_detail('https://www.nyulawglobal.org/globalex/zambia-resources', 'reference')
        
        self.assertIn('Legal Research Resources', result['content'])
        self.assertIn('Main content about Zambian legal research', result['content'])
        # Should not include header/footer content in main content extraction
        self.assertNotIn('Header content', result['content'])
        self.assertNotIn('Footer content', result['content'])

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_reference_detail_network_error(self, mock_get):
        # Simulate network error
        mock_get.side_effect = Exception("Connection timeout")
        
        result = fetch_globalex_reference_detail('https://www.nyulawglobal.org/globalex/error-page', 'reference')
        
        self.assertIsNone(result)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_reference_detail_404_error(self, mock_get):
        # Simulate 404 error
        mock_get.return_value.status_code = 404
        
        result = fetch_globalex_reference_detail('https://www.nyulawglobal.org/globalex/missing-page', 'reference')
        
        self.assertIsNone(result)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_references_network_error(self, mock_get):
        # Simulate network error when fetching main GlobaLex page
        mock_get.side_effect = Exception("DNS resolution failed")
        processed_ids = set()
        
        # Should handle error gracefully and not crash
        fetch_globalex_references(processed_ids)
        
        # No IDs should be processed due to network error
        self.assertEqual(len(processed_ids), 0)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_references_content_div_extraction(self, mock_get):
        # Test various content div extraction scenarios
        html = '''
        <html>
        <body>
            <div class="content">
                <h1>Zambia Legal Research Portal</h1>
                <p>Content in the content class div.</p>
            </div>
            <a href="/research/zambia-legal-guide.html">Zambia Legal Guide</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        processed_ids = set()
        
        with patch('zambian_law_scraper.fetch_globalex_reference_detail', return_value={
            'title': 'Legal Research Portal', 
            'content': 'Content in the content class div.', 
            'type': 'reference', 
            'source': 'url', 
            'related_files': [], 
            'citations': []
        }):
            fetch_globalex_references(processed_ids)
        
        self.assertGreater(len(processed_ids), 0)

    @patch('zambian_law_scraper.requests.get')
    def test_fetch_globalex_references_keyword_filtering(self, mock_get):
        # Test that only relevant links are processed based on keywords
        html = '''
        <html>
        <body>
            <a href="/page1.html">Zambia Legal Research</a>
            <a href="/page2.html">Legal Guide for Researchers</a>
            <a href="/page3.html">Law Database Access</a>
            <a href="/page4.html">Resources for Legal Studies</a>
            <a href="/page5.html">Unrelated Business Page</a>
            <a href="/page6.html">Sports News</a>
        </body>
        </html>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html
        processed_ids = set()
        
        with patch('zambian_law_scraper.fetch_globalex_reference_detail', return_value={
            'title': 'Legal Reference', 
            'content': 'Legal content.', 
            'type': 'reference', 
            'source': 'url', 
            'related_files': [], 
            'citations': []
        }) as mock_detail:
            fetch_globalex_references(processed_ids)
        
        # Should process links with relevant keywords, not the unrelated ones
        self.assertGreaterEqual(len(processed_ids), 4)  # At least the 4 relevant links
        self.assertLess(len(processed_ids), 6)  # Should not process all 6 links

if __name__ == '__main__':
    unittest.main()
