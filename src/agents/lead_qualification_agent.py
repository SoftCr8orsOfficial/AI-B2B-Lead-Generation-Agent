"""
Module 6: AI Lead Qualification Agent
Purpose: Score and qualify leads based on multiple intelligence signals
Author: AI Sales Intelligence & Lead Generation Agent
Date: 2026-07-10

PDF Requirements:
Lead Scoring Rules:
- Website Available → +10
- Business Email → +10
- Phone Number → +10
- Contact Form → +10
- LinkedIn Company → +10
- Founder Found → +15
- CEO Found → +15
- Priority Country → +20
- Company Size >20 Employees → +10

Priority Levels:
- High Priority (70-100)
- Medium Priority (40-69)
- Low Priority (0-39)
"""

import pandas as pd
import logging
import sys
import re
from pathlib import Path
import codecs
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any  # <-- ADDED

# Configure logging
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/lead_qualification_agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"

# Input files from previous modules
WEBSITE_FILE = DATA_PROCESSED / "website_intelligence.csv"
LINKEDIN_FILE = DATA_PROCESSED / "linkedin_data.csv"
DECISION_MAKERS_FILE = DATA_PROCESSED / "decision_makers.csv"
WEBSITE_ANALYSIS_FILE = DATA_PROCESSED / "website_analysis.csv"
OUTPUT_FILE = DATA_PROCESSED / "qualified_leads.csv"

# Priority Countries (from PDF)
PRIORITY_COUNTRIES = [
    "United States", "USA", "US",
    "Canada",
    "United Kingdom", "UK",
    "Australia",
    "Germany",
    "Netherlands",
    "United Arab Emirates", "UAE",
    "Saudi Arabia",
    "Qatar",
    "Kuwait",
    "Oman",
    "Singapore",
    "Pakistan"
]

# SoftCr8ors services (from PDF) - for recommendation logic
SOFTCR8ORS_SERVICES = [
    "Custom Software Development",
    "Web Development",
    "Android Application Development",
    "iOS Application Development",
    "AI Development",
    "AI Agents",
    "Machine Learning Solutions",
    "SaaS Development",
    "CRM Development",
    "ERP Development",
    "Business Automation",
    "API Development",
    "MVP Development",
    "UI/UX Design",
    "Graphic Design",
    "Search Engine Optimization (SEO)"
]


class LeadQualificationAgent:
    """
    AI Lead Qualification Agent.
    
    Scores leads based on multiple intelligence signals:
    - Website availability, emails, phones, contact form
    - LinkedIn presence, decision makers
    - Priority countries, company size
    """
    
    def __init__(
        self,
        website_file: Path = WEBSITE_FILE,
        linkedin_file: Path = LINKEDIN_FILE,
        decision_makers_file: Path = DECISION_MAKERS_FILE,
        analysis_file: Path = WEBSITE_ANALYSIS_FILE,
        output_file: Path = OUTPUT_FILE
    ):
        self.website_file = website_file
        self.linkedin_file = linkedin_file
        self.decision_makers_file = decision_makers_file
        self.analysis_file = analysis_file
        self.output_file = output_file
        
        self.df_website = None
        self.df_linkedin = None
        self.df_decision = None
        self.df_analysis = None
        self.results = []
        
        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("="*70)
        logger.info("AI LEAD QUALIFICATION AGENT - MODULE 6")
        logger.info("="*70)
        logger.info(f"Output file: {self.output_file}")
    
    def is_valid_value(self, val: Any) -> bool:
        """Check if value exists and is not empty/NaN."""
        if val is None:
            return False
        if isinstance(val, float):
            if pd.isna(val):
                return False
        if isinstance(val, str):
            if val.strip() == '' or val.lower() in ['nan', 'none', 'null', '']:
                return False
        if isinstance(val, list):
            return len(val) > 0
        if isinstance(val, bool):
            return val
        return True
    
    def load_data(self) -> None:
        """Load all data from previous modules."""
        logger.info("Loading data from previous modules...")
        
        try:
            self.df_website = pd.read_csv(self.website_file)
            logger.info(f"Loaded website data: {len(self.df_website)} records")
        except Exception as e:
            logger.warning(f"Could not load website data: {e}")
            self.df_website = pd.DataFrame()
        
        try:
            self.df_linkedin = pd.read_csv(self.linkedin_file)
            logger.info(f"Loaded LinkedIn data: {len(self.df_linkedin)} records")
        except Exception as e:
            logger.warning(f"Could not load LinkedIn data: {e}")
            self.df_linkedin = pd.DataFrame()
        
        try:
            self.df_decision = pd.read_csv(self.decision_makers_file)
            logger.info(f"Loaded decision maker data: {len(self.df_decision)} records")
        except Exception as e:
            logger.warning(f"Could not load decision maker data: {e}")
            self.df_decision = pd.DataFrame()
        
        try:
            self.df_analysis = pd.read_csv(self.analysis_file)
            logger.info(f"Loaded website analysis data: {len(self.df_analysis)} records")
        except Exception as e:
            logger.warning(f"Could not load website analysis data: {e}")
            self.df_analysis = pd.DataFrame()
    
    def get_company_data(self, website_url: str, company_name: str) -> Dict[str, Any]:
        """Get all data for a company from merged DataFrames."""
        data = {
            'website_url': website_url,
            'company_name': company_name,
            # Website data
            'has_website': False,
            'has_business_email': False,
            'has_contact_email': False,
            'has_phone': False,
            'has_whatsapp': False,
            'has_contact_form': False,
            'has_ssl': False,
            'has_blog': False,
            'has_careers': False,
            'has_social_links': False,
            'technologies': [],
            # LinkedIn data
            'has_linkedin': False,
            'linkedin_industry': None,
            'linkedin_company_size': None,
            'linkedin_employee_count': None,
            'linkedin_headquarters': None,
            # Decision maker data
            'has_founder': False,
            'has_ceo': False,
            'has_cto': False,
            'has_coo': False,
            'has_owner': False,
            'has_managing_director': False,
            'has_director': False,
            'has_head_engineering': False,
            'decision_makers_count': 0,
            # Analysis data
            'website_score': 0,
            'has_mobile_app': False,
            'has_ai_features': False,
            'has_automation': False,
            'has_live_chat': False,
            'has_call_to_action': False,
            'is_outdated': False,
            'poor_ui_ux': False,
            'missing_seo': False,
            'weak_branding': False,
            'ai_recommendations': [],
            # Location
            'location': '',
            'source': '',
            # Lead qualification
            'lead_score': 0,
            'priority_level': 'Low',
            'qualification_reasons': [],
            'ai_recommendation': None
        }
        
        # Get website data
        if not self.df_website.empty:
            website_rows = self.df_website[
                (self.df_website['website_url'] == website_url) |
                (self.df_website['company_name'] == company_name)
            ]
            if not website_rows.empty:
                row = website_rows.iloc[0]
                data['has_website'] = self.is_valid_url(website_url)
                data['has_business_email'] = self.is_valid_value(row.get('business_emails', []))
                data['has_contact_email'] = self.is_valid_value(row.get('contact_emails', []))
                data['has_phone'] = self.is_valid_value(row.get('phones', []))
                data['has_whatsapp'] = self.is_valid_value(row.get('whatsapp', None))
                data['has_contact_form'] = self.is_valid_value(row.get('contact_form', False))
                data['has_ssl'] = self.is_valid_value(row.get('ssl', False))
                data['has_blog'] = self.is_valid_value(row.get('blog', False))
                data['has_careers'] = self.is_valid_value(row.get('careers', False))
                data['technologies'] = row.get('technologies', [])
                if isinstance(data['technologies'], str):
                    try:
                        data['technologies'] = eval(data['technologies'])
                    except:
                        data['technologies'] = []
                data['location'] = row.get('location', '')
                data['source'] = row.get('source', '')
                
                # Check social links
                social_links = row.get('social_links', {})
                if isinstance(social_links, str):
                    try:
                        social_links = eval(social_links)
                    except:
                        social_links = {}
                data['has_social_links'] = len(social_links) > 0 if isinstance(social_links, dict) else False
        
        # Get LinkedIn data
        if not self.df_linkedin.empty:
            linkedin_rows = self.df_linkedin[
                (self.df_linkedin['website_url'] == website_url) |
                (self.df_linkedin['company_name'] == company_name)
            ]
            if not linkedin_rows.empty:
                row = linkedin_rows.iloc[0]
                if row.get('linkedin_status') == 'found':
                    data['has_linkedin'] = True
                    data['linkedin_industry'] = row.get('linkedin_industry', None)
                    data['linkedin_company_size'] = row.get('linkedin_company_size', None)
                    data['linkedin_employee_count'] = row.get('linkedin_employee_count', None)
                    data['linkedin_headquarters'] = row.get('linkedin_headquarters', None)
        
        # Get decision maker data
        if not self.df_decision.empty:
            decision_rows = self.df_decision[
                (self.df_decision['website_url'] == website_url) |
                (self.df_decision['company_name'] == company_name)
            ]
            if not decision_rows.empty:
                row = decision_rows.iloc[0]
                data['has_founder'] = self.is_valid_value(row.get('founder', None))
                data['has_ceo'] = self.is_valid_value(row.get('ceo', None))
                data['has_cto'] = self.is_valid_value(row.get('cto', None))
                data['has_coo'] = self.is_valid_value(row.get('coo', None))
                data['has_owner'] = self.is_valid_value(row.get('owner', None))
                data['has_managing_director'] = self.is_valid_value(row.get('managing_director', None))
                data['has_director'] = self.is_valid_value(row.get('director', None))
                data['has_head_engineering'] = self.is_valid_value(row.get('head_of_engineering', None))
                data['decision_makers_count'] = row.get('decision_makers_found', 0) or 0
        
        # Get website analysis data
        if not self.df_analysis.empty:
            analysis_rows = self.df_analysis[
                (self.df_analysis['website_url'] == website_url) |
                (self.df_analysis['company_name'] == company_name)
            ]
            if not analysis_rows.empty:
                row = analysis_rows.iloc[0]
                data['website_score'] = row.get('score', 0) or 0
                data['has_mobile_app'] = row.get('has_mobile_app', False)
                data['has_ai_features'] = row.get('has_ai_features', False)
                data['has_automation'] = row.get('has_automation', False)
                data['has_live_chat'] = row.get('has_live_chat', False)
                data['has_call_to_action'] = row.get('has_call_to_action', False)
                data['is_outdated'] = row.get('is_outdated', False)
                data['poor_ui_ux'] = row.get('poor_ui_ux', False)
                data['missing_seo'] = row.get('missing_seo', False)
                data['weak_branding'] = row.get('weak_branding', False)
                ai_recs = row.get('ai_recommendations', [])
                if isinstance(ai_recs, str):
                    try:
                        ai_recs = eval(ai_recs)
                    except:
                        ai_recs = []
                data['ai_recommendations'] = ai_recs
        
        return data
    
    def is_valid_url(self, url: Any) -> bool:
        """Check if URL is valid."""
        if not url:
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
        return True
    
    def is_priority_country(self, location: str) -> bool:
        """Check if company is in priority country."""
        if not location:
            return False
        for country in PRIORITY_COUNTRIES:
            if country.lower() in location.lower():
                return True
        return False
    
    def get_company_size(self, data: Dict[str, Any]) -> int:
        """Extract company size from LinkedIn data."""
        size = data.get('linkedin_company_size')
        employees = data.get('linkedin_employee_count')
        
        if employees:
            try:
                clean = str(employees).replace(',', '').replace('+', '').strip()
                if 'K' in clean.upper():
                    clean = clean.upper().replace('K', '')
                    return int(float(clean) * 1000)
                if 'M' in clean.upper():
                    clean = clean.upper().replace('M', '')
                    return int(float(clean) * 1000000)
                return int(float(clean))
            except:
                pass
        
        if size:
            try:
                match = re.search(r'(\d+)', str(size))
                if match:
                    return int(match.group(1))
            except:
                pass
        
        return 0
    
    def calculate_lead_score(self, data: Dict[str, Any]) -> Tuple[int, List[str]]:
        """
        Calculate lead score based on PDF rules.
        
        Returns:
            Tuple of (score, reasons)
        """
        score = 0
        reasons = []
        
        # Rule 1: Website Available → +10
        if data.get('has_website'):
            score += 10
            reasons.append("Website available (+10)")
        
        # Rule 2: Business Email → +10
        if data.get('has_business_email'):
            score += 10
            reasons.append("Business email found (+10)")
        
        # Rule 3: Contact Email → +10
        if data.get('has_contact_email'):
            score += 10
            reasons.append("Contact email found (+10)")
        
        # Rule 4: Phone Number → +10
        if data.get('has_phone'):
            score += 10
            reasons.append("Phone number found (+10)")
        
        # Rule 5: WhatsApp Number → +5 (bonus)
        if data.get('has_whatsapp'):
            score += 5
            reasons.append("WhatsApp number found (+5)")
        
        # Rule 6: Contact Form → +10
        if data.get('has_contact_form'):
            score += 10
            reasons.append("Contact form exists (+10)")
        
        # Rule 7: LinkedIn Company → +10
        if data.get('has_linkedin'):
            score += 10
            reasons.append("LinkedIn company found (+10)")
        
        # Rule 8: Founder Found → +15
        if data.get('has_founder'):
            score += 15
            reasons.append("Founder found (+15)")
        
        # Rule 9: CEO Found → +15
        if data.get('has_ceo'):
            score += 15
            reasons.append("CEO found (+15)")
        
        # Rule 10: Other Decision Makers → +5 each (bonus)
        if data.get('has_cto'):
            score += 5
            reasons.append("CTO found (+5)")
        if data.get('has_coo'):
            score += 5
            reasons.append("COO found (+5)")
        if data.get('has_owner'):
            score += 5
            reasons.append("Owner found (+5)")
        if data.get('has_managing_director'):
            score += 5
            reasons.append("Managing Director found (+5)")
        if data.get('has_director'):
            score += 5
            reasons.append("Director found (+5)")
        if data.get('has_head_engineering'):
            score += 5
            reasons.append("Head of Engineering found (+5)")
        
        # Rule 11: Priority Country → +20
        if self.is_priority_country(data.get('location', '')):
            score += 20
            reasons.append("Priority country (+20)")
        
        # Rule 12: Company Size >20 Employees → +10
        company_size = self.get_company_size(data)
        if company_size > 20:
            score += 10
            reasons.append(f"Company size {company_size} > 20 employees (+10)")
        elif company_size > 0:
            reasons.append(f"Company size {company_size} employees")
        
        # Bonus: SSL Certificate → +5
        if data.get('has_ssl'):
            score += 5
            reasons.append("SSL certificate (+5)")
        
        # Bonus: Blog → +5
        if data.get('has_blog'):
            score += 5
            reasons.append("Blog exists (+5)")
        
        # Bonus: Social Links → +5
        if data.get('has_social_links'):
            score += 5
            reasons.append("Social media links (+5)")
        
        # Bonus: Mobile App → +5
        if data.get('has_mobile_app'):
            score += 5
            reasons.append("Mobile app detected (+5)")
        
        # Bonus: AI Features → +5
        if data.get('has_ai_features'):
            score += 5
            reasons.append("AI features detected (+5)")
        
        # Bonus: Automation → +5
        if data.get('has_automation'):
            score += 5
            reasons.append("Automation detected (+5)")
        
        # Bonus: Live Chat → +5
        if data.get('has_live_chat'):
            score += 5
            reasons.append("Live chat detected (+5)")
        
        # Cap score at 100
        score = min(score, 100)
        
        return score, reasons
    
    def get_priority_level(self, score: int) -> str:
        """Get priority level based on score."""
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Medium"
        else:
            return "Low"
    
    def generate_ai_recommendation(self, data: Dict[str, Any]) -> str:
        """Generate AI recommendation based on analysis and score."""
        recommendations = []
        
        # Check for SoftCr8ors service opportunities
        if data.get('poor_ui_ux') or data.get('weak_branding'):
            recommendations.append("UI/UX Design & Branding")
        
        if data.get('missing_seo'):
            recommendations.append("SEO Optimization")
        
        if not data.get('has_mobile_app'):
            recommendations.append("Mobile Application Development")
        
        if not data.get('has_ai_features'):
            recommendations.append("AI Development / AI Agents")
        
        if not data.get('has_automation'):
            recommendations.append("Business Automation")
        
        if not data.get('has_live_chat'):
            recommendations.append("AI Chatbot Integration")
        
        if data.get('is_outdated'):
            recommendations.append("Website Redesign")
        
        if not data.get('has_blog'):
            recommendations.append("Content Marketing / Blog")
        
        if not data.get('has_social_links'):
            recommendations.append("Social Media Marketing")
        
        # Add from website analysis recommendations
        ai_recs = data.get('ai_recommendations', [])
        if ai_recs:
            for rec in ai_recs:
                if rec and rec not in recommendations:
                    recommendations.append(rec)
        
        # If no specific recommendations, suggest general
        if not recommendations:
            recommendations.append("Custom Software Development")
            recommendations.append("Digital Marketing")
        
        # Limit to top 3
        return ", ".join(recommendations[:3])
    
    def get_lead_insight(self, data: Dict[str, Any]) -> str:
        """Generate lead insight summary."""
        insights = []
        
        if data.get('has_founder'):
            insights.append("Founder identified — direct decision-maker access")
        if data.get('has_ceo'):
            insights.append("CEO identified — executive-level contact")
        if data.get('has_linkedin'):
            insights.append("LinkedIn presence confirmed — verified company")
        if data.get('has_business_email') or data.get('has_contact_email'):
            insights.append("Email communication channel available")
        if data.get('has_phone'):
            insights.append("Phone contact available")
        if self.is_priority_country(data.get('location', '')):
            insights.append("Located in priority market")
        if data.get('has_ai_features'):
            insights.append("Already using AI — potential for advanced solutions")
        if not data.get('has_mobile_app'):
            insights.append("Mobile app opportunity identified")
        if data.get('poor_ui_ux') or data.get('weak_branding'):
            insights.append("Branding/UI upgrade potential")
        
        if not insights:
            return "Basic lead — further qualification recommended"
        
        return ". ".join(insights[:3])
    
    def process_company(self, website_url: str, company_name: str) -> Dict[str, Any]:
        """Process a single company and generate lead qualification."""
        data = self.get_company_data(website_url, company_name)
        
        # Calculate score
        score, reasons = self.calculate_lead_score(data)
        
        # Determine priority
        priority = self.get_priority_level(score)
        
        # Generate recommendation
        recommendation = self.generate_ai_recommendation(data)
        
        # Generate insight
        insight = self.get_lead_insight(data)
        
        result = {
            'company_name': data['company_name'],
            'website_url': data['website_url'],
            'location': data['location'],
            'source': data['source'],
            'lead_score': score,
            'priority_level': priority,
            'qualification_reasons': " | ".join(reasons),
            'ai_recommendation': recommendation,
            'lead_insight': insight,
            'has_website': data['has_website'],
            'has_business_email': data['has_business_email'],
            'has_contact_email': data['has_contact_email'],
            'has_phone': data['has_phone'],
            'has_whatsapp': data['has_whatsapp'],
            'has_contact_form': data['has_contact_form'],
            'has_linkedin': data['has_linkedin'],
            'has_founder': data['has_founder'],
            'has_ceo': data['has_ceo'],
            'has_cto': data['has_cto'],
            'decision_makers_count': data['decision_makers_count'],
            'technologies': str(data['technologies']) if data['technologies'] else '',
            'linkedin_industry': data['linkedin_industry'],
            'linkedin_company_size': data['linkedin_company_size'],
            'website_score': data['website_score'],
            'has_mobile_app': data['has_mobile_app'],
            'has_ai_features': data['has_ai_features'],
            'priority_country': self.is_priority_country(data.get('location', ''))
        }
        
        return result
    
    def get_unique_companies(self) -> List[Tuple[str, str]]:
        """Get unique companies from website data."""
        companies = []
        
        if self.df_website.empty:
            logger.warning("No website data available")
            return companies
        
        # Get unique companies by website_url and company_name
        seen = set()
        for _, row in self.df_website.iterrows():
            url = row.get('website_url', '')
            name = row.get('company_name', 'Unknown')
            
            # Skip invalid entries
            if pd.isna(url) or not url or url.lower() in ['nan', '']:
                continue
            
            key = (url, name)
            if key not in seen:
                seen.add(key)
                companies.append((url, name))
        
        logger.info(f"Found {len(companies)} unique companies")
        return companies
    
    def run(self) -> pd.DataFrame:
        """Run the Lead Qualification Agent."""
        logger.info("Starting AI Lead Qualification Agent...")
        
        self.load_data()
        
        companies = self.get_unique_companies()
        
        if not companies:
            logger.error("No companies found to process")
            return pd.DataFrame()
        
        total = len(companies)
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for index, (website_url, company_name) in enumerate(companies):
            try:
                logger.info(f"[{index+1}/{total}] Processing: {company_name[:40]}...")
                
                result = self.process_company(website_url, company_name)
                self.results.append(result)
                
                if result['priority_level'] == 'High':
                    high_count += 1
                elif result['priority_level'] == 'Medium':
                    medium_count += 1
                else:
                    low_count += 1
                
                if (index + 1) % 50 == 0:
                    logger.info(f"Progress: {index+1}/{total} | High: {high_count} | Medium: {medium_count} | Low: {low_count}")
                
            except Exception as e:
                logger.error(f"Error processing {company_name}: {e}")
                continue
        
        # Convert to DataFrame
        results_df = pd.DataFrame(self.results)
        
        # Sort by score descending
        results_df = results_df.sort_values('lead_score', ascending=False)
        
        # Save to CSV
        results_df.to_csv(self.output_file, index=False, encoding='utf-8')
        
        logger.info("="*70)
        logger.info("LEAD QUALIFICATION AGENT - COMPLETED")
        logger.info("="*70)
        logger.info(f"Total Companies: {len(results_df)}")
        logger.info(f"High Priority: {high_count}")
        logger.info(f"Medium Priority: {medium_count}")
        logger.info(f"Low Priority: {low_count}")
        logger.info(f"Output: {self.output_file}")
        logger.info("="*70)
        
        return results_df


def main():
    try:
        agent = LeadQualificationAgent()
        results = agent.run()
        
        print("\n" + "="*70)
        print("AI LEAD QUALIFICATION AGENT - SUMMARY")
        print("="*70)
        print(f"Total Leads Qualified: {len(results)}")
        
        if not results.empty:
            high = len(results[results['priority_level'] == 'High'])
            medium = len(results[results['priority_level'] == 'Medium'])
            low = len(results[results['priority_level'] == 'Low'])
            
            print(f"High Priority: {high}")
            print(f"Medium Priority: {medium}")
            print(f"Low Priority: {low}")
            
            print("\n" + "="*70)
            print("TOP 10 HIGHEST SCORING LEADS")
            print("="*70)
            
            top_leads = results[results['priority_level'] == 'High'].head(10)
            if not top_leads.empty:
                cols = ['company_name', 'lead_score', 'priority_level', 'has_ceo', 'has_founder']
                print(top_leads[cols].to_string(index=False))
        
        print(f"\nOutput: {OUTPUT_FILE}")
        print("="*70)
        
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()