"""
Module 3: LinkedIn Company Intelligence Agent (With Playwright)
Purpose: Extract ALL LinkedIn company data using Playwright headless browser
Author: AI Sales Intelligence & Lead Generation Agent
Date: 2026-07-10

PDF Requirements:
- Company LinkedIn URL
- Company Description
- Headquarters
- Industry
- Company Size
- Employee Count
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import re
import time
import json
from typing import Dict, Optional, List, Any, Tuple
from urllib.parse import urlparse
from datetime import datetime
import sys
from pathlib import Path
import codecs

# Playwright
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/linkedin_agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_PROCESSED / "website_intelligence.csv"
OUTPUT_FILE = DATA_PROCESSED / "linkedin_data.csv"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}
REQUEST_TIMEOUT = 15
MAX_RETRIES = 2
RETRY_DELAY = 3


class LinkedInIntelligenceAgent:
    """LinkedIn Intelligence Agent using Playwright for proper rendering."""
    
    def __init__(self, input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE):
        self.input_file = input_file
        self.output_file = output_file
        self.df = None
        self.results = []
        
        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("="*70)
        logger.info("LINKEDIN INTELLIGENCE AGENT - MODULE 3 (Playwright)")
        logger.info("="*70)
        logger.info(f"Input: {self.input_file}")
        logger.info(f"Output: {self.output_file}")
    
    def is_valid_url(self, url: Any) -> bool:
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
            return False
        if '/aclk?' in url or 'googleadservices' in url:
            return False
        return True
    
    def load_data(self) -> pd.DataFrame:
        try:
            self.df = pd.read_csv(self.input_file)
            logger.info(f"Loaded {len(self.df)} records")
            return self.df
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.input_file}")
            raise
    
    def extract_domain(self, url: str) -> str:
        if not self.is_valid_url(url):
            return ""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            domain = re.sub(r'^www\.', '', domain)
            parts = domain.split('.')
            if len(parts) >= 2:
                return '.'.join(parts[-2:])
            return domain
        except:
            return ""
    
    def get_search_term(self, company_name: Any, website_url: str) -> str:
        if pd.isna(company_name) or not isinstance(company_name, str):
            company_name = ""
        else:
            company_name = company_name.strip()
        
        # Clean suffixes
        suffixes = [
            "Software House", "Software Company", "Software Development",
            "IT Company", "Web Development", "Digital Agency", "Technology",
            "Pvt Ltd", "Private Limited", "LLC", "Ltd", "Inc", "Corp",
            "Solutions", "Technologies", "Tech"
        ]
        for suffix in suffixes:
            company_name = company_name.replace(suffix, "").strip()
        
        if not company_name or len(company_name) < 3:
            if self.is_valid_url(website_url):
                domain = self.extract_domain(website_url)
                if domain:
                    parts = domain.split('.')
                    if parts:
                        company_name = parts[0].replace('-', ' ').replace('_', ' ').title()
        
        return company_name
    
    def extract_linkedin_from_social(self, social_links: Any) -> Optional[str]:
        if pd.isna(social_links):
            return None
        if not isinstance(social_links, str):
            return None
        
        try:
            if social_links.startswith('{'):
                links_dict = eval(social_links)
                if isinstance(links_dict, dict):
                    for key, value in links_dict.items():
                        if 'linkedin' in key.lower() and self.is_valid_url(value):
                            return value
            elif social_links.startswith('['):
                links_list = eval(social_links)
                if isinstance(links_list, list):
                    for link in links_list:
                        if isinstance(link, str) and 'linkedin.com' in link and self.is_valid_url(link):
                            return link
        except:
            pass
        return None
    
    def search_linkedin_page(self, company_name: str, website_url: str) -> Optional[str]:
        search_term = self.get_search_term(company_name, website_url)
        if not search_term or len(search_term) < 2:
            return None
        
        search_terms = [
            f"{search_term} LinkedIn company",
            f"{search_term} company LinkedIn",
        ]
        
        if self.is_valid_url(website_url):
            domain = self.extract_domain(website_url)
            if domain:
                search_terms.append(f"{domain} LinkedIn")
        
        for search_term_query in search_terms:
            try:
                query = search_term_query.replace(" ", "+")
                search_url = f"https://www.google.com/search?q={query}"
                
                response = requests.get(search_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if href and 'linkedin.com/company/' in href:
                        clean_url = self._extract_clean_url(href)
                        if clean_url and self.is_valid_url(clean_url):
                            return clean_url
                time.sleep(1)
            except:
                continue
        return None
    
    def _extract_clean_url(self, href: str) -> Optional[str]:
        try:
            if href.startswith('/url?q='):
                match = re.search(r'/url\?q=([^&]+)', href)
                if match:
                    return match.group(1)
            elif href.startswith('https://www.linkedin.com/company/'):
                return href
            elif href.startswith('http://www.linkedin.com/company/'):
                return href.replace('http://', 'https://')
        except:
            pass
        return None
    
    def fetch_linkedin_with_playwright(self, url: str) -> Optional[str]:
        """Fetch LinkedIn page using Playwright headless browser."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                # Navigate with timeout
                page.goto(url, timeout=30000, wait_until='networkidle')
                
                # Wait for content to load
                page.wait_for_timeout(3000)
                
                # Scroll to load dynamic content
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(2000)
                
                content = page.content()
                browser.close()
                return content
                
        except PlaywrightTimeout:
            logger.warning(f"Playwright timeout for {url}")
            return None
        except Exception as e:
            logger.warning(f"Playwright error for {url}: {e}")
            return None
    
    def scrape_linkedin_page(self, linkedin_url: str) -> Dict[str, Optional[str]]:
        """
        Scrape ALL LinkedIn company fields using Playwright.
        
        Extracts:
        - Company Description
        - Headquarters
        - Industry
        - Company Size
        - Employee Count
        """
        data = {
            'linkedin_url': linkedin_url,
            'linkedin_description': None,
            'linkedin_headquarters': None,
            'linkedin_industry': None,
            'linkedin_company_size': None,
            'linkedin_employee_count': None,
        }
        
        if not self.is_valid_url(linkedin_url):
            return data
        
        # Fetch with Playwright
        html = self.fetch_linkedin_with_playwright(linkedin_url)
        
        if not html:
            logger.warning(f"Failed to fetch {linkedin_url} with Playwright")
            return data
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            
            # ============================================================
            # 1. Description from Meta Tag
            # ============================================================
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                data['linkedin_description'] = meta_desc.get('content').strip()
            
            if not data['linkedin_description']:
                og_desc = soup.find('meta', {'property': 'og:description'})
                if og_desc and og_desc.get('content'):
                    data['linkedin_description'] = og_desc.get('content').strip()
            
            # ============================================================
            # 2. Headquarters
            # ============================================================
            hq_patterns = [
                r'Headquarters\s*:?\s*([^,\n]+(?:,\s*[^,\n]+)*)',
                r'Headquarters\s*([^,\n]+(?:,\s*[^,\n]+)*)',
                r'HQ\s*:?\s*([^,\n]+(?:,\s*[^,\n]+)*)',
                r'Location\s*:?\s*([^,\n]+(?:,\s*[^,\n]+)*)',
            ]
            for pattern in hq_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data['linkedin_headquarters'] = match.group(1).strip()
                    break
            
            # ============================================================
            # 3. Industry
            # ============================================================
            industry_patterns = [
                r'Industry\s*:?\s*([^\n]+)',
                r'Sector\s*:?\s*([^\n]+)',
                r'Field\s*:?\s*([^\n]+)',
            ]
            for pattern in industry_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data['linkedin_industry'] = match.group(1).strip()
                    break
            
            # ============================================================
            # 4. Company Size
            # ============================================================
            size_patterns = [
                r'Company size\s*:?\s*([^\n]+)',
                r'Size\s*:?\s*([^\n]+)',
                r'(\d+)\s*[-–]\s*(\d+)\s*employees?',
                r'(\d+)\s*employees?',
            ]
            for pattern in size_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2:
                        data['linkedin_company_size'] = f"{match.group(1)}-{match.group(2)}"
                    else:
                        data['linkedin_company_size'] = match.group(1).strip()
                    break
            
            # ============================================================
            # 5. Employee Count
            # ============================================================
            emp_patterns = [
                r'(\d+)\s*(?:employees?|people|members?)',
                r'(\d+,\d+)\s*(?:employees?|people)',
                r'(\d+\.\d+[Kk])\s*(?:employees?|people)',
                r'(\d+[Kk])\s*(?:employees?|people)',
            ]
            for pattern in emp_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data['linkedin_employee_count'] = match.group(1).strip()
                    break
            
            # Try from title
            if not data['linkedin_employee_count'] and soup.title:
                title_text = soup.title.string
                if title_text:
                    match = re.search(r'(\d+)\s*(?:employees?|followers?)', title_text, re.IGNORECASE)
                    if match:
                        data['linkedin_employee_count'] = match.group(1).strip()
            
            # If no size, use employee count
            if not data['linkedin_company_size'] and data['linkedin_employee_count']:
                data['linkedin_company_size'] = data['linkedin_employee_count']
            
            logger.debug(f"Extracted data for {linkedin_url}")
            
        except Exception as e:
            logger.warning(f"Error parsing LinkedIn page: {e}")
        
        return data
    
    def process_company(self, row: pd.Series, index: int) -> Dict:
        company_name = row.get('company_name', 'Unknown')
        if pd.isna(company_name):
            company_name = ''
        else:
            company_name = str(company_name).strip()
            if not company_name:
                company_name = 'Unknown'
        
        website_url = row.get('website_url', '')
        if pd.isna(website_url):
            website_url = ''
        
        social_links = row.get('social_links', '')
        linkedin_from_social = self.extract_linkedin_from_social(social_links)
        
        result = {
            'website_url': website_url,
            'company_name': company_name,
            'linkedin_url': linkedin_from_social,
            'linkedin_description': None,
            'linkedin_headquarters': None,
            'linkedin_industry': None,
            'linkedin_company_size': None,
            'linkedin_employee_count': None,
            'linkedin_status': 'not_found',
            'source': 'search'
        }
        
        # Try social links first
        if linkedin_from_social and self.is_valid_url(linkedin_from_social):
            logger.info(f"[{index+1}] Found LinkedIn from social: {company_name[:30]}...")
            linkedin_data = self.scrape_linkedin_page(linkedin_from_social)
            if linkedin_data.get('linkedin_description') or linkedin_data.get('linkedin_industry'):
                result.update(linkedin_data)
                result['linkedin_status'] = 'found'
                result['source'] = 'social_links'
                logger.info(f"[OK] Extracted data from social LinkedIn")
                return result
            else:
                # Still save URL even if data not extracted
                result['linkedin_url'] = linkedin_from_social
                result['linkedin_status'] = 'found'
                result['source'] = 'social_links'
                return result
        
        # Search for LinkedIn
        logger.info(f"[{index+1}] Searching: {company_name[:40]}...")
        linkedin_url = self.search_linkedin_page(company_name, website_url)
        
        if linkedin_url and self.is_valid_url(linkedin_url):
            linkedin_data = self.scrape_linkedin_page(linkedin_url)
            result['linkedin_url'] = linkedin_url
            result.update(linkedin_data)
            result['linkedin_status'] = 'found'
            result['source'] = 'search'
            logger.info(f"[OK] Found LinkedIn for {company_name[:30]}...")
        
        return result
    
    def run(self) -> pd.DataFrame:
        logger.info("Starting LinkedIn Intelligence Agent with Playwright...")
        self.load_data()
        
        total = len(self.df)
        found_count = 0
        
        for index, row in self.df.iterrows():
            try:
                result = self.process_company(row, index)
                self.results.append(result)
                
                if result['linkedin_status'] == 'found':
                    found_count += 1
                
                if (index + 1) % 20 == 0:
                    logger.info(f"Progress: {index + 1}/{total}. Found: {found_count}")
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error on row {index}: {e}")
                continue
        
        results_df = pd.DataFrame(self.results)
        results_df.to_csv(self.output_file, index=False, encoding='utf-8')
        
        logger.info("="*70)
        logger.info(f"COMPLETED! Total: {len(results_df)} | Found: {found_count}")
        logger.info(f"Output: {self.output_file}")
        logger.info("="*70)
        
        return results_df


def main():
    try:
        agent = LinkedInIntelligenceAgent()
        results = agent.run()
        
        print("\n" + "="*70)
        print("LINKEDIN INTELLIGENCE AGENT - SUMMARY")
        print("="*70)
        found = results[results['linkedin_status'] == 'found']
        print(f"Total: {len(results)}")
        print(f"LinkedIn Found: {len(found)}")
        print(f"Output: {OUTPUT_FILE}")
        print("="*70)
        
        if not found.empty:
            print("\nSample:")
            cols = ['company_name', 'linkedin_url', 'linkedin_industry', 'linkedin_company_size']
            print(found[cols].head(5).to_string(index=False))
        
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()