"""
Module 5: AI Website Analysis Agent
Purpose: Analyze company websites and detect business opportunities
Author: AI Sales Intelligence & Lead Generation Agent
Date: 2026-07-10

PDF Requirements:
Detect: Outdated Website, Poor UI/UX, Missing SEO, Weak Branding,
        No Mobile Application, No AI Features, No Automation,
        Missing Live Chat, Missing Call-to-Action, Slow Website,
        Poor User Experience

Generate AI Recommendations: Website Redesign, Mobile Application,
        SEO Optimization, AI Chatbot, AI Automation, SaaS Platform,
        CRM, ERP, Business Automation, UI/UX Improvements, Graphic Design
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import re
import time
import json
from typing import Dict, Optional, List, Any
from urllib.parse import urlparse
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
        logging.FileHandler('logs/website_analysis_agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_PROCESSED / "website_intelligence.csv"
OUTPUT_FILE = DATA_PROCESSED / "website_analysis.csv"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}
REQUEST_TIMEOUT = 10
MAX_RETRIES = 2


class WebsiteAnalysisAgent:
    """
    AI Website Analysis Agent.
    
    Analyzes company websites and detects:
    - Outdated Website, Poor UI/UX, Missing SEO, Weak Branding
    - No Mobile Application, No AI Features, No Automation
    - Missing Live Chat, Missing Call-to-Action, Slow Website
    - Poor User Experience
    
    Generates AI recommendations:
    - Website Redesign, Mobile Application, SEO Optimization
    - AI Chatbot, AI Automation, SaaS Platform, CRM, ERP
    - Business Automation, UI/UX Improvements, Graphic Design
    """
    
    def __init__(self, input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE):
        self.input_file = input_file
        self.output_file = output_file
        self.df = None
        self.results = []
        
        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("="*70)
        logger.info("AI WEBSITE ANALYSIS AGENT - MODULE 5")
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
            logger.error(f"File not found: {self.input_file}")
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
    
    def analyze_website(self, url: str, html: str, row: pd.Series) -> Dict:
        """
        Analyze website and detect issues.
        
        Returns:
            Dictionary with analysis results and recommendations
        """
        analysis = {
            'website_url': url,
            'company_name': row.get('company_name', 'Unknown'),
            'has_mobile_app': False,
            'has_ai_features': False,
            'has_automation': False,
            'has_live_chat': False,
            'has_call_to_action': False,
            'has_ssl': row.get('ssl', False),
            'has_blog': row.get('blog', False),
            'has_contact_form': row.get('contact_form', False),
            'has_social_links': False,
            'has_services': False,
            'has_portfolio': False,
            'has_careers': row.get('careers', False),
            'is_outdated': False,
            'poor_ui_ux': False,
            'missing_seo': False,
            'weak_branding': False,
            'slow_website': False,
            'poor_user_experience': False,
            'ai_recommendations': [],
            'score': 0,
            'status': 'analyzed'
        }
        
        if not html:
            analysis['status'] = 'fetch_failed'
            return analysis
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text().lower()
        
        # ============================================================
        # DETECTION CHECKS
        # ============================================================
        
        # 1. Mobile App Detection
        mobile_keywords = ['app', 'download', 'play store', 'app store', 'ios', 'android', 'mobile app']
        if any(keyword in text for keyword in mobile_keywords):
            analysis['has_mobile_app'] = True
        
        # 2. AI Features Detection
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 
                       'chatbot', 'llm', 'gpt', 'openai', 'tensorflow', 'pytorch', 'automation']
        if any(keyword in text for keyword in ai_keywords):
            analysis['has_ai_features'] = True
        
        # 3. Automation Detection
        automation_keywords = ['automation', 'auto', 'workflow', 'process automation', 'rpa']
        if any(keyword in text for keyword in automation_keywords):
            analysis['has_automation'] = True
        
        # 4. Live Chat Detection
        live_chat_keywords = ['live chat', 'chat with us', 'chat now', 'chat widget', 'intercom', 'drift']
        if any(keyword in text for keyword in live_chat_keywords):
            analysis['has_live_chat'] = True
        
        # 5. Call-to-Action Detection
        cta_keywords = ['contact us', 'get started', 'request quote', 'book now', 'sign up', 
                        'learn more', 'get a quote', 'free consultation', 'contact now']
        if any(keyword in text for keyword in cta_keywords):
            analysis['has_call_to_action'] = True
        
        # 6. Social Links Detection
        social_keywords = ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube']
        if any(keyword in text for keyword in social_keywords):
            analysis['has_social_links'] = True
        
        # 7. Services Detection
        if 'services' in text or 'what we do' in text:
            analysis['has_services'] = True
        
        # 8. Portfolio/Work Detection
        portfolio_keywords = ['portfolio', 'work', 'projects', 'case studies', 'our work']
        if any(keyword in text for keyword in portfolio_keywords):
            analysis['has_portfolio'] = True
        
        # ============================================================
        # ISSUE DETECTION
        # ============================================================
        
        # 9. Outdated Website Detection
        outdated_keywords = ['2022', '2023', 'old', 'legacy', 'classic']
        if any(keyword in text for keyword in outdated_keywords) or not analysis['has_blog']:
            analysis['is_outdated'] = True
        
        # 10. Poor UI/UX Detection
        ui_ux_keywords = ['old design', 'bad design', 'poor navigation', 'outdated interface']
        if any(keyword in text for keyword in ui_ux_keywords) or not analysis['has_social_links']:
            analysis['poor_ui_ux'] = True
        
        # 11. Missing SEO Detection
        meta_desc = soup.find('meta', {'name': 'description'})
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if not meta_desc or not meta_keywords:
            analysis['missing_seo'] = True
        
        # 12. Weak Branding Detection
        branding_keywords = ['logo', 'brand', 'identity', 'mission', 'vision']
        if not any(keyword in text for keyword in branding_keywords) or not analysis['has_social_links']:
            analysis['weak_branding'] = True
        
        # 13. Slow Website Detection (check page size)
        page_size = len(html)
        if page_size > 2000000:  # >2MB
            analysis['slow_website'] = True
        
        # 14. Poor User Experience Detection
        if analysis['poor_ui_ux'] or analysis['missing_seo'] or analysis['weak_branding']:
            analysis['poor_user_experience'] = True
        
        # ============================================================
        # AI RECOMMENDATIONS GENERATION
        # ============================================================
        
        recommendations = []
        
        # Check which services SoftCr8ors offers that this company needs
        softcr8ors_services = [
            ('website_redesign', 'Website Redesign', analysis['is_outdated'] or analysis['poor_ui_ux']),
            ('mobile_app', 'Mobile Application', not analysis['has_mobile_app']),
            ('seo_optimization', 'SEO Optimization', analysis['missing_seo']),
            ('ai_chatbot', 'AI Chatbot', not analysis['has_live_chat']),
            ('ai_automation', 'AI Automation', not analysis['has_automation']),
            ('saas_platform', 'SaaS Platform', not analysis['has_mobile_app']),
            ('crm', 'CRM Development', not analysis['has_services']),
            ('erp', 'ERP Development', not analysis['has_services']),
            ('business_automation', 'Business Automation', not analysis['has_automation']),
            ('ui_ux_improvements', 'UI/UX Improvements', analysis['poor_ui_ux']),
            ('graphic_design', 'Graphic Design', analysis['weak_branding']),
        ]
        
        for key, service, condition in softcr8ors_services:
            if condition:
                recommendations.append(service)
        
        # Limit to top 5 recommendations
        analysis['ai_recommendations'] = recommendations[:5]
        
        # ============================================================
        # CALCULATE SCORE
        # ============================================================
        
        # Score: Higher is better (more features = better website)
        score = 0
        score += 10 if analysis['has_mobile_app'] else 0
        score += 10 if analysis['has_ai_features'] else 0
        score += 10 if analysis['has_automation'] else 0
        score += 10 if analysis['has_live_chat'] else 0
        score += 10 if analysis['has_call_to_action'] else 0
        score += 10 if analysis['has_ssl'] else 0
        score += 10 if analysis['has_blog'] else 0
        score += 10 if analysis['has_contact_form'] else 0
        score += 10 if analysis['has_social_links'] else 0
        score += 10 if analysis['has_services'] else 0
        
        analysis['score'] = score
        
        # ============================================================
        # STATUS
        # ============================================================
        
        if score >= 70:
            analysis['status'] = 'good_website'
        elif score >= 40:
            analysis['status'] = 'needs_improvement'
        else:
            analysis['status'] = 'needs_redesign'
        
        return analysis
    
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
        
        logger.info(f"[{index+1}/{len(self.df)}] Analyzing: {company_name[:40]}...")
        
        html = self.fetch_page(website_url)
        analysis = self.analyze_website(website_url, html, row)
        
        # Add company info
        analysis['company_name'] = company_name
        
        logger.info(f"[OK] Score: {analysis['score']}/100, Issues: {len(analysis['ai_recommendations'])}")
        
        return analysis
    
    def run(self) -> pd.DataFrame:
        """Run the Website Analysis Agent."""
        logger.info("Starting AI Website Analysis Agent...")
        self.load_data()
        
        total = len(self.df)
        analyzed_count = 0
        
        for index, row in self.df.iterrows():
            try:
                result = self.process_company(row, index)
                self.results.append(result)
                
                if result['status'] != 'fetch_failed':
                    analyzed_count += 1
                
                if (index + 1) % 20 == 0:
                    logger.info(f"Progress: {index + 1}/{total}")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error on row {index}: {e}")
                continue
        
        results_df = pd.DataFrame(self.results)
        results_df.to_csv(self.output_file, index=False, encoding='utf-8')
        
        logger.info("="*70)
        logger.info(f"COMPLETED! Total: {len(results_df)} | Analyzed: {analyzed_count}")
        logger.info(f"Output: {self.output_file}")
        logger.info("="*70)
        
        return results_df


def main():
    try:
        agent = WebsiteAnalysisAgent()
        results = agent.run()
        
        print("\n" + "="*70)
        print("AI WEBSITE ANALYSIS AGENT - SUMMARY")
        print("="*70)
        print(f"Total Companies: {len(results)}")
        print(f"Analyzed: {len(results[results['status'] != 'fetch_failed'])}")
        print(f"Good Websites: {len(results[results['status'] == 'good_website'])}")
        print(f"Need Improvement: {len(results[results['status'] == 'needs_improvement'])}")
        print(f"Need Redesign: {len(results[results['status'] == 'needs_redesign'])}")
        print(f"Output: {OUTPUT_FILE}")
        print("="*70)
        
        # Show sample recommendations
        print("\nSample AI Recommendations:")
        sample = results[results['ai_recommendations'].apply(lambda x: len(x) > 0)].head(5)
        for _, row in sample.iterrows():
            print(f"\n{row['company_name']}:")
            print(f"  Score: {row['score']}/100")
            print(f"  Recommendations: {', '.join(row['ai_recommendations'])}")
        
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()