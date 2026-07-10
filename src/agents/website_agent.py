"""
Module 2: Website Intelligence Agent
FIXED: Better email extraction with dynamic content handling
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import re
import time
import json
from typing import Dict, Optional, List, Any, Set, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime
import sys
from pathlib import Path
import codecs

# Configure logging with UTF-8 support
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/website_agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_RAW / "all_countries_leads.csv"
OUTPUT_FILE = DATA_PROCESSED / "website_intelligence.csv"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_DELAY = 2


class WebsiteIntelligenceAgent:
    """Website Intelligence Agent with improved email extraction."""
    
    def __init__(self, input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE):
        self.input_file = input_file
        self.output_file = output_file
        self.df = None
        self.results = []
        
        DATA_RAW.mkdir(parents=True, exist_ok=True)
        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info(f"Website Intelligence Agent initialized")
        logger.info(f"Input file: {self.input_file}")
        logger.info(f"Output file: {self.output_file}")
    
    def is_valid_url(self, url: Any) -> bool:
        """Check if URL is valid and not NaN/None."""
        if url is None:
            return False
        if isinstance(url, float):
            return False
        if not isinstance(url, str):
            return False
        url = url.strip()
        if not url:
            return False
        if url.lower() in ['nan', 'none', 'null', '']:
            return False
        if not url.startswith(('http://', 'https://')):
            if url.startswith('/'):
                return False
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                return False
        if '/aclk?' in url or 'googleadservices' in url:
            return False
        if url.startswith('https:///') or url.startswith('http:///'):
            return False
        return True
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for proper fetching."""
        if not url:
            return ""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                return ""
        url = url.rstrip('/')
        return url
    
    def load_data(self) -> pd.DataFrame:
        """Load the leads data from CSV."""
        try:
            self.df = pd.read_csv(self.input_file)
            logger.info(f"Loaded {len(self.df)} records from {self.input_file}")
            return self.df
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.input_file}")
            logger.info("Please ensure Module 1 (Business Discovery Agent) has been run first.")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def fetch_page(self, url: str) -> Tuple[Optional[str], Optional[requests.Response]]:
        """Fetch a webpage with retry logic."""
        if not self.is_valid_url(url):
            return None, None
        
        normalized_url = self.normalize_url(url)
        if not normalized_url:
            return None, None
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    normalized_url,
                    headers=HEADERS,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.text, response
                elif response.status_code in [403, 404, 500, 502, 503]:
                    logger.warning(f"HTTP {response.status_code} for {normalized_url}")
                    return None, response
                else:
                    logger.warning(f"HTTP {response.status_code} for {normalized_url} (attempt {attempt+1})")
                    time.sleep(RETRY_DELAY)
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout for {normalized_url} (attempt {attempt+1})")
                time.sleep(RETRY_DELAY)
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error for {normalized_url} (attempt {attempt+1})")
                time.sleep(RETRY_DELAY)
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error for {normalized_url}: {e}")
                time.sleep(RETRY_DELAY)
        
        return None, None
    
    def extract_emails_improved(self, html: str, soup: BeautifulSoup, url: str) -> Tuple[List[str], List[str]]:
        """
        IMPROVED: Extract emails using multiple methods.
        
        Returns:
            Tuple of (business_emails, contact_emails)
        """
        if not html:
            return [], []
        
        all_emails = set()
        contact_emails = set()
        business_emails = set()
        
        # Method 1: Regex from HTML
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        regex_emails = re.findall(email_pattern, html)
        for email in regex_emails:
            if '@example.com' in email:
                continue
            if 'sentry.wixpress.com' in email:
                continue
            if len(email) > 50:
                continue
            all_emails.add(email.lower())
        
        # Method 2: Find mailto: links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0].strip()
                if email and '@' in email:
                    if len(email) < 50:
                        all_emails.add(email.lower())
        
        # Method 3: Decode obfuscated emails (common anti-spam technique)
        # Pattern: contact<!-- -->@bittechnologies<!-- -->.co
        obfuscated_pattern = r'([a-zA-Z0-9._%+-]+)<!--[^>]*-->@<!--[^>]*-->([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        matches = re.findall(obfuscated_pattern, html)
        for match in matches:
            email = f"{match[0]}@{match[1]}"
            all_emails.add(email)
        
        # Method 4: Find emails in text (avoid email in code/scripts)
        # Get visible text only
        text = self.extract_text_from_soup(soup)
        text_emails = re.findall(email_pattern, text)
        for email in text_emails:
            if len(email) < 50 and '@' in email:
                all_emails.add(email.lower())
        
        # Categorize emails
        contact_keywords = ['contact', 'info', 'hello', 'support', 'sales', 'enquiry', 'inquiry', 'connect']
        for email in all_emails:
            if any(kw in email for kw in contact_keywords):
                contact_emails.add(email)
            else:
                business_emails.add(email)
        
        # If no emails found in contact categories, but some exist, put them in contact
        if contact_emails and not business_emails:
            # Move one to business if possible
            for email in contact_emails:
                if 'info' not in email and 'contact' not in email:
                    business_emails.add(email)
                    contact_emails.remove(email)
                    break
        
        # If only business emails and no contact, move one to contact
        if business_emails and not contact_emails:
            first = next(iter(business_emails))
            contact_emails.add(first)
            business_emails.remove(first)
        
        return list(business_emails)[:5], list(contact_emails)[:5]
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        if not text:
            return []
        
        phone_patterns = [
            r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}',
            r'\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{4}[-.\s]?\d{4}',
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        filtered = []
        for phone in phones:
            clean = re.sub(r'[^\d+\-]', '', phone)
            digits = re.sub(r'[^\d]', '', clean)
            if 5 <= len(digits) <= 15:
                filtered.append(clean)
        
        return list(set(filtered))[:5]
    
    def extract_whatsapp(self, text: str) -> Optional[str]:
        """Extract WhatsApp number from text."""
        if not text:
            return None
        
        patterns = [
            r'whatsapp:?//?[^\s"\']+',
            r'wa\.me/[^\s"\']+',
            r'api\.whatsapp\.com/[^\s"\']+',
            r'whatsapp[\s:]+([\+0-9\-\(\)\s]{8,20})',
            r'whatsapp\s*number[\s:]*([\+0-9\-\(\)\s]{8,20})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    clean = re.sub(r'[^\d+]', '', match)
                    if len(clean) >= 8 and len(clean) <= 15:
                        return clean
        
        phones = self.extract_phones(text)
        for phone in phones:
            idx = text.find(phone)
            if idx != -1:
                surrounding = text[max(0, idx-50):min(len(text), idx+50)]
                if 'whatsapp' in surrounding.lower():
                    return phone
        
        return None
    
    def extract_social_links(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """Extract social media links from page."""
        social_links = {}
        social_domains = {
            'facebook': 'facebook.com',
            'twitter': 'twitter.com',
            'linkedin': 'linkedin.com',
            'instagram': 'instagram.com',
            'youtube': 'youtube.com',
            'github': 'github.com',
            'tiktok': 'tiktok.com',
            'pinterest': 'pinterest.com',
        }
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue
            
            full_url = urljoin(url, href)
            
            for social, domain in social_domains.items():
                if domain in full_url.lower():
                    if social not in social_links:
                        social_links[social] = full_url
                    break
        
        return social_links
    
    def check_ssl(self, url: str) -> bool:
        """Check if website has SSL certificate."""
        if not self.is_valid_url(url):
            return False
        
        normalized = self.normalize_url(url)
        if not normalized:
            return False
        
        https_url = normalized.replace('http://', 'https://')
        try:
            response = requests.get(https_url, timeout=5, allow_redirects=True)
            if response.url.startswith('https://'):
                return True
        except:
            pass
        
        if url.startswith('https://'):
            return True
        
        return False
    
    def extract_technologies(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Extract technologies used from page."""
        technologies = set()
        
        tech_patterns = {
            'WordPress': ['wp-content', 'wp-includes', 'wordpress', 'wp-json'],
            'React': ['react', 'react-dom', 'react-js'],
            'Angular': ['angular', 'ng-', 'ngx-'],
            'Vue': ['vue', 'vuejs', 'v-'],
            'Node': ['nodejs', 'node.js', 'express'],
            'Laravel': ['laravel', 'elixir', 'livewire'],
            'PHP': ['php', '.php', '<?php'],
            'Python': ['python', 'django', 'flask'],
            'Java': ['java', 'jsp', 'servlet'],
            'Ruby': ['ruby', 'rails', '.erb'],
            'Go': ['golang', 'go-', 'gin'],
            'Rust': ['rust', 'cargo', '.rs'],
            'Django': ['django', 'djangojs', 'csrf'],
            'Flask': ['flask', 'jinja'],
            'AWS': ['aws', 'amazonaws', 's3.amazonaws'],
            'Azure': ['azure', 'windowsazure'],
            'Docker': ['docker', 'container'],
            'Kubernetes': ['k8s', 'kubernetes'],
            'TensorFlow': ['tensorflow', 'tf-', 'keras'],
            'PyTorch': ['pytorch', 'torch-'],
            '.NET': ['asp.net', '.net', 'c#', 'cshtml'],
        }
        
        html_lower = html.lower() if html else ''
        for tech, indicators in tech_patterns.items():
            for indicator in indicators:
                if indicator.lower() in html_lower:
                    technologies.add(tech)
                    break
        
        meta_generator = soup.find('meta', {'name': 'generator'})
        if meta_generator and meta_generator.get('content'):
            content = meta_generator.get('content').lower()
            for tech in tech_patterns:
                if tech.lower() in content:
                    technologies.add(tech)
        
        return list(technologies)
    
    def extract_text_from_soup(self, soup: BeautifulSoup) -> str:
        """Extract clean text from BeautifulSoup object."""
        if not soup:
            return ""
        
        for element in soup(['script', 'style', 'noscript', 'meta', 'link']):
            element.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def find_contact_pages(self, soup: BeautifulSoup, url: str) -> List[str]:
        """Find contact page URLs."""
        contact_urls = []
        contact_keywords = ['contact', 'contact-us', 'contactus', 'get-in-touch', 'reach-us']
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            for keyword in contact_keywords:
                if keyword in href:
                    full_url = urljoin(url, href)
                    if full_url not in contact_urls:
                        contact_urls.append(full_url)
                    break
        
        return contact_urls[:3]  # Max 3 contact pages
    
    def fetch_contact_pages(self, contact_urls: List[str]) -> List[str]:
        """Fetch additional contact pages for email extraction."""
        contact_htmls = []
        for url in contact_urls:
            html, _ = self.fetch_page(url)
            if html:
                contact_htmls.append(html)
            time.sleep(1)
        return contact_htmls
    
    def analyze_website(self, url: str, html: str, soup: BeautifulSoup) -> Dict:
        """Analyze website and extract all intelligence."""
        data = {
            'website_url': url,
            'business_emails': [],
            'contact_emails': [],
            'phones': [],
            'whatsapp': None,
            'contact_form': False,
            'about_us': None,
            'description': None,
            'services': [],
            'products': [],
            'industries_served': [],
            'portfolio': [],
            'clients': [],
            'careers': False,
            'technologies': [],
            'blog': False,
            'ssl': self.check_ssl(url),
            'social_links': {},
            'title': None,
            'status': 'success'
        }
        
        if not html or not soup:
            data['status'] = 'failed'
            return data
        
        # Extract emails from homepage
        business_emails, contact_emails = self.extract_emails_improved(html, soup, url)
        data['business_emails'] = business_emails
        data['contact_emails'] = contact_emails
        
        # Find and fetch contact pages for more emails
        contact_urls = self.find_contact_pages(soup, url)
        if contact_urls:
            logger.debug(f"Found contact pages: {contact_urls}")
            contact_htmls = self.fetch_contact_pages(contact_urls)
            for contact_html in contact_htmls:
                contact_soup = BeautifulSoup(contact_html, 'html.parser')
                add_business, add_contact = self.extract_emails_improved(contact_html, contact_soup, url)
                data['business_emails'].extend(add_business)
                data['contact_emails'].extend(add_contact)
                time.sleep(0.5)
        
        # Remove duplicates
        data['business_emails'] = list(set(data['business_emails']))[:5]
        data['contact_emails'] = list(set(data['contact_emails']))[:5]
        
        # Extract phones from all content
        text = self.extract_text_from_soup(soup)
        data['phones'] = self.extract_phones(text)
        
        # Also check contact page texts for phones
        for contact_html in contact_htmls:
            contact_soup = BeautifulSoup(contact_html, 'html.parser')
            contact_text = self.extract_text_from_soup(contact_soup)
            data['phones'].extend(self.extract_phones(contact_text))
        data['phones'] = list(set(data['phones']))[:5]
        
        data['whatsapp'] = self.extract_whatsapp(text)
        
        forms = soup.find_all('form')
        for form in forms:
            if 'contact' in str(form).lower():
                data['contact_form'] = True
                break
        
        if soup.title:
            data['title'] = soup.title.string.strip() if soup.title.string else None
        
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            data['description'] = meta_desc.get('content').strip()
        
        # FIXED: Using 'string' instead of 'text'
        about_keywords = ['about', 'about us', 'our story', 'who we are']
        for keyword in about_keywords:
            elements = soup.find_all(['section', 'div', 'p'], string=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element:
                    text_content = element.get_text().strip()
                    if text_content and len(text_content) > 100:
                        data['about_us'] = text_content[:1000]
                        break
            if data['about_us']:
                break
        
        service_keywords = ['services', 'what we do', 'our services', 'our offerings']
        for keyword in service_keywords:
            elements = soup.find_all(['section', 'div', 'h2', 'h3'], string=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element and element.parent:
                    text_content = element.parent.get_text().strip()
                    if text_content:
                        data['services'].append(text_content[:500])
            if data['services']:
                break
        
        product_keywords = ['products', 'our products', 'product', 'solutions']
        for keyword in product_keywords:
            elements = soup.find_all(['section', 'div', 'h2', 'h3'], string=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element and element.parent:
                    text_content = element.parent.get_text().strip()
                    if text_content:
                        data['products'].append(text_content[:500])
            if data['products']:
                break
        
        data['social_links'] = self.extract_social_links(soup, url)
        data['technologies'] = self.extract_technologies(soup, html)
        
        blog_keywords = ['blog', 'news', 'articles', 'insights']
        for keyword in blog_keywords:
            if keyword in text.lower():
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if keyword in href.lower():
                        data['blog'] = True
                        break
            if data['blog']:
                break
        
        career_keywords = ['careers', 'jobs', 'join us', 'working at', 'open positions']
        for keyword in career_keywords:
            if keyword in text.lower():
                data['careers'] = True
                break
        
        return data
    
    def process_company(self, row: pd.Series, index: int) -> Dict:
        """Process a single company website."""
        company_name = row.get('company_name', 'Unknown')
        if pd.isna(company_name):
            company_name = 'Unknown'
        else:
            company_name = str(company_name).strip()
        
        website_url = row.get('website', '') or row.get('website_url', '')
        if pd.isna(website_url):
            website_url = ''
        
        result = {
            'website_url': website_url,
            'domain': self.extract_domain_from_url(website_url),
            'business_emails': [],
            'contact_emails': [],
            'phones': [],
            'whatsapp': None,
            'contact_form': False,
            'about_us': None,
            'description': None,
            'services': [],
            'products': [],
            'industries_served': [],
            'portfolio': [],
            'clients': [],
            'careers': False,
            'technologies': [],
            'blog': False,
            'ssl': False,
            'social_links': {},
            'title': None,
            'status': 'failed',
            'company_name': company_name,
            'location': row.get('location', ''),
            'source': row.get('source', ''),
            'original_phone': row.get('phone', ''),
            'original_address': row.get('address', ''),
            'date_analyzed': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if not self.is_valid_url(website_url):
            logger.warning(f"Skipping {company_name}: Invalid URL")
            result['status'] = 'invalid_url'
            return result
        
        logger.info(f"[{index+1}/{len(self.df)}] Processing: {company_name[:50]}...")
        logger.info(f"Analyzing: {website_url}")
        
        html, response = self.fetch_page(website_url)
        
        if not html:
            logger.warning(f"Failed to fetch {website_url}")
            result['status'] = 'connection_error'
            return result
        
        soup = BeautifulSoup(html, 'html.parser')
        data = self.analyze_website(website_url, html, soup)
        result.update(data)
        
        logger.info(f"[OK] {website_url}: {len(result['business_emails'])} business emails, {len(result['contact_emails'])} contact emails, {len(result['phones'])} phones")
        
        return result
    
    def extract_domain_from_url(self, url: str) -> str:
        """Extract domain from URL."""
        if not self.is_valid_url(url):
            return ""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            domain = re.sub(r'^www\.', '', domain)
            return domain
        except:
            return ""
    
    def run(self) -> pd.DataFrame:
        """Run the Website Intelligence Agent."""
        logger.info("Starting Website Intelligence Agent")
        
        self.load_data()
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        total = len(self.df)
        success_count = 0
        email_found_count = 0
        
        for index, row in self.df.iterrows():
            try:
                result = self.process_company(row, index)
                self.results.append(result)
                
                if result['status'] == 'success':
                    success_count += 1
                    if result['business_emails'] or result['contact_emails']:
                        email_found_count += 1
                
                if (index + 1) % 50 == 0:
                    logger.info(f"Progress: {index + 1}/{total}. Successful: {success_count}. Emails found: {email_found_count}")
                
                time.sleep(1.5)
                
            except Exception as e:
                logger.error(f"Error processing row {index}: {e}")
                continue
        
        results_df = pd.DataFrame(self.results)
        results_df.to_csv(self.output_file, index=False, encoding='utf-8')
        
        logger.info("="*70)
        logger.info(f"Analyzed: {len(results_df)} websites")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Companies with emails: {email_found_count}")
        logger.info(f"Saved to: {self.output_file}")
        logger.info("="*70)
        
        return results_df


def main():
    """Main entry point."""
    try:
        agent = WebsiteIntelligenceAgent()
        results = agent.run()
        
        print("\n" + "="*70)
        print("WEBSITE INTELLIGENCE AGENT - SUMMARY")
        print("="*70)
        print(f"Total Companies: {len(results)}")
        print(f"Successful: {len(results[results['status'] == 'success'])}")
        print(f"Emails Found: {len(results[(results['business_emails'].apply(len) > 0) | (results['contact_emails'].apply(len) > 0)])}")
        print(f"Output: {OUTPUT_FILE}")
        print("="*70)
        
        return results
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.info("Please ensure Module 1 (Business Discovery Agent) has been run first.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()