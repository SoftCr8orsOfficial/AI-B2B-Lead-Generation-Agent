"""
Module 4: Decision Maker Finder
Purpose: Find publicly available decision-makers (Founder, CEO, CTO, etc.)
Author: AI Sales Intelligence & Lead Generation Agent
Date: 2026-07-10

PDF Requirements:
Find: Founder, CEO, CTO, COO, Owner, Managing Director, VP Engineering, VP Technology, Director, Head of Engineering
Collect: Full Name, Job Title, Public LinkedIn Profile URL
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import re
import time
import json
from typing import Dict, Optional, List, Any, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime
import sys
from pathlib import Path
import codecs

# Configure logging
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/decision_maker_agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_PROCESSED / "website_intelligence.csv"
OUTPUT_FILE = DATA_PROCESSED / "decision_makers.csv"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}
REQUEST_TIMEOUT = 15
MAX_RETRIES = 2


class DecisionMakerFinder:
    """
    Decision Maker Finder Agent.
    
    Finds publicly available decision-makers:
    - Founder, CEO, CTO, COO, Owner
    - Managing Director, VP Engineering, VP Technology
    - Director, Head of Engineering
    """
    
    def __init__(self, input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE):
        self.input_file = input_file
        self.output_file = output_file
        self.df = None
        self.results = []
        
        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("="*70)
        logger.info("DECISION MAKER FINDER - MODULE 4")
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
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch webpage with retry."""
        if not self.is_valid_url(url):
            return None
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                if response.status_code == 200:
                    return response.text
            except:
                time.sleep(2)
        return None
    
    def find_decision_makers_from_website(self, url: str, html: str) -> List[Dict]:
        """
        Find decision-makers from website content.
        
        Looks for: Founder, CEO, CTO, COO, Owner, Managing Director,
        VP Engineering, VP Technology, Director, Head of Engineering
        """
        decision_makers = []
        
        if not html:
            return decision_makers
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # Decision maker patterns
        patterns = {
            'Founder': [r'Founder', r'Co-Founder', r'Co-founder'],
            'CEO': [r'CEO', r'Chief Executive Officer'],
            'CTO': [r'CTO', r'Chief Technology Officer'],
            'COO': [r'COO', r'Chief Operating Officer'],
            'Owner': [r'Owner', r'Proprietor'],
            'Managing Director': [r'Managing Director', r'MD'],
            'VP Engineering': [r'VP Engineering', r'Vice President Engineering'],
            'VP Technology': [r'VP Technology', r'Vice President Technology'],
            'Director': [r'Director', r'Head of'],
            'Head of Engineering': [r'Head of Engineering', r'Engineering Head'],
        }
        
        # Find team section
        team_keywords = ['team', 'leadership', 'management', 'about', 'our team', 'meet the team']
        team_html = None
        
        for keyword in team_keywords:
            if keyword in text.lower():
                # Try to find team section
                for tag in soup.find_all(['section', 'div', 'article']):
                    if keyword in tag.get_text().lower():
                        team_html = str(tag)
                        break
                if team_html:
                    break
        
        # If no team section found, use full text
        search_text = team_html if team_html else text
        
        # Find names with titles
        for title, title_patterns in patterns.items():
            for pattern in title_patterns:
                # Look for pattern: "Name - Title" or "Name, Title"
                # Format 1: Name - Title
                matches = re.findall(
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[-–,]\s*' + pattern,
                    search_text,
                    re.IGNORECASE
                )
                for match in matches:
                    if len(match) > 1 and len(match) < 50:
                        decision_makers.append({
                            'title': title,
                            'full_name': match.strip(),
                            'linkedin_url': None
                        })
                
                # Format 2: Title: Name
                matches = re.findall(
                    pattern + r'\s*[::]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                    search_text,
                    re.IGNORECASE
                )
                for match in matches:
                    if len(match) > 1 and len(match) < 50:
                        decision_makers.append({
                            'title': title,
                            'full_name': match.strip(),
                            'linkedin_url': None
                        })
        
        # Remove duplicates
        seen = set()
        unique_makers = []
        for maker in decision_makers:
            key = f"{maker['full_name']}_{maker['title']}"
            if key not in seen:
                seen.add(key)
                unique_makers.append(maker)
        
        return unique_makers
    
    def find_linkedin_for_decision_maker(self, full_name: str, company_name: str) -> Optional[str]:
        """Search LinkedIn for decision maker."""
        if not full_name or len(full_name) < 2:
            return None
        
        search_terms = [
            f"{full_name} {company_name} LinkedIn",
            f"{full_name} LinkedIn",
        ]
        
        for search_term in search_terms:
            try:
                query = search_term.replace(" ", "+")
                search_url = f"https://www.google.com/search?q={query}"
                
                response = requests.get(search_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'linkedin.com/in/' in href:
                        # Extract clean URL
                        if href.startswith('/url?q='):
                            match = re.search(r'/url\?q=([^&]+)', href)
                            if match:
                                return match.group(1)
                        elif href.startswith('https://www.linkedin.com/in/'):
                            return href
                time.sleep(1)
            except:
                continue
        
        return None
    
    def process_company(self, row: pd.Series, index: int) -> Dict:
        """Process a single company."""
        company_name = row.get('company_name', 'Unknown')
        if pd.isna(company_name):
            company_name = 'Unknown'
        else:
            company_name = str(company_name).strip()
        
        website_url = row.get('website_url', '')
        if pd.isna(website_url):
            website_url = ''
        
        result = {
            'company_name': company_name,
            'website_url': website_url,
            'founder': None,
            'founder_linkedin': None,
            'ceo': None,
            'ceo_linkedin': None,
            'cto': None,
            'cto_linkedin': None,
            'coo': None,
            'coo_linkedin': None,
            'owner': None,
            'owner_linkedin': None,
            'managing_director': None,
            'managing_director_linkedin': None,
            'vp_engineering': None,
            'vp_engineering_linkedin': None,
            'vp_technology': None,
            'vp_technology_linkedin': None,
            'director': None,
            'director_linkedin': None,
            'head_of_engineering': None,
            'head_of_engineering_linkedin': None,
            'decision_makers_found': 0,
            'status': 'not_found'
        }
        
        # Fetch website
        logger.info(f"[{index+1}/{len(self.df)}] Processing: {company_name[:40]}...")
        html = self.fetch_page(website_url)
        
        if not html:
            logger.warning(f"Failed to fetch {website_url}")
            result['status'] = 'fetch_failed'
            return result
        
        # Find decision makers
        makers = self.find_decision_makers_from_website(website_url, html)
        
        if not makers:
            logger.info(f"No decision makers found for {company_name[:30]}...")
            result['status'] = 'no_makers'
            return result
        
        # Map to result fields
        title_mapping = {
            'Founder': ('founder', 'founder_linkedin'),
            'CEO': ('ceo', 'ceo_linkedin'),
            'CTO': ('cto', 'cto_linkedin'),
            'COO': ('coo', 'coo_linkedin'),
            'Owner': ('owner', 'owner_linkedin'),
            'Managing Director': ('managing_director', 'managing_director_linkedin'),
            'VP Engineering': ('vp_engineering', 'vp_engineering_linkedin'),
            'VP Technology': ('vp_technology', 'vp_technology_linkedin'),
            'Director': ('director', 'director_linkedin'),
            'Head of Engineering': ('head_of_engineering', 'head_of_engineering_linkedin'),
        }
        
        for maker in makers:
            title = maker.get('title', '')
            name = maker.get('full_name', '')
            if title in title_mapping:
                name_field, linkedin_field = title_mapping[title]
                if not result[name_field]:  # Only set if not already set
                    result[name_field] = name
                    # Try to find LinkedIn
                    linkedin = self.find_linkedin_for_decision_maker(name, company_name)
                    if linkedin:
                        result[linkedin_field] = linkedin
                    result['decision_makers_found'] += 1
        
        result['status'] = 'found' if result['decision_makers_found'] > 0 else 'no_makers'
        
        logger.info(f"[OK] Found {result['decision_makers_found']} decision makers for {company_name[:30]}...")
        
        return result
    
    def run(self) -> pd.DataFrame:
        """Run the Decision Maker Finder."""
        logger.info("Starting Decision Maker Finder...")
        
        self.load_data()
        
        total = len(self.df)
        found_count = 0
        
        for index, row in self.df.iterrows():
            try:
                result = self.process_company(row, index)
                self.results.append(result)
                
                if result['status'] == 'found':
                    found_count += 1
                
                if (index + 1) % 20 == 0:
                    logger.info(f"Progress: {index + 1}/{total}. Found: {found_count}")
                
                time.sleep(1.5)
                
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
        agent = DecisionMakerFinder()
        results = agent.run()
        
        print("\n" + "="*70)
        print("DECISION MAKER FINDER - SUMMARY")
        print("="*70)
        print(f"Total Companies: {len(results)}")
        print(f"Found Decision Makers: {len(results[results['status'] == 'found'])}")
        print(f"Output: {OUTPUT_FILE}")
        print("="*70)
        
        found = results[results['status'] == 'found']
        if not found.empty:
            print("\nSample Decision Makers Found:")
            cols = ['company_name', 'founder', 'ceo', 'cto', 'decision_makers_found']
            print(found[cols].head(5).to_string(index=False))
        
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()