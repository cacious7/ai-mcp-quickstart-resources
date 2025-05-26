import os
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import zambian_law_scraper as zls

class TestZambianLawScraper(unittest.TestCase):
    def setUp(self):
        # Setup a temp lawdata dir
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

    def test_ensure_data_dir(self):
        shutil.rmtree(self.temp_dir)
        zls.ensure_data_dir()
        self.assertTrue(os.path.exists(self.temp_dir))

    def test_save_and_load_checkpoint(self):
        ids = {'a', 'b', 'c'}
        zls.save_checkpoint(ids)
        loaded = zls.load_checkpoint()
        self.assertEqual(ids, loaded)

    def test_law_id_from_url(self):
        url = 'https://zambialii.org/akn/zm/act/2017/2/eng@2017-04-13'
        law_id = zls.law_id_from_url(url)
        self.assertEqual(law_id, 'zm_act_2017_2_eng@2017-04-13')

    @patch('zambian_law_scraper.requests.get')
    @patch('builtins.print')
    def test_download_pdf_and_extract_text(self, mock_print, mock_get):
        # --- Test 1: Normal download when no duplicate exists ---
        # Mock SESSION.get instead of requests.get directly if the main code uses SESSION
        with patch('zambian_law_scraper.SESSION.get') as mock_session_get:
            mock_session_get.return_value.status_code = 200
            pdf_content_bytes = b'%PDF-1.4 test pdf content'
            # mock_session_get.return_value.content = pdf_content_bytes # For non-stream
            mock_session_get.return_value.iter_content = lambda chunk_size: [pdf_content_bytes] # For stream=True

            pdf_path = zls.download_pdf('http://example.com/test1.pdf', 'testlaw1', title='Test Law 1', year='2023')
            self.assertTrue(os.path.exists(pdf_path))
            self.assertEqual(pdf_path, os.path.join(self.temp_dir, 'testlaw1.pdf'))
            mock_print.assert_any_call(f"    Downloading PDF: http://example.com/test1.pdf")
            mock_session_get.assert_called_once_with('http://example.com/test1.pdf', headers=zls.HEADERS, timeout=30, stream=True)

            with open(pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Count 0 >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF')
            text = zls.extract_pdf_text(pdf_path)
            self.assertIsInstance(text, str)
            os.remove(pdf_path)
        
        mock_print.reset_mock()
        # mock_get.reset_mock() # mock_get is the outer patch, not used if SESSION.get is patched internally

        # --- Test 2: Skip download if law_id matches an existing file ---
        with patch('zambian_law_scraper.SESSION.get') as mock_session_get: # Patch session for this test too
            existing_pdf_path_law_id = os.path.join(self.temp_dir, 'testlaw2.pdf')
            with open(existing_pdf_path_law_id, 'wb') as f:
                f.write(b'dummy pdf content')
            pdf_path_skipped_law_id = zls.download_pdf('http://example.com/test2.pdf', 'testlaw2', title='Another Law', year='2024')
            self.assertEqual(pdf_path_skipped_law_id, existing_pdf_path_law_id)
            mock_print.assert_any_call(f"    PDF with ID 'testlaw2' or similar metadata likely already exists at: {existing_pdf_path_law_id}. Skipping download.")
            mock_session_get.assert_not_called() # Ensure SESSION.get was not called
            os.remove(existing_pdf_path_law_id)
        mock_print.reset_mock()

        # --- Test 3: Skip download if title and year match an existing file in a subfolder ---
        with patch('zambian_law_scraper.SESSION.get') as mock_session_get:
            law_subfolder = os.path.join(self.temp_dir, 'law_xyz_folder')
            os.makedirs(law_subfolder, exist_ok=True)
            existing_pdf_path_title_year = os.path.join(law_subfolder, 'Some_Law_Title_2023_abc.pdf')
            with open(existing_pdf_path_title_year, 'wb') as f:
                f.write(b'dummy pdf content for title year match')
            pdf_path_skipped_title_year = zls.download_pdf('http://example.com/test3.pdf', 'newlawid123', title='Some Law Title', year='2023')
            self.assertEqual(pdf_path_skipped_title_year, existing_pdf_path_title_year)
            mock_print.assert_any_call(f"    PDF with ID 'newlawid123' or similar metadata likely already exists at: {existing_pdf_path_title_year}. Skipping download.")
            mock_session_get.assert_not_called()
            shutil.rmtree(law_subfolder)
        mock_print.reset_mock()

        # --- Test 4: Download if title matches but year is different ---
        with patch('zambian_law_scraper.SESSION.get') as mock_session_get:
            mock_session_get.return_value.status_code = 200
            mock_session_get.return_value.iter_content = lambda chunk_size: [b'%PDF-1.4 test pdf content']
            pdf_path_diff_year = zls.download_pdf('http://example.com/test4.pdf', 'testlaw4', title='Test Law 1', year='2022')
            self.assertTrue(os.path.exists(pdf_path_diff_year))
            self.assertEqual(pdf_path_diff_year, os.path.join(self.temp_dir, 'testlaw4.pdf'))
            mock_print.assert_any_call("    Downloading PDF: http://example.com/test4.pdf")
            mock_session_get.assert_called_once_with('http://example.com/test4.pdf', headers=zls.HEADERS, timeout=30, stream=True)
            os.remove(pdf_path_diff_year)
        mock_print.reset_mock()

        # --- Test 5: Insufficient metadata message and download proceeds ---
        with patch('zambian_law_scraper.SESSION.get') as mock_session_get:
            mock_session_get.return_value.status_code = 200
            mock_session_get.return_value.iter_content = lambda chunk_size: [b'%PDF-1.4 test pdf content']
            pdf_path_no_meta = zls.download_pdf('http://example.com/test5.pdf', 'testlaw5_no_meta')
            self.assertTrue(os.path.exists(pdf_path_no_meta))
            mock_print.assert_any_call("    No metadata (title/year) provided for pre-download duplicate check for http://example.com/test5.pdf. Proceeding with download.")
            mock_print.assert_any_call("    Downloading PDF: http://example.com/test5.pdf")
            mock_session_get.assert_called_once_with('http://example.com/test5.pdf', headers=zls.HEADERS, timeout=30, stream=True)
            os.remove(pdf_path_no_meta)
        mock_print.reset_mock()

        # --- Test 6: Download fails (e.g., 404 error) ---
        with patch('zambian_law_scraper.SESSION.get') as mock_session_get:
            mock_session_get.return_value.status_code = 404
            mock_session_get.return_value.iter_content = lambda chunk_size: [] # Ensure iter_content is also mocked for failure cases
            pdf_path_failed = zls.download_pdf('http://example.com/nonexistent.pdf', 'testlaw_fail', title='Non Existent', year='2023')
            self.assertIsNone(pdf_path_failed)
            mock_print.assert_any_call("    Failed to download PDF: http://example.com/nonexistent.pdf (status 404)")
            mock_session_get.assert_called_once_with('http://example.com/nonexistent.pdf', headers=zls.HEADERS, timeout=30, stream=True)
        mock_print.reset_mock()

    def test_normalize_law_content_and_semantic_compare(self):
        text1 = 'Section 1. This is law. Section 2. More law.'
        text2 = 'Section 1. This is law. Section 2. More law.'
        norm1 = zls.normalize_law_content(text1)
        norm2 = zls.normalize_law_content(text2)
        self.assertEqual(norm1, norm2)
        self.assertTrue(zls.is_semantically_same_law(text1, text2))

    def test_save_law_json_and_duplicate_handling(self):
        # Save a law
        law = {
            'title': 'Test Law',
            'content': 'Section 1. Law.',
            'year': '2024',
            'language': 'en',
            'related_files': [],
            'citations': []
        }
        zls.save_law_json(law, 'testlaw')
        # Save a duplicate with newer year
        law2 = dict(law)
        law2['year'] = '2025'
        zls.save_law_json(law2, 'testlaw2')
        # Only one folder should exist (newer kept)
        folders = [f for f in os.listdir(self.temp_dir) if os.path.isdir(os.path.join(self.temp_dir, f))]
        self.assertIn('testlaw2', folders)  # Newer law folder exists

    @patch('zambian_law_scraper.requests.get') # This outer mock might be redundant if SESSION.get is always used and mocked internally
    @patch('zambian_law_scraper.download_pdf') # Add mock for download_pdf
    @patch('zambian_law_scraper.extract_pdf_text') # Add mock for extract_pdf_text
    @patch('os.path.exists') # Mock os.path.exists
    def test_fetch_zambialii_act_detail_html(self, mock_os_path_exists, mock_extract_text, mock_download_pdf, mock_requests_get):
        # Simulate a law detail page with HTML content
        with patch('zambian_law_scraper.SESSION.get') as mock_session_get: 
            html = '''<html lang="en"><h1>Test Law 2024</h1><div class="doc-content">Section 1. Law text.</div><a href="test.pdf">Test PDF</a></html>'''
            mock_session_get.return_value.status_code = 200
            mock_session_get.return_value.text = html
            
            # Configure mocks for download_pdf and extract_pdf_text
            mock_download_pdf.return_value = "/fake/path/to/downloaded.pdf"
            mock_extract_text.return_value = "Text from PDF"
            mock_os_path_exists.return_value = True # Ensure os.path.exists returns True for the fake PDF path

            # The function being tested is fetch_zambialii_act_detail, which is deprecated.
            # It calls fetch_zambialii_detail(url, "act")
            law = zls.fetch_zambialii_act_detail('http://example.com/law') 
            
            self.assertEqual(law['title'], 'Test Law 2024')
            self.assertEqual(law['content'], 'Text from PDF') 
            self.assertEqual(law['language'], 'en')
            mock_session_get.assert_called_once_with('http://example.com/law', timeout=20)
            mock_download_pdf.assert_called_once()
            # Verify the correct path was passed to os.path.exists and extract_pdf_text
            mock_os_path_exists.assert_any_call("/fake/path/to/downloaded.pdf")
            mock_extract_text.assert_called_once_with("/fake/path/to/downloaded.pdf")

    @patch('zambian_law_scraper.requests.get') # This outer mock might be redundant
    @patch('zambian_law_scraper.save_law_json') # Add mock for save_law_json
    @patch('zambian_law_scraper.save_checkpoint') # Add mock for save_checkpoint
    def test_fetch_zambialii_acts_pagination(self, mock_save_checkpoint, mock_save_law_json, mock_requests_get):
        with patch('zambian_law_scraper.SESSION.get') as mock_session_get, \
             patch('zambian_law_scraper.fetch_zambialii_detail') as mock_fetch_detail: # Mock the detail fetcher
            
            page1_html = '<a href="/akn/zm/act/2024/1/eng@2024-01-01">Law1</a>'
            page2_html = '<a href="/akn/zm/act/2024/2/eng@2024-01-02">Law2</a>'
            
            # Mock return value for fetch_zambialii_detail
            mock_fetch_detail.return_value = {
                'title': 'Mocked Law', 
                'content': 'Mocked Content', 
                'year': '2024', 
                'language': 'en', 
                'source': 'mock_url',
                'type': 'act',
                'related_files': [], 
                'citations': []
            }

            def side_effect_session_get(url, *args, **kwargs):
                resp = MagicMock()
                resp.status_code = 200
                if 'page=1' in url:
                    resp.text = page1_html
                elif 'page=2' in url:
                    resp.text = page2_html
                else:
                    resp.text = ''  # No law links for page > 2, causing the loop to stop
                return resp
            
            mock_session_get.side_effect = side_effect_session_get
            processed_ids = set()
            
            # The function fetch_zambialii_acts calls fetch_zambialii_detail internally.
            # We've mocked fetch_zambialii_detail above.
            acts = zls.fetch_zambialii_acts(processed_ids)
            
            self.assertEqual(len(acts), 2)
            self.assertEqual(mock_session_get.call_count, 3) # Page 1, Page 2, Page 3 (empty)
            self.assertEqual(mock_fetch_detail.call_count, 2) # Called for Law1 and Law2
            # Check if URLs passed to fetch_zambialii_detail are correct
            expected_detail_calls = [
                unittest.mock.call('https://zambialii.org/akn/zm/act/2024/1/eng@2024-01-01', "act"),
                unittest.mock.call('https://zambialii.org/akn/zm/act/2024/2/eng@2024-01-02', "act")
            ]
            mock_fetch_detail.assert_has_calls(expected_detail_calls, any_order=False)

if __name__ == '__main__':
    unittest.main()
