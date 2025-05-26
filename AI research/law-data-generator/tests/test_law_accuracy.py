import os
import json
import re
from PyPDF2 import PdfReader

def extract_pdf_text(pdf_path):
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            text = "\n".join(page.extract_text() or '' for page in reader.pages)
        return text
    except Exception as e:
        return ""

def normalize_text(text):
    import string
    text = text.lower()
    # Remove all whitespace and newlines
    text = ''.join(text.split())
    # Remove all punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

def compare_texts(text1, text2):
    n1 = normalize_text(text1)
    n2 = normalize_text(text2)
    if not n1 or not n2:
        return 0.0
    # Compute character-level overlap (intersection over union)
    set1 = set(n1)
    set2 = set(n2)
    intersection = set1 & set2
    union = set1 | set2
    jaccard = len(intersection) / len(union) if union else 0.0
    # Also compute exact substring match ratio (min coverage)
    min_len = min(len(n1), len(n2))
    max_len = max(len(n1), len(n2))
    match_count = sum(1 for a, b in zip(n1, n2) if a == b)
    coverage = match_count / max_len if max_len else 0.0
    # Return the higher of the two as the accuracy
    return max(jaccard, coverage)

def test_law_folder(law_folder):
    report = {}
    json_file = None
    pdf_file = None
    for fname in os.listdir(law_folder):
        if fname.endswith('.json'):
            json_file = os.path.join(law_folder, fname)
        if fname.endswith('.pdf'):
            pdf_file = os.path.join(law_folder, fname)
    if not json_file or not pdf_file:
        report['status'] = 'missing_files'
        report['accuracy'] = 0.0
        return report
    with open(json_file, encoding='utf-8') as f:
        law = json.load(f)
    pdf_text = extract_pdf_text(pdf_file)
    content_text = law.get('content', '')
    accuracy = compare_texts(pdf_text, content_text)
    report['status'] = 'ok'
    report['accuracy'] = accuracy
    report['law_title'] = law.get('title')
    report['law_id'] = os.path.basename(law_folder)
    report['pdf_file'] = os.path.basename(pdf_file)
    report['json_file'] = os.path.basename(json_file)
    # Save per-folder report
    with open(os.path.join(law_folder, 'accuracy_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    # Also save the accuracy score in a plain text file for easy access
    with open(os.path.join(law_folder, 'accuracy_score.txt'), 'w', encoding='utf-8') as f:
        f.write(f"{accuracy:.4f}\n")
    return report

def aggregate_reports(data_dir):
    all_reports = []
    for folder in os.listdir(data_dir):
        law_folder = os.path.join(data_dir, folder)
        if os.path.isdir(law_folder):
            report_path = os.path.join(law_folder, 'accuracy_report.json')
            if os.path.exists(report_path):
                with open(report_path, encoding='utf-8') as f:
                    all_reports.append(json.load(f))
    # Aggregate
    total = len(all_reports)
    ok = sum(1 for r in all_reports if r['status'] == 'ok')
    avg_accuracy = sum(r['accuracy'] for r in all_reports if r['status'] == 'ok') / ok if ok else 0.0
    summary = {
        'total_laws': total,
        'laws_with_reports': ok,
        'average_accuracy': avg_accuracy,
        'details': all_reports
    }
    # Save global report as JSON
    with open(os.path.join(data_dir, 'aggregate_accuracy_report.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    # Also save the global average accuracy as a plain text file
    with open(os.path.join(data_dir, 'aggregate_accuracy_score.txt'), 'w', encoding='utf-8') as f:
        f.write(f"{avg_accuracy:.4f}\n")
    return summary

def main():
    data_dir = 'lawdata'
    for folder in os.listdir(data_dir):
        law_folder = os.path.join(data_dir, folder)
        if os.path.isdir(law_folder):
            test_law_folder(law_folder)
    summary = aggregate_reports(data_dir)
    print(f"Tested {summary['laws_with_reports']} out of {summary['total_laws']} laws.")
    print(f"Average PDF-to-content accuracy: {summary['average_accuracy']:.2%}")

if __name__ == '__main__':
    main()
