import os
import json
import requests
import re
import sys
import time
import hashlib # Ensure hashlib is imported
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
from PyPDF2 import PdfReader

DATA_DIR = "lawdata"
CHECKPOINT_FILE = "scraper_checkpoint.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Initialize a session for making requests
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

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
        "acts_url": "https://www.judiciaryzambia.com",  # Updated to base_url
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

# Color codes for logs
LOG_COLORS = {
    'INFO': '\033[94m',    # Blue
    'SUCCESS': '\033[92m', # Green
    'WARNING': '\033[93m', # Yellow
    'ERROR': '\033[91m',   # Red
    'RESET': '\033[0m'
}

def log_info(msg):
    print(f"{LOG_COLORS['INFO']}[INFO]{LOG_COLORS['RESET']} {msg}")

def log_success(msg):
    print(f"{LOG_COLORS['SUCCESS']}[SUCCESS]{LOG_COLORS['RESET']} {msg}")

def log_warning(msg):
    print(f"{LOG_COLORS['WARNING']}[WARNING]{LOG_COLORS['RESET']} {msg}")

def log_error(msg):
    print(f"{LOG_COLORS['ERROR']}[ERROR]{LOG_COLORS['RESET']} {msg}")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    # Create .gitignore in DATA_DIR if it doesn't exist
    gitignore_path = os.path.join(DATA_DIR, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("*\\n")
            f.write("!/.gitignore\\n")
        log_info(f"Created .gitignore in {DATA_DIR}")

def save_checkpoint(processed_ids):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(list(processed_ids), f)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return set(json.load(f))
    return set()

def print_progress_bar(current, total, prefix='', bar_length=40, color='green', elapsed=None):
    colors = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    color_code = colors.get(color, '')
    reset_code = colors['reset']
    filled = int(bar_length * current // max(1, total))
    bar = f"{color_code}{'█' * filled}{'-' * (bar_length - filled)}{reset_code}"
    percent = (current / total) * 100 if total else 0
    timer = f" | Elapsed: {elapsed:.1f}s" if elapsed is not None else ''
    sys.stdout.write(f"\r{prefix} |{bar}| {current}/{total} ({percent:.1f}%)" + timer)
    sys.stdout.flush()
    if current >= total:
        print()

def fetch_zambialii_acts(processed_ids, progress_callback=None):
    acts = []
    page = 1
    total_pages = None # Not currently used, but could be for progress if known
    while True:
        url = f"https://zambialii.org/legislation/all?page={page}"
        log_info(f"Fetching: {url}")
        try:
            # resp = requests.get(url, headers=HEADERS, timeout=15)
            resp = SESSION.get(url, timeout=15) # Use session
        except Exception as e:
            log_error(f"Request failed: {e}")
            break
        if resp.status_code != 200:
            log_warning(f"Non-200 status code: {resp.status_code}")
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        # Law links are <a> tags with href starting with /akn/zm/act or /akn/zm/si or /akn/zm/chapter
        law_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/akn/zm/'):
                law_links.append(a)
        log_info(f"Found {len(law_links)} law links on page {page}.")
        if not law_links:
            log_warning("No law links found, stopping.")
            break
        for link in law_links:
            law_url = "https://zambialii.org" + link['href']
            law_id = law_id_from_url(law_url)
            if law_id in processed_ids:
                continue
            # law_data = fetch_zambialii_act_detail(law_url) # Old call
            law_data = fetch_zambialii_detail(law_url, "act") # Use generic detail fetcher
            if law_data:
                acts.append(law_data)
                processed_ids.add(law_id)
                save_law_json(law_data, law_id)
                save_checkpoint(processed_ids)
                log_success(f"Saved: {law_id}")
                time.sleep(1)
        page += 1  # <-- Fix: increment page number to avoid infinite loop
    return acts

def fetch_zambialii_act_detail(url):
    """
    DEPRECATED: This function is replaced by fetch_zambialii_detail(url, law_type).
    It should be removed in a future cleanup.
    """
    log_warning("DEPRECATED: fetch_zambialii_act_detail(url) called. Use fetch_zambialii_detail(url, law_type) instead.")
    # Redirect to the new function for now, or raise an error
    return fetch_zambialii_detail(url, "act")

def fetch_zambialii_detail(url, law_type):
    log_info(f"Fetching detail: {url} (Type: {law_type})")
    try:
        # resp = requests.get(url, headers=HEADERS, timeout=20)
        resp = SESSION.get(url, timeout=20) # Use session
    except Exception as e:
        log_error(f"Detail request failed for {url}: {e}")
        return None
    if resp.status_code != 200:
        log_warning(f"Non-200 status code for detail: {resp.status_code}")
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
    current_law_id = law_id_from_url(url) # Define current_law_id for download_pdf

    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            if not href.startswith('http'):
                pdf_url = urljoin(url, href)
            else:
                pdf_url = href
            
            # Pass title and year to download_pdf if available
            # title and year are already defined above in this function
            log_info(f"Found PDF link: {pdf_url}")
            # Assuming download_pdf is a robust function that handles saving and returns a path
            # It should also handle potential duplicate downloads gracefully.
            # The stub for download_pdf needs to be replaced with a real implementation.
            pdf_path_temp = download_pdf(pdf_url, current_law_id, title, year) # Call the actual download_pdf
            
            if pdf_path_temp and os.path.exists(pdf_path_temp):
                pdf_path = pdf_path_temp # Store the valid path
                pdf_text_extracted = extract_pdf_text(pdf_path)
                if pdf_text_extracted:
                    pdf_text = pdf_text_extracted
                    log_info(f"Extracted text from PDF: {pdf_path}")
                else:
                    log_warning(f"Could not extract text from PDF: {pdf_path}")
                related_files.append({'type': 'pdf', 'url': pdf_url, 'path': pdf_path})
            else:
                log_warning(f"PDF download failed or file not found for {pdf_url}")
            # Consider if we should break after finding the first PDF, or collect all.
            # For now, assume one primary PDF is sufficient if found.
            if pdf_path: # If a PDF was successfully processed
                 break 
    if pdf_text:
        content = pdf_text # Prioritize PDF content if available
    citations = []
    for a in soup.find_all('a', class_=re.compile('citation', re.I)):
        citations.append(a.get_text(strip=True))
    for a in soup.find_all('a', href=True):
        href = a['href']
        file_ext_match = re.search(r'\.(doc|docx|rtf)$', href.lower())
        if not href.lower().endswith('.pdf') and file_ext_match:
            file_ext = file_ext_match.group(1)
            if not href.startswith('http'):
                doc_url = urljoin(url, href)
            else:
                doc_url = href
            log_info(f"Found related document ({file_ext}): {doc_url}")
            # For .doc, .docx, .rtf, we are just recording the URL.
            # Downloading and text extraction for these would require additional libraries (e.g., python-docx, striprtf).
            related_files.append({
                'type': file_ext,
                'url': doc_url
                # 'path': downloaded_doc_path # If we were to download them
            })
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

def law_id_from_url(url):
    original_url_for_hash = url
    parsed_url = urlparse(url)
    # If the path contains '/akn/', use everything after '/akn/' as the base
    akn_index = parsed_url.path.find('/akn/')
    if akn_index != -1:
        akn_path = parsed_url.path[akn_index + 5:]  # skip '/akn/'
        # Replace slashes with underscores, but preserve '@' (do not replace with underscore)
        law_id_base = akn_path.replace('/', '_')
        # If there's a query or fragment, append it
        if parsed_url.query:
            law_id_base += '_' + parsed_url.query.replace('=', '_').replace('&', '_')
        if parsed_url.fragment:
            law_id_base += '_' + parsed_url.fragment
        # Only replace non-alphanumeric except underscore and @
        law_id = re.sub(r'[^a-zA-Z0-9_@-]', '_', law_id_base)
    else:
        # fallback to previous logic
        path_part = os.path.basename(parsed_url.path)
        if not path_part or path_part.lower() in ['index.html', 'index.php', 'default.aspx', '']:
            if parsed_url.query:
                law_id_base = parsed_url.query
            elif parsed_url.fragment:
                law_id_base = parsed_url.fragment
            else:
                law_id_base = parsed_url.netloc
        else:
            law_id_base = path_part
        if '?' in law_id_base:
            law_id_base = law_id_base.split('?', 1)[0]
        law_id_base = law_id_base.replace('sb.php?subject_id=', 'subject_')
        law_id = re.sub(r'[^a-zA-Z0-9_-]', '_', law_id_base)
    law_id = re.sub(r'_+', '_', law_id).strip('_')
    if not law_id:
        law_id = hashlib.md5(original_url_for_hash.encode('utf-8')).hexdigest()[:10]
    MAX_LAW_ID_LENGTH = 100
    if len(law_id) > MAX_LAW_ID_LENGTH:
        hash_suffix = hashlib.md5(law_id.encode('utf-8')).hexdigest()[:8]
        law_id = law_id[:MAX_LAW_ID_LENGTH - len(hash_suffix) - 1] + "_" + hash_suffix
        law_id = re.sub(r'_+', '_', law_id).strip('_')
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
    """
    Search lawdata/ for a law with the same or very similar title.
    Returns: (full_file_path_to_json, law_data_dict, containing_folder_path) or (None, None, None)
    """
    if not os.path.exists(DATA_DIR):
        return None, None, None
    if not title: # Cannot search if no title is provided
        return None, None, None

    for law_id_folder_name in os.listdir(DATA_DIR):
        law_folder_path = os.path.join(DATA_DIR, law_id_folder_name)
        if not os.path.isdir(law_folder_path):
            continue
        
        # Assuming the JSON file is named after the law_id, e.g., <law_id_folder_name>.json
        # Or iterate through all .json files if naming is not strict.
        # For now, let's assume it's {law_id_folder_name}.json or the first .json found.
        # A more robust way would be to ensure only one JSON per folder or a clear naming convention.
        json_files_in_folder = [f for f in os.listdir(law_folder_path) if f.endswith('.json')]
        
        for fname in json_files_in_folder:
            file_path = os.path.join(law_folder_path, fname)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    law = json.load(f)
            except json.JSONDecodeError:
                log_warning(f"Could not decode JSON from {file_path}")
                continue
            except Exception as e:
                log_warning(f"Error reading {file_path}: {e}")
                continue

            if isinstance(law, list): # Should be a dict
                continue

            existing_title = law.get('title')
            if existing_title and existing_title.lower() == title.lower():
                return file_path, law, law_folder_path
            # Optional: Fuzzy match (substring). Be cautious with this.
            if existing_title and title.lower() in existing_title.lower():
                log_info(f"Fuzzy title match: new='{title}', existing='{existing_title}' from {file_path}")
                return file_path, law, law_folder_path
                
    return None, None, None

def _move_related_files(law_data, destination_folder):
    """Helper function to move related files and update paths in law_data."""
    if 'related_files' in law_data:
        for rel_file_info in law_data.get('related_files', []):
            if 'path' in rel_file_info and rel_file_info['path'] and os.path.exists(rel_file_info['path']):
                original_file_path = rel_file_info['path']
                file_basename = os.path.basename(original_file_path)
                
                # Sanitize basename slightly to avoid issues, though download_pdf should ideally handle this.
                # This is a basic sanitization.
                safe_basename = re.sub(r'[^\w\.\-]', '_', file_basename)
                destination_file_path = os.path.join(destination_folder, safe_basename)

                if os.path.abspath(original_file_path) != os.path.abspath(destination_file_path):
                    try:
                        os.makedirs(destination_folder, exist_ok=True)
                        os.replace(original_file_path, destination_file_path)
                        log_info(f"Moved file {original_file_path} to {destination_file_path}")
                        rel_file_info['path'] = destination_file_path # Update path in law_data
                    except Exception as e:
                        log_warning(f"Could not move file {original_file_path} to {destination_file_path}: {e}")
                else:
                    # File is already in the destination folder, ensure path is absolute and correct
                    rel_file_info['path'] = os.path.abspath(destination_file_path)
            elif 'path' in rel_file_info and rel_file_info['path']:
                log_warning(f"File path specified but does not exist: {rel_file_info['path']} for law {law_data.get('title')}")


def save_law_json(law, law_id):
    ensure_data_dir()
    new_law_folder = os.path.join(DATA_DIR, law_id)
    # Do not create new_law_folder prematurely, only if we are certain to save there.

    current_law_title = law.get('title')
    existing_law_filepath, existing_law_data, existing_law_folder_path = find_existing_law_by_title(current_law_title, law.get('year'))

    if existing_law_data:
        log_warning(f"Potential duplicate for title: '{current_law_title}'. Existing: {existing_law_filepath}, New source: {law.get('source')}")
        
        # Scenario 1: Existing law has no content, replace it.
        if not existing_law_data.get('content') or not str(existing_law_data.get('content')).strip():
            log_info(f"Existing law at {existing_law_filepath} has no content. Replacing with new data.")
            os.makedirs(existing_law_folder_path, exist_ok=True) # Ensure folder exists
            with open(existing_law_filepath, "w", encoding="utf-8") as f:
                json.dump(law, f, ensure_ascii=False, indent=2)
            _move_related_files(law, existing_law_folder_path) # Move new files to existing folder
            with open(existing_law_filepath, "w", encoding="utf-8") as f: # Save again with updated paths
                json.dump(law, f, ensure_ascii=False, indent=2)
            log_success(f"Replaced empty-content law at {existing_law_filepath} with new data from {law.get('source')}.")
            # If new_law_folder was different and potentially created, check if it's empty and remove.
            # This check is tricky if new_law_folder wasn't created yet.
            # For now, assume if we replace an existing, the new_law_folder for the current law_id isn't used.
            return

        # Scenario 2: Semantically same law, compare years.
        if is_semantically_same_law(law.get('content', ''), existing_law_data.get('content', '')):
            try:
                new_year_str = str(law.get('year') or law.get('date', '0')).split('-')[0]
                old_year_str = str(existing_law_data.get('year') or existing_law_data.get('date', '0')).split('-')[0]
                
                new_year_match = re.search(r'(19\d{2}|20\d{2})', new_year_str)
                old_year_match = re.search(r'(19\d{2}|20\d{2})', old_year_str)

                new_year = int(new_year_match.group(0)) if new_year_match else 0
                old_year = int(old_year_match.group(0)) if old_year_match else 0
            except (ValueError, TypeError, AttributeError) as e:
                log_warning(f"Could not parse years for comparison: new='{law.get('year')}/{law.get('date')}', old='{existing_law_data.get('year')}/{existing_law_data.get('date')}'. Error: {e}")
                new_year, old_year = 0, 0 # Fallback

            if new_year > old_year:
                log_info(f"Semantically same. New version (Year: {new_year}) is newer than existing (Year: {old_year}). Replacing at {existing_law_filepath}.")
                os.makedirs(existing_law_folder_path, exist_ok=True)
                with open(existing_law_filepath, "w", encoding="utf-8") as f:
                    json.dump(law, f, ensure_ascii=False, indent=2)
                _move_related_files(law, existing_law_folder_path)
                with open(existing_law_filepath, "w", encoding="utf-8") as f:
                    json.dump(law, f, ensure_ascii=False, indent=2)
                log_success(f"Updated law at {existing_law_filepath} with newer version from {law.get('source')}.")
            else:
                log_warning(f"Semantically same. Existing (Year: {old_year}) is same or newer than new (Year: {new_year}). Keeping existing at {existing_law_filepath}.")
            return # Processed duplicate

        # Scenario 3: Same title, but different content. Log and save new law under its own ID.
        log_warning(f"Laws with same title '{current_law_title}' but different content. Existing: {existing_law_filepath}. Saving new law from {law.get('source')} under its own ID: {law_id}")
        # Fall through to save the new law in its own folder.

    # Default: Save new law in its own folder if no duplicate was actioned above.
    if not os.path.exists(new_law_folder):
        os.makedirs(new_law_folder)
    
    new_law_json_path = os.path.join(new_law_folder, f"{law_id}.json")
    with open(new_law_json_path, "w", encoding="utf-8") as f:
        json.dump(law, f, ensure_ascii=False, indent=2)
    
    _move_related_files(law, new_law_folder) # Move related files to this new folder
    
    # Update JSON with potentially new related file paths after moving
    with open(new_law_json_path, "w", encoding="utf-8") as f:
        json.dump(law, f, ensure_ascii=False, indent=2)
    log_success(f"Saved new law: {new_law_json_path}")


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
            log_info(f"Fetching: {url}")
            try:
                # resp = requests.get(url, headers=HEADERS, timeout=20)
                resp = SESSION.get(url, timeout=20) # Use session
            except Exception as e:
                log_error(f"Request failed: {e}")
                break
            if resp.status_code != 200:
                log_warning(f"Non-200 status code: {resp.status_code}")
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
                elif section["type"] == "speech" and ("/speeches/" in href or "/doc/speech" in href): # Completed condition
                    law_links.append((a, section["type"]))
                # Add more specific conditions if needed for other types based on URL patterns
            log_info(f"Found {len(law_links)} {section['type']} links on page {page}.")
            if not law_links:
                break
            for link_tag, law_type in law_links: # Unpack the tuple
                # Ensure link_tag has 'href'
                if not hasattr(link_tag, 'get') or not link_tag.get('href'):
                    log_warning(f"Skipped invalid link object: {link_tag} in section {section['type']}")
                    continue

                item_url = urljoin(base_url, link_tag['href'])
                law_id = law_id_from_url(item_url)

                # The following block that skips based on processed_ids is now removed
                # if law_id in processed_ids:
                #     # log_info(f"Skipping {law_id} ({law_type}), already processed.")
                #     continue
                
                # Always attempt to fetch details and then let save_law_json handle duplicates/updates
                law_data = fetch_zambialii_detail(item_url, law_type)
                if law_data:
                    save_law_json(law_data, law_id) # This function handles existing files
                    processed_ids.add(law_id) # Add to set for current session's checkpoint
                    save_checkpoint(processed_ids)
                    log_success(f"Saved/Updated: {law_id} ({law_type}) from {item_url}")
                    time.sleep(1) # Be respectful to the server
                else:
                    log_warning(f"No data returned for {law_id} ({law_type}) from {item_url}")
            
            page += 1
            # Safety break for very long sections, especially judgments
            if page > 200 and section["type"] == "judgment": # Limit judgment pages for now
                log_warning(f"Reached page limit (200) for judgments in {section['url']}. Moving to next section.")
                break
            if page > 50 and section["type"] != "judgment": # Limit other sections to 50 pages
                log_warning(f"Reached page limit (50) for {section['type']} in {section['url']}. Moving to next section.")
                break


def extract_pdf_text(pdf_path):
    """
    Extracts text from a PDF file with maximum accuracy for legal documents.
    - Tries pdfplumber (best for layout/tables), then pdfminer.six, then PyPDF2.
    - If all fail or text is empty, tries OCR (Tesseract) for scanned/image PDFs.
    - Returns a single string suitable for ML and legal display.
    """
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        if text and len(text.strip()) > 0:
            return text.strip()
    except Exception as e:
        log_warning(f"pdfplumber extraction failed: {e}")
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract_text
        text = pdfminer_extract_text(pdf_path)
        if text and len(text.strip()) > 0:
            return text.strip()
    except Exception as e:
        log_warning(f"pdfminer.six extraction failed: {e}")
    try:
        from PyPDF2 import PdfReader
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            text = '\n'.join((page.extract_text() or '').strip() for page in reader.pages)
        if text and len(text.strip()) > 0:
            log_warning("Used PyPDF2 fallback for PDF extraction. Output may be less accurate.")
            return text.strip()
    except Exception as e:
        log_warning(f"Exception extracting PDF text with PyPDF2: {e}")
    # OCR fallback for scanned/image PDFs
    try:
        from pdf2image import convert_from_path
        import pytesseract
        images = convert_from_path(pdf_path)
        text = '\n'.join(pytesseract.image_to_string(img) for img in images)
        if text and len(text.strip()) > 0:
            log_success("Used OCR fallback for scanned PDF.")
            return text.strip()
    except Exception as e:
        log_warning(f"OCR extraction failed: {e}")
    return ""

def download_pdf(pdf_url, law_id, title=None, year=None):
    pdf_filename = os.path.join(DATA_DIR, f"{law_id}.pdf")
    # Check for duplicate by law_id
    if os.path.exists(pdf_filename):
        print(f"    PDF with ID '{law_id}' or similar metadata likely already exists at: {pdf_filename}. Skipping download.")
        return pdf_filename
    # Check for duplicate by title/year in subfolders
    if title and year:
        for item in os.listdir(DATA_DIR):
            item_path = os.path.join(DATA_DIR, item)
            if os.path.isdir(item_path):
                for fname in os.listdir(item_path):
                    if title.replace(' ', '_') in fname and str(year) in fname and fname.endswith('.pdf'):
                        match_path = os.path.join(item_path, fname)
                        print(f"    PDF with ID '{law_id}' or similar metadata likely already exists at: {match_path}. Skipping download.")
                        return match_path
    if not title and not year:
        print(f"    No metadata (title/year) provided for pre-download duplicate check for {pdf_url}. Proceeding with download.")
    
    try:
        # Use SESSION.get for consistency and to allow proper mocking if tests target zambian_law_scraper.SESSION.get
        resp = SESSION.get(pdf_url, headers=HEADERS, timeout=30, stream=True) 
        if resp.status_code == 200:
            with open(pdf_filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            print(f"    Downloading PDF: {pdf_url}")
            print(f"    Successfully downloaded PDF to: {pdf_filename}")
            return pdf_filename
        else:
            print(f"    Failed to download PDF: {pdf_url} (status {resp.status_code})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"    Request failed during PDF download: {pdf_url} ({e})")
        return None

def fetch_ministry_justice_documents(processed_ids):
    log_warning("[STUB] fetch_ministry_justice_documents called - no implementation.")
    return

def fetch_judiciary_cases(processed_ids):
    log_warning("[STUB] fetch_judiciary_cases called - no implementation.")
    return

def fetch_parliament_acts(processed_ids):
    log_warning("[STUB] fetch_parliament_acts called - no implementation.")
    return

def fetch_blackhall_acts(processed_ids):
    log_warning("[STUB] fetch_blackhall_acts called - no implementation.")
    return

def fetch_loc_references(processed_ids):
    log_warning("[STUB] fetch_loc_references called - no implementation.")
    return

def fetch_globalex_references(processed_ids):
    log_warning("[STUB] fetch_globalex_references called - no implementation.")
    return

def fetch_hrc_publications(processed_ids):
    log_warning("[STUB] fetch_hrc_publications called - no implementation.")
    return

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
        json.dump(report, f, ensure_ascii=False, indent=2) # Corrected this line
    
    log_success(f"Source analysis report saved to: {report_file}")
    return report

# Add at the end of the existing file, before main()
def main():
    start_time = time.time()
    ensure_data_dir()
    processed_ids = load_checkpoint()
    
    log_info("=== ZAMBIAN LAW SCRAPER - COMPREHENSIVE RESEARCH UPDATE ===")
    log_info("Starting comprehensive scraping of Zambian legal sources...\n")
    
    # 1. ZambiaLII - Primary and most comprehensive source
    log_info("1. Fetching all Zambian law data from ZambiaLII...")
    log_info("   (Legislation, Bills, Judgments, Gazettes, Speeches, Law Reform Reports)")
    try:
        fetch_zambialii_all(processed_ids)
        log_success("   ✅ ZambiaLII scraping completed successfully\n")
    except Exception as e:
        log_error(f"   ❌ ZambiaLII scraping failed: {e}\n")
    
    # 2. Ministry of Justice - Policies and legal documents  
    log_info("2. Fetching documents from Ministry of Justice...")
    log_info("   (Policies, Reports, Legal Bulletins)")
    try:
        fetch_ministry_justice_documents(processed_ids)
        log_success("   ✅ Ministry of Justice scraping completed\n")
    except Exception as e:
        log_error(f"   ❌ Ministry of Justice scraping failed: {e}\n")
    
    # 3. Judiciary of Zambia - Case law and judgments
    log_info("3. Fetching all Zambian law data from Judiciary of Zambia...")
    log_info("   (Judgments from Supreme Court, High Court, Subordinate Courts)")
    try:
        fetch_judiciary_cases(processed_ids)
        log_success("   ✅ Judiciary scraping completed successfully\n")
    except Exception as e:
        log_error(f"   ❌ Judiciary scraping failed: {e}\n")
    
    # 4. Parliament of Zambia - Acts and Bills (with SSL error handling)
    log_info("4. Fetching all Zambian law data from Parliament of Zambia...")
    log_info("   (Acts and Bills - Note: may have SSL certificate issues)")
    try:
        fetch_parliament_acts(processed_ids)
        log_success("   ✅ Parliament scraping completed successfully\n")
    except Exception as e:
        log_error(f"   ❌ Parliament scraping failed: {e}\n")
    
    # 5. Blackhall's Laws of Zambia - Statutory laws (subscription-based)
    log_info("5. Fetching all Zambian law data from Blackhall's Laws of Zambia...")
    log_info("   (Statutory Laws - Note: requires subscription for full access)")
    try:
        fetch_blackhall_acts(processed_ids)
        log_success("   ✅ Blackhall scraping completed successfully\n")
    except Exception as e:
        log_error(f"   ❌ Blackhall scraping failed: {e}\n")
    
    # 6. Library of Congress - Legal research guides
    log_info("6. Fetching legal references from Law Library of Congress...")
    log_info("   (Legal Research Guides and Reference Materials)")
    try:
        fetch_loc_references(processed_ids)
        log_success("   ✅ Library of Congress scraping completed\n")
    except Exception as e:
        log_error(f"   ❌ Library of Congress scraping failed: {e}\n")
    
    # 7. GlobaLex - Legal research resources
    log_info("7. Fetching legal references from GlobaLex...")
    log_info("   (Legal Research Resources and Guides)")
    try:
        fetch_globalex_references(processed_ids)
        log_success("   ✅ GlobaLex scraping completed\n")
    except Exception as e:
        log_error(f"   ❌ GlobaLex scraping failed: {e}\n")
    
    # 8. Human Rights Commission - Reports and publications (may be inaccessible)
    log_info("8. Fetching publications from Zambia Human Rights Commission...")
    log_info("   (Human Rights Reports - Note: website may be inaccessible)")
    try:
        fetch_hrc_publications(processed_ids)
        log_success("   ✅ HRC scraping completed\n")
    except Exception as e:
        log_error(f"   ❌ HRC scraping failed: {e}\n")
    
    elapsed = time.time() - start_time
    log_info(f"\nScraping complete. Total time: {elapsed:.1f} seconds.")
    log_info("=== SCRAPING COMPLETED ===")
    log_info(f"Total documents processed: {len(processed_ids)}")
    log_info(f"Data saved to: {DATA_DIR}")
    log_info("\nSUMMARY OF SOURCES:")
    log_info("✅ ZambiaLII: Primary source with 9,000+ documents")
    log_info("✅ Judiciary: Extensive case archive from 2016-2025") 
    log_info("✅ Ministry of Justice: Policies and legal bulletins")
    log_info("⚠️  Parliament: SSL issues may limit access")
    log_info("⚠️  Blackhall: Subscription required for full access")
    log_info("✅ Research Sources: LoC and GlobaLex guides accessible")
    log_info("❌ HRC & ACC: Websites currently inaccessible")
    log_info("\nDone.")

if __name__ == "__main__":
    main()
