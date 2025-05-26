import os
import json
import shutil
import tempfile
import unittest
from PyPDF2 import PdfWriter
from test_law_accuracy import test_law_folder, aggregate_reports

class TestLawAccuracyWithRealPDF(unittest.TestCase):
    def setUp(self):
        # Create a temp lawdata structure
        self.temp_dir = tempfile.mkdtemp()
        self.law_folder = os.path.join(self.temp_dir, 'testlaw')
        os.makedirs(self.law_folder)
        # Minimal fake law
        self.law_json = {
            'title': 'Test Law',
            'content': 'This is the content of the law. Section 1. Section 2.',
            'year': '2024',
            'language': 'en',
            'related_files': [],
            'citations': []
        }
        with open(os.path.join(self.law_folder, 'testlaw.json'), 'w', encoding='utf-8') as f:
            json.dump(self.law_json, f)
        # Create a real PDF with the same text
        pdf_path = os.path.join(self.law_folder, 'testlaw.pdf')
        self.create_pdf_with_text(pdf_path, self.law_json['content'])

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def create_pdf_with_text(self, pdf_path, text):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.pdfmetrics import registerFont
        try:
            registerFont(TTFont('Arial', 'arial.ttf'))
        except:
            pass
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont('Helvetica', 12)
        width, height = letter
        lines = text.split('. ')
        y = height - inch
        for line in lines:
            c.drawString(inch, y, line.strip())
            y -= 14
        c.save()

    def test_law_folder_accuracy_real_pdf(self):
        report = test_law_folder(self.law_folder)
        self.assertEqual(report['status'], 'ok')
        self.assertGreater(report['accuracy'], 0.8)  # Allow for minor PDF extraction loss

    def test_aggregate_reports_real_pdf(self):
        # Add a second law folder
        law_folder2 = os.path.join(self.temp_dir, 'testlaw2')
        os.makedirs(law_folder2)
        with open(os.path.join(law_folder2, 'testlaw2.json'), 'w', encoding='utf-8') as f:
            json.dump(self.law_json, f)
        self.create_pdf_with_text(os.path.join(law_folder2, 'testlaw2.pdf'), self.law_json['content'])
        # Run per-folder and aggregate
        test_law_folder(self.law_folder)
        test_law_folder(law_folder2)
        summary = aggregate_reports(self.temp_dir)
        self.assertEqual(summary['laws_with_reports'], 2)
        self.assertGreater(summary['average_accuracy'], 0.8)

if __name__ == '__main__':
    unittest.main()
