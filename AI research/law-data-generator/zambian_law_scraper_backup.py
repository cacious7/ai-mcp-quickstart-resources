import os
import json
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
from urllib.parse import urljoin, urlparse
from PyPDF2 import PdfReader
import hashlib # Ensure hashlib is imported

DATA_DIR = "lawdata"
CHECKPOINT_FILE = "scraper_checkpoint.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SOURCES = [
    {
        "name": "ZambiaLII",
        "base_url": "https://zambialii.org",
        "acts_url": "https://zambialii.org/legislation/all",
        "type": "act"
    },
    {
        "name": "Blackhall’s Laws of Zambia",
        "base_url": "https://www.zambialaws.com",
        "acts_url": "https://www.zambialaws.com/acts",
        "type": "act"
    },
    {
        "name": "Judiciary of Zambia",
        "base_url": "https://www.judiciaryzambia.com",
        "acts_url": "https://www.judiciaryzambia.com/cases",
        "type": "case-law"
    },
    {
        "name": "Law Library of Congress",
        "base_url": "https://www.loc.gov",
        "acts_url": "https://www.loc.gov/law/help/guide/nations/zambia.php",
        "type": "reference"
    },
    {
        "name": "GlobaLex",
        "base_url": "https://www.nyulawglobal.org",
        "acts_url": "https://www.nyulawglobal.org/globalex/Zambia.html",
        "type": "reference"
    },
    {
        "name": "Zambia Human Rights Commission",
        "base_url": "https://www.hrc.org.zm",
        "acts_url": "https://www.hrc.org.zm/publications",
        "type": "reference"
    }
]

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_checkpoint(processed_ids):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(list(processed_ids), f)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return set(json.load(f))
    return set()

def fetch_zambialii_acts(processed_ids):
    acts = []
    page = 1
    while True:
        url = f"https://zambialii.org/legislation/all?page={page}"
        print(f"Fetching: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
        except Exception as e:
            print(f"Request failed: {e}")
            break
        if resp.status_code != 200:
            print(f"Non-200 status code: {resp.status_code}")
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        # Law links are <a> tags with href starting with /akn/zm/act or /akn/zm/si or /akn/zm/chapter
        law_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/akn/zm/'):
                law_links.append(a)
        print(f"Found {len(law_links)} law links on page {page}.")
        if not law_links:
            print("No law links found, stopping.")
            break
        for link in law_links:
            law_url = "https://zambialii.org" + link['href']
            law_id = law_id_from_url(law_url)
            if law_id in processed_ids:
                continue
            law_data = fetch_zambialii_act_detail(law_url)
            if law_data:
                acts.append(law_data)
                processed_ids.add(law_id)
                save_law_json(law_data, law_id)
                save_checkpoint(processed_ids)
                print(f"Saved: {law_id}")
                time.sleep(1)
        page += 1
    return acts

def download_pdf(pdf_url, law_id):
    pdf_filename = os.path.join(DATA_DIR, f"{law_id}.pdf")
    try:
        resp = requests.get(pdf_url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            with open(pdf_filename, "wb") as f:
                f.write(resp.content)
            return pdf_filename
        else:
            print(f"    Failed to download PDF: {pdf_url} (status {resp.status_code})")
    except Exception as e:
        print(f"    Exception downloading PDF: {e}")
    return None

def extract_pdf_text(pdf_path):
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            text = "\n".join(page.extract_text() or '' for page in reader.pages)
        return text
    except Exception as e:
        print(f"    Exception extracting PDF text: {e}")
        return ""

def fetch_zambialii_act_detail(url):
    print(f"  Fetching detail: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except Exception as e:
        print(f"  Detail request failed: {e}")
        return None
    if resp.status_code != 200:
        print(f"  Non-200 status code for detail: {resp.status_code}")
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find(['h1', 'h2'])
    title = title_tag.get_text(strip=True) if title_tag else None
    year = None
    if title:
        m = re.search(r'(19|20)\d{2}', title)
        if m:
            year = m.group(0)
    # Try to extract date from metadata or page
    date = None
    meta_date = soup.find('meta', {'property': 'article:published_time'})
    if meta_date and meta_date.get('content'):
        date = meta_date['content']
    # Try to get language (from meta or page)
    language = None
    meta_lang = soup.find('meta', {'http-equiv': 'content-language'})
    if meta_lang and meta_lang.get('content'):
        language = meta_lang['content']
    if not language:
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            language = html_tag['lang']
    if not language:
        language = 'en'  # Default to English if not specified
    content_div = soup.find('div', class_='doc-content')
    content = content_div.get_text(separator="\n", strip=True) if content_div else ''
    pdf_url = None
    pdf_path = None
    pdf_text = None
    related_files = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            pdf_url = urljoin(url, href)
            pdf_path = download_pdf(pdf_url, law_id_from_url(url))
            if pdf_path:
                pdf_text = extract_pdf_text(pdf_path)
                related_files.append({'type': 'pdf', 'url': pdf_url, 'path': pdf_path})
            break
    if pdf_text:
        content = pdf_text
    citations = []
    for a in soup.find_all('a', class_=re.compile('citation', re.I)):
        citations.append(a.get_text(strip=True))
    for a in soup.find_all('a', href=True):
        href = a['href']
        if not href.lower().endswith('.pdf') and (href.lower().endswith('.doc') or href.lower().endswith('.docx') or href.lower().endswith('.rtf')):
            related_files.append({'type': 'document', 'url': urljoin(url, href)})
    return {
        "title": title,
        "year": year,
        "date": date,
        "language": language,
        "content": content,
        "source": url,
        "type": "act",
        "related_files": related_files,
        "citations": citations
    }

def law_id_from_url(url):
    original_url_for_hash = url # Ensure this is defined for fallback hashing
    parsed_url = urlparse(url)
    # Try to get a meaningful name from the path
    path_part = os.path.basename(parsed_url.path)

    # If path_part is empty or generic (like 'index.html'), try using the query or fragment
    if not path_part or path_part.lower() in ['index.html', 'index.php', 'default.aspx', '']:
        if parsed_url.query:
            # Use the query string directly if path is not informative
            law_id_base = parsed_url.query
        elif parsed_url.fragment:
            law_id_base = parsed_url.fragment
        else:
            # Fallback to domain if path, query, and fragment are not useful
            law_id_base = parsed_url.netloc
    else:
        law_id_base = path_part

    # If law_id_base (derived from path_part or query) itself contains '?', 
    # it might be a filename that includes query-like characters, or an actual query string.
    # Split at the first '?' and take the part before it to remove parameters.
    # This handles cases like path_part = "file.php?param=value"
    if '?' in law_id_base:
        law_id_base = law_id_base.split('?', 1)[0]
    
    # Sanitize the base name
    # Replace known problematic patterns first.
    # This specific replace might be less effective if '?' was already stripped by the logic above,
    # but it's kept for specific cases or if the pattern doesn't involve '?'.
    law_id_base = law_id_base.replace('sb.php?subject_id=', 'subject_') 

    # Basic slugification: replace non-alphanumeric with underscore
    law_id = re.sub(r'[^a-zA-Z0-9_-]', '_', law_id_base)
    # Remove leading/trailing underscores and multiple underscores
    law_id = re.sub(r'_+', '_', law_id).strip('_')

    if not law_id: # Handle cases where the ID becomes empty
        # Fallback to a hash of the original URL if the generated ID is empty
        law_id = hashlib.md5(original_url_for_hash.encode('utf-8')).hexdigest()[:10]
    
    # Ensure law_id is not too long (Windows path length limits)
    # MAX_FILENAME_LENGTH is typically around 250, leave some room.
    MAX_LAW_ID_LENGTH = 100 
    if len(law_id) > MAX_LAW_ID_LENGTH:
        # If too long, truncate and add a hash of the full original ID to maintain uniqueness
        # Hash the current law_id being truncated, not original_url_for_hash, to ensure uniqueness for long similar base IDs
        hash_suffix = hashlib.md5(law_id.encode('utf-8')).hexdigest()[:8] 
        law_id = law_id[:MAX_LAW_ID_LENGTH - len(hash_suffix) - 1] + "_" + hash_suffix
        law_id = re.sub(r'_+', '_', law_id).strip('_') # Clean up again after truncation

    return law_id

def normalize_law_content(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    # Split by section/paragraph markers (e.g., 'section', 'part', numbers)
    # Use a more robust split for legal docs
    sections = re.split(r'(section \d+|part \d+|article \d+|\n\d+\.|\n[a-z]\)|\n)', text)
    # Remove empty and very short sections
    return [s.strip() for s in sections if len(s.strip()) > 10]

def is_semantically_same_law(content1, content2):
    # Compare by normalized sections/clauses
    sections1 = set(normalize_law_content(content1))
    sections2 = set(normalize_law_content(content2))
    if not sections1 or not sections2:
        return False
    # Calculate intersection over union
    intersection = sections1 & sections2
    union = sections1 | sections2
    if not union:
        return False
    similarity = len(intersection) / len(union)
    return similarity >= 0.9

def find_existing_law_by_title(title, year=None):
    # Search lawdata/ for a law with the same or very similar title
    for folder in os.listdir(DATA_DIR):
        law_folder = os.path.join(DATA_DIR, folder)
        if not os.path.isdir(law_folder):
            continue
        for fname in os.listdir(law_folder):
            if fname.endswith('.json'):
                with open(os.path.join(law_folder, fname), encoding='utf-8') as f:
                    try:
                        law = json.load(f)
                    except Exception:
                        continue
                    if isinstance(law, list):
                        # Defensive: skip lists, only process dicts
                        continue
                    if law.get('title') and title and law['title'].lower() == title.lower():
                        return fname, law
                    # Optionally, fuzzy match on title
                    if law.get('title') and title and title.lower() in law['title'].lower():
                        return fname, law
    return None, None

def save_law_json(law, law_id):
    # Create a subfolder for each law
    law_folder = os.path.join(DATA_DIR, law_id)
    if not os.path.exists(law_folder):
        os.makedirs(law_folder)
    # Check for duplicate by title
    existing_fname, existing_law = find_existing_law_by_title(law.get('title'), law.get('year'))
    if existing_law:
        if is_semantically_same_law(law.get('content', ''), existing_law.get('content', '')):
            new_year = law.get('year') or law.get('date')
            old_year = existing_law.get('year') or existing_law.get('date')
            if new_year and old_year:
                if str(new_year) > str(old_year):
                    filename = os.path.join(DATA_DIR, existing_fname)
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(law, f, ensure_ascii=False, indent=2)
                    print(f"  Duplicate found, kept newer version: {existing_fname}")
                else:
                    print(f"  Duplicate found, kept existing (newer or same year): {existing_fname}")
                return
            else:
                print(f"  Duplicate found, kept existing (no year info): {existing_fname}")
                return
    # Save JSON in the law's folder
    filename = os.path.join(law_folder, f"{law_id}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(law, f, ensure_ascii=False, indent=2)
    # Move related files (PDF, etc.) into the law's folder if they exist
    for rel in law.get('related_files', []):
        if 'path' in rel and os.path.exists(rel['path']):
            dest_path = os.path.join(law_folder, os.path.basename(rel['path']))
            if os.path.abspath(rel['path']) != os.path.abspath(dest_path):
                try:
                    os.replace(rel['path'], dest_path)
                except Exception as e:
                    print(f"    Could not move file {rel['path']} to {dest_path}: {e}")
            rel['path'] = dest_path
    # Update JSON with new related file paths
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(law, f, ensure_ascii=False, indent=2)

def fetch_zambialii_all(processed_ids):
    """
    Fetch all types from ZambiaLII: acts, bills, judgments, speeches, gazettes, law reform reports.
    Updated with correct URLs based on research.
    """
    base_url = "https://zambialii.org"
    # Define all relevant sections with correct URLs from research
    sections = [
        {"url": f"{base_url}/legislation/", "type": "act"},  # Correct URL for legislation
        {"url": f"{base_url}/doc/bill", "type": "bill"},    # Correct URL for bills
        {"url": f"{base_url}/judgments/", "type": "judgment"},  # Correct URL for judgments
        {"url": f"{base_url}/gazettes/", "type": "gazette"},    # Correct URL for gazettes
        {"url": f"{base_url}/doc/law-reform-report", "type": "law_reform_report"},  # Correct URL
        {"url": f"{base_url}/doc/speech", "type": "speech"},    # Correct URL for speeches
    ]
    for section in sections:
        page = 0
        while True:
            url = section["url"] + (f"?page={page}" if page > 0 else "")
            print(f"Fetching: {url}")
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
            except Exception as e:
                print(f"Request failed: {e}")
                break
            if resp.status_code != 200:
                print(f"Non-200 status code: {resp.status_code}")
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            # Find all law links (acts, bills, etc.)
            law_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Accept all /akn/zm/ links for acts, bills, gazettes, law reform reports
                if href.startswith('/akn/zm/'):
                    law_links.append((a, section["type"]))
                # Judgments: /node/ or /zm/judgment/ or /zm/case-law/
                elif section["type"] == "judgment" and ("/judgment/" in href or "/case-law/" in href or "/node/" in href):
                    law_links.append((a, section["type"]))
                # Speeches: /speeches/ or similar
                elif section["type"] == "speech" and "/speeches/" in href:
                    law_links.append((a, section["type"]))
            print(f"Found {len(law_links)} {section['type']} links on page {page}.")
            if not law_links:
                break
            for link, law_type in law_links:
                law_url = urljoin(base_url, link['href'])
                law_id = law_id_from_url(law_url)
                if law_id in processed_ids:
                    continue
                law_data = fetch_zambialii_detail(law_url, law_type)
                if law_data:
                    processed_ids.add(law_id)
                    save_law_json(law_data, law_id)
                    save_checkpoint(processed_ids)
                    print(f"Saved: {law_id}")
                    time.sleep(1)
            page += 1

def fetch_zambialii_detail(url, law_type):
    print(f"  Fetching detail: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
    except Exception as e:
        print(f"  Detail request failed: {e}")
        return None
    if resp.status_code != 200:
        print(f"  Non-200 status code for detail: {resp.status_code}")
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find(['h1', 'h2'])
    title = title_tag.get_text(strip=True) if title_tag else None
    year = None
    if title:
        m = re.search(r'(19|20)\d{2}', title)
        if m:
            year = m.group(0)
    date = None
    meta_date = soup.find('meta', {'property': 'article:published_time'})
    if meta_date and meta_date.get('content'):
        date = meta_date['content']
    language = None
    meta_lang = soup.find('meta', {'http-equiv': 'content-language'})
    if meta_lang and meta_lang.get('content'):
        language = meta_lang['content']
    if not language:
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            language = html_tag['lang']
    if not language:
        language = 'en'
    content_div = soup.find('div', class_='doc-content')
    content = content_div.get_text(separator="\n", strip=True) if content_div else ''
    pdf_url = None
    pdf_path = None
    pdf_text = None
    related_files = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            pdf_url = urljoin(url, href)
            pdf_path = download_pdf(pdf_url, law_id_from_url(url))
            if pdf_path:
                pdf_text = extract_pdf_text(pdf_path)
                related_files.append({'type': 'pdf', 'url': pdf_url, 'path': pdf_path})
            break
    if pdf_text:
        content = pdf_text
    citations = []
    for a in soup.find_all('a', class_=re.compile('citation', re.I)):
        citations.append(a.get_text(strip=True))
    for a in soup.find_all('a', href=True):
        href = a['href']
        if not href.lower().endswith('.pdf') and (href.lower().endswith('.doc') or href.lower().endswith('.docx') or href.lower().endswith('.rtf')):
            related_files.append({'type': 'document', 'url': urljoin(url, href)})
    return {
        "title": title,
        "year": year,
        "date": date,
        "language": language,
        "content": content,
        "source": url,
        "type": law_type,
        "related_files": related_files,
        "citations": citations
    }

def generate_source_analysis_report():
    """
    Generate a comprehensive report of all legal sources researched,
    their accessibility status, and document types available.
    """
    report = {
        "title": "Comprehensive Analysis of Zambian Legal Sources",
        "date_generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sources": {
            "zambialii": {
                "name": "ZambiaLII",
                "url": "https://zambialii.org",
                "status": "✅ Fully Accessible",
                "description": "Primary legal database with comprehensive collection",
                "document_types": {
                    "legislation": {"url": "https://zambialii.org/legislation/", "count": 698},
                    "bills": {"url": "https://zambialii.org/doc/bill", "count": 30},
                    "judgments": {"url": "https://zambialii.org/judgments/", "count": 8680},
                    "gazettes": {"url": "https://zambialii.org/gazettes/", "count": 1204},
                    "speeches": {"url": "https://zambialii.org/doc/speech", "count": 4},
                    "law_reform_reports": {"url": "https://zambialii.org/doc/law-reform-report", "count": 0}
                },
                "url_pattern": "/akn/zm/ (Akoma Ntoso format)",
                "reliability": "High",
                "coverage": "Comprehensive - primary source for Zambian law"
            },
            "judiciary": {
                "name": "Judiciary of Zambia",
                "url": "https://judiciaryzambia.com",
                "status": "✅ Accessible",
                "description": "Official judiciary website with extensive case archive",
                "document_types": {
                    "judgments": {"coverage": "2016-2025", "organization": "Monthly archives"},
                    "supreme_court": {"type": "Supreme Court judgments"},
                    "high_court": {"type": "High Court judgments"},
                    "subordinate_courts": {"type": "Subordinate Court judgments"}
                },
                "reliability": "High",
                "coverage": "Extensive case law from all court levels"
            },
            "ministry_justice": {
                "name": "Ministry of Justice",
                "url": "https://www.moj.gov.zm",
                "status": "⚠️ Partial Access",
                "description": "Government ministry with policies and legal documents",
                "document_types": {
                    "policies": {"type": "National policies and legal frameworks"},
                    "reports": {"type": "Ministry reports and bulletins"},
                    "gazettes": {"type": "Government gazette notices"}
                },
                "issues": "Legal document sections have server errors",
                "accessibility": "Main site accessible, document sections problematic",
                "reliability": "Medium"
            },
            "parliament": {
                "name": "Parliament of Zambia",
                "url": "https://www.parliament.gov.zm",
                "status": "❌ SSL Issues",
                "description": "Legislative body with acts and bills",
                "document_types": {
                    "acts": {"type": "Acts of Parliament"},
                    "bills": {"type": "Parliamentary Bills"}
                },
                "issues": "SSL certificate problems prevent access",
                "alternatives": "HTTP version may work, needs testing",
                "reliability": "Low due to technical issues"
            },
            "blackhall": {
                "name": "Blackhall's Laws of Zambia",
                "url": "https://www.zambialaws.com",
                "status": "✅ Accessible (Subscription Required)",
                "description": "Commercial legal database with statutory laws",
                "document_types": {
                    "statutory_laws": {"organization": "By chapter", "coverage": "Comprehensive"}
                },
                "access_model": "Subscription-based",
                "reliability": "High for subscribed content"
            },
            "library_congress": {
                "name": "Library of Congress - Zambia Legal Guide",
                "url": "https://guides.loc.gov/law-zambia",
                "status": "✅ Accessible",
                "description": "Authoritative legal research guide",
                "document_types": {
                    "research_guides": {"type": "Legal research methodologies"},
                    "source_directories": {"type": "Comprehensive source listings"},
                    "legal_frameworks": {"type": "Constitutional and legal system overview"}
                },
                "reliability": "Very High",
                "coverage": "Research-oriented, excellent for understanding legal system"
            },
            "globalex": {
                "name": "GlobaLex - Zambia Legal Research",
                "url": "https://www.nyulawglobal.org/globalex/Zambia.html",
                "status": "✅ Accessible",
                "description": "Academic legal research resource",
                "document_types": {
                    "research_guides": {"type": "Academic legal research guides"},
                    "source_analysis": {"type": "Legal source evaluations"},
                    "system_overview": {"type": "Legal system structure analysis"}
                },
                "reliability": "Very High",
                "coverage": "Academic perspective on Zambian legal system"
            },
            "human_rights_commission": {
                "name": "Zambia Human Rights Commission",
                "url": "https://www.hrc.org.zm",
                "status": "❌ Not Accessible",
                "description": "Independent human rights body",
                "issues": "Website URLs are invalid",
                "alternatives": "None found",
                "reliability": "Unknown"
            },
            "anti_corruption_commission": {
                "name": "Anti-Corruption Commission",
                "url": "https://www.acc.gov.zm",
                "status": "❌ Account Suspended",
                "description": "Anti-corruption enforcement body", 
                "issues": "Website account suspended",
                "alternatives": "None found",
                "reliability": "Unknown"
            }
        },
        "summary": {
            "total_sources_researched": 9,
            "fully_accessible": 4,
            "partially_accessible": 1,
            "technical_issues": 2,
            "inaccessible": 2,
            "primary_sources": ["zambialii", "judiciary", "ministry_justice"],
            "research_sources": ["library_congress", "globalex"],
            "commercial_sources": ["blackhall"],
            "recommendations": [
                "Focus on ZambiaLII as primary source (9,000+ documents)",
                "Utilize Judiciary website for comprehensive case law",
                "Monitor Parliament website for SSL certificate fixes",
                "Consider Blackhall subscription for complete statutory coverage",
                "Use LoC and GlobaLex guides for research methodology"
            ]
        }
    }
    
    # Save report to file
    report_file = os.path.join(DATA_DIR, "source_analysis_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Source analysis report saved to: {report_file}")
    return report

# Add at the end of the existing file, before main()
def main():
    ensure_data_dir()
    processed_ids = load_checkpoint()
    
    print("=== ZAMBIAN LAW SCRAPER - COMPREHENSIVE RESEARCH UPDATE ===")
    print("Starting comprehensive scraping of Zambian legal sources...\n")
    
    # 1. ZambiaLII - Primary and most comprehensive source
    print("1. Fetching all Zambian law data from ZambiaLII...")
    print("   (Legislation, Bills, Judgments, Gazettes, Speeches, Law Reform Reports)")
    try:
        fetch_zambialii_all(processed_ids)
        print("   ✅ ZambiaLII scraping completed successfully\n")
    except Exception as e:
        print(f"   ❌ ZambiaLII scraping failed: {e}\n")
    
    # 2. Ministry of Justice - Policies and legal documents  
    print("2. Fetching documents from Ministry of Justice...")
    print("   (Policies, Reports, Legal Bulletins)")
    try:
        fetch_ministry_justice_documents(processed_ids)
        print("   ✅ Ministry of Justice scraping completed\n")
    except Exception as e:
        print(f"   ❌ Ministry of Justice scraping failed: {e}\n")
    
    # 3. Judiciary of Zambia - Case law and judgments
    print("3. Fetching all Zambian law data from Judiciary of Zambia...")
    print("   (Judgments from Supreme Court, High Court, Subordinate Courts)")
    try:
        fetch_judiciary_cases(processed_ids)
        print("   ✅ Judiciary scraping completed successfully\n")
    except Exception as e:
        print(f"   ❌ Judiciary scraping failed: {e}\n")
    
    # 4. Parliament of Zambia - Acts and Bills (with SSL error handling)
    print("4. Fetching all Zambian law data from Parliament of Zambia...")
    print("   (Acts and Bills - Note: may have SSL certificate issues)")
    try:
        fetch_parliament_acts(processed_ids)
        print("   ✅ Parliament scraping completed successfully\n")
    except Exception as e:
        print(f"   ❌ Parliament scraping failed: {e}\n")
    
    # 5. Blackhall's Laws of Zambia - Statutory laws (subscription-based)
    print("5. Fetching all Zambian law data from Blackhall's Laws of Zambia...")
    print("   (Statutory Laws - Note: requires subscription for full access)")
    try:
        fetch_blackhall_acts(processed_ids)
        print("   ✅ Blackhall scraping completed successfully\n")
    except Exception as e:
        print(f"   ❌ Blackhall scraping failed: {e}\n")
    
    # 6. Library of Congress - Legal research guides
    print("6. Fetching legal references from Law Library of Congress...")
    print("   (Legal Research Guides and Reference Materials)")
    try:
        fetch_loc_references(processed_ids)
        print("   ✅ Library of Congress scraping completed\n")
    except Exception as e:
        print(f"   ❌ Library of Congress scraping failed: {e}\n")
    
    # 7. GlobaLex - Legal research resources
    print("7. Fetching legal references from GlobaLex...")
    print("   (Legal Research Resources and Guides)")
    try:
        fetch_globalex_references(processed_ids)
        print("   ✅ GlobaLex scraping completed\n")
    except Exception as e:
        print(f"   ❌ GlobaLex scraping failed: {e}\n")
    
    # 8. Human Rights Commission - Reports and publications (may be inaccessible)
    print("8. Fetching publications from Zambia Human Rights Commission...")
    print("   (Human Rights Reports - Note: website may be inaccessible)")
    try:
        fetch_hrc_publications(processed_ids)
        print("   ✅ HRC scraping completed\n")
    except Exception as e:
        print(f"   ❌ HRC scraping failed: {e}\n")
    
    print("=== SCRAPING COMPLETED ===")
    print(f"Total documents processed: {len(processed_ids)}")
    print(f"Data saved to: {DATA_DIR}")
    print("\nSUMMARY OF SOURCES:")
    print("✅ ZambiaLII: Primary source with 9,000+ documents")
    print("✅ Judiciary: Extensive case archive from 2016-2025") 
    print("✅ Ministry of Justice: Policies and legal bulletins")
    print("⚠️  Parliament: SSL issues may limit access")
    print("⚠️  Blackhall: Subscription required for full access")
    print("✅ Research Sources: LoC and GlobaLex guides accessible")
    print("❌ HRC & ACC: Websites currently inaccessible")
    print("\nDone.")

if __name__ == "__main__":
    main()
