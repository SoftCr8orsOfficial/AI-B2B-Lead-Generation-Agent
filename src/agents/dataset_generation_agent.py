"""
Module 7: Dataset Generation Agent (Memory Optimized)
Purpose: Generate all final datasets for the AI Sales Intelligence platform
Author: AI Sales Intelligence & Lead Generation Agent
Date: 2026-07-10
"""

import pandas as pd
import logging
import sys
import json
from pathlib import Path
import codecs
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dataset_generation_agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_EXPORTS = BASE_DIR / "data" / "exports"

# Input files
WEBSITE_FILE = DATA_PROCESSED / "website_intelligence.csv"
LINKEDIN_FILE = DATA_PROCESSED / "linkedin_data.csv"
DECISION_MAKERS_FILE = DATA_PROCESSED / "decision_makers.csv"
WEBSITE_ANALYSIS_FILE = DATA_PROCESSED / "website_analysis.csv"
QUALIFIED_LEADS_FILE = DATA_PROCESSED / "qualified_leads.csv"

# Output files
OUTPUT_EXCEL = DATA_EXPORTS / "business_leads.xlsx"
OUTPUT_CLEANED = DATA_EXPORTS / "cleaned_leads.csv"
OUTPUT_ML = DATA_EXPORTS / "ml_ready_dataset.csv"
OUTPUT_SCORED = DATA_EXPORTS / "scored_leads.csv"
OUTPUT_SALES = DATA_EXPORTS / "sales_ready_dataset.xlsx"
OUTPUT_FINAL = DATA_EXPORTS / "final_database.csv"


class DatasetGenerationAgent:
    """Dataset Generation Agent - Memory Optimized."""
    
    def __init__(self):
        self.df_website = None
        self.df_linkedin = None
        self.df_decision = None
        self.df_analysis = None
        self.df_qualified = None
        
        DATA_EXPORTS.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("="*70)
        logger.info("DATASET GENERATION AGENT - MODULE 7")
        logger.info("="*70)
        logger.info(f"Output directory: {DATA_EXPORTS}")
    
    def load_data(self) -> None:
        """Load all data from previous modules."""
        logger.info("Loading data from previous modules...")
        
        try:
            self.df_website = pd.read_csv(WEBSITE_FILE, low_memory=False)
            logger.info(f"Loaded website data: {len(self.df_website)} records")
        except Exception as e:
            logger.warning(f"Could not load website data: {e}")
            self.df_website = pd.DataFrame()
        
        try:
            self.df_linkedin = pd.read_csv(LINKEDIN_FILE, low_memory=False)
            logger.info(f"Loaded LinkedIn data: {len(self.df_linkedin)} records")
        except Exception as e:
            logger.warning(f"Could not load LinkedIn data: {e}")
            self.df_linkedin = pd.DataFrame()
        
        try:
            self.df_decision = pd.read_csv(DECISION_MAKERS_FILE, low_memory=False)
            logger.info(f"Loaded decision maker data: {len(self.df_decision)} records")
        except Exception as e:
            logger.warning(f"Could not load decision maker data: {e}")
            self.df_decision = pd.DataFrame()
        
        try:
            self.df_analysis = pd.read_csv(WEBSITE_ANALYSIS_FILE, low_memory=False)
            logger.info(f"Loaded website analysis data: {len(self.df_analysis)} records")
        except Exception as e:
            logger.warning(f"Could not load website analysis data: {e}")
            self.df_analysis = pd.DataFrame()
        
        try:
            self.df_qualified = pd.read_csv(QUALIFIED_LEADS_FILE, low_memory=False)
            logger.info(f"Loaded qualified leads data: {len(self.df_qualified)} records")
        except Exception as e:
            logger.warning(f"Could not load qualified leads data: {e}")
            self.df_qualified = pd.DataFrame()
    
    def clean_value(self, val: Any) -> Any:
        """Clean and standardize a value."""
        if val is None:
            return ''
        if isinstance(val, float):
            if pd.isna(val):
                return ''
        if isinstance(val, str):
            if val.lower() in ['nan', 'none', 'null', '']:
                return ''
            return val.strip()
        if isinstance(val, list):
            return ', '.join(str(v) for v in val if v)
        if isinstance(val, dict):
            return json.dumps(val)
        return val
    
    def merge_all_data(self) -> pd.DataFrame:
        """Merge all data sources into a single DataFrame - Memory Optimized."""
        logger.info("Merging all data sources...")
        
        if self.df_website.empty:
            logger.error("No website data available")
            return pd.DataFrame()
        
        # Start with website data
        base_df = self.df_website.copy()
        
        # Drop duplicate website_url to avoid memory explosion
        base_df = base_df.drop_duplicates(subset=['website_url', 'company_name'])
        
        # Convert website_url to string for consistent merging
        base_df['website_url'] = base_df['website_url'].astype(str)
        
        logger.info(f"Base records: {len(base_df)}")
        
        # Merge LinkedIn data (deduplicate first)
        if not self.df_linkedin.empty:
            linkedin_df = self.df_linkedin.copy()
            linkedin_df = linkedin_df.drop_duplicates(subset=['website_url'])
            linkedin_df['website_url'] = linkedin_df['website_url'].astype(str)
            
            linkedin_cols = ['website_url', 'linkedin_url', 'linkedin_description', 
                            'linkedin_headquarters', 'linkedin_industry', 
                            'linkedin_company_size', 'linkedin_employee_count']
            existing_cols = [col for col in linkedin_cols if col in linkedin_df.columns]
            linkedin_subset = linkedin_df[existing_cols]
            
            base_df = base_df.merge(linkedin_subset, on='website_url', how='left')
            logger.info(f"After LinkedIn merge: {len(base_df)}")
        
        # Merge Decision Maker data (deduplicate first)
        if not self.df_decision.empty:
            decision_df = self.df_decision.copy()
            decision_df = decision_df.drop_duplicates(subset=['website_url'])
            decision_df['website_url'] = decision_df['website_url'].astype(str)
            
            decision_cols = ['website_url', 'founder', 'founder_linkedin', 'ceo', 'ceo_linkedin',
                            'cto', 'cto_linkedin', 'coo', 'coo_linkedin', 'owner', 'owner_linkedin',
                            'managing_director', 'managing_director_linkedin', 'decision_makers_found']
            existing_cols = [col for col in decision_cols if col in decision_df.columns]
            decision_subset = decision_df[existing_cols]
            
            base_df = base_df.merge(decision_subset, on='website_url', how='left')
            logger.info(f"After Decision Maker merge: {len(base_df)}")
        
        # Merge Analysis data (deduplicate first)
        if not self.df_analysis.empty:
            analysis_df = self.df_analysis.copy()
            analysis_df = analysis_df.drop_duplicates(subset=['website_url'])
            analysis_df['website_url'] = analysis_df['website_url'].astype(str)
            
            analysis_cols = ['website_url', 'score', 'has_mobile_app', 'has_ai_features',
                            'has_automation', 'has_live_chat', 'has_call_to_action',
                            'is_outdated', 'poor_ui_ux', 'missing_seo', 'weak_branding',
                            'ai_recommendations', 'status']
            existing_cols = [col for col in analysis_cols if col in analysis_df.columns]
            analysis_subset = analysis_df[existing_cols]
            
            base_df = base_df.merge(analysis_subset, on='website_url', how='left')
            logger.info(f"After Analysis merge: {len(base_df)}")
        
        # Merge Qualified Leads data (deduplicate first)
        if not self.df_qualified.empty:
            qualified_df = self.df_qualified.copy()
            qualified_df = qualified_df.drop_duplicates(subset=['website_url'])
            qualified_df['website_url'] = qualified_df['website_url'].astype(str)
            
            qualified_cols = ['website_url', 'lead_score', 'priority_level', 
                            'qualification_reasons', 'ai_recommendation', 'lead_insight',
                            'has_website', 'has_business_email', 'has_contact_email',
                            'has_phone', 'has_whatsapp', 'has_contact_form',
                            'has_linkedin', 'has_founder', 'has_ceo', 'has_cto',
                            'decision_makers_count', 'priority_country']
            existing_cols = [col for col in qualified_cols if col in qualified_df.columns]
            qualified_subset = qualified_df[existing_cols]
            
            base_df = base_df.merge(qualified_subset, on='website_url', how='left')
            logger.info(f"After Qualified Leads merge: {len(base_df)}")
        
        logger.info(f"Final merged dataset: {len(base_df)} records")
        return base_df
    
    def generate_business_leads(self, df: pd.DataFrame) -> None:
        """Generate business_leads.xlsx"""
        logger.info("Generating business_leads.xlsx...")
        
        key_cols = [
            'company_name', 'website_url', 'location', 'source',
            'business_emails', 'contact_emails', 'phones', 'whatsapp',
            'contact_form', 'description', 'technologies',
            'linkedin_url', 'linkedin_industry', 'linkedin_company_size',
            'founder', 'ceo', 'cto', 'coo', 'managing_director',
            'lead_score', 'priority_level', 'ai_recommendation'
        ]
        
        existing_cols = [col for col in key_cols if col in df.columns]
        export_df = df[existing_cols].copy()
        
        for col in export_df.columns:
            export_df[col] = export_df[col].apply(self.clean_value)
        
        export_df.to_excel(OUTPUT_EXCEL, index=False)
        logger.info(f"Saved: {OUTPUT_EXCEL} ({len(export_df)} records)")
    
    def generate_cleaned_leads(self, df: pd.DataFrame) -> None:
        """Generate cleaned_leads.csv"""
        logger.info("Generating cleaned_leads.csv...")
        
        cleaned_df = df.copy()
        cleaned_df = cleaned_df.dropna(subset=['company_name'], how='all')
        cleaned_df = cleaned_df.drop_duplicates(subset=['company_name', 'website_url'])
        
        for col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].apply(self.clean_value)
        
        cleaned_df.to_csv(OUTPUT_CLEANED, index=False, encoding='utf-8')
        logger.info(f"Saved: {OUTPUT_CLEANED} ({len(cleaned_df)} records)")
    
    def generate_ml_ready_dataset(self, df: pd.DataFrame) -> None:
        """Generate ml_ready_dataset.csv"""
        logger.info("Generating ml_ready_dataset.csv...")
        
        ml_cols = [
            'company_name', 'website_url', 'location',
            'has_website', 'has_business_email', 'has_contact_email',
            'has_phone', 'has_whatsapp', 'has_contact_form',
            'has_linkedin', 'has_founder', 'has_ceo', 'has_cto',
            'decision_makers_count', 'technologies',
            'has_mobile_app', 'has_ai_features', 'has_automation',
            'has_live_chat', 'has_call_to_action',
            'is_outdated', 'poor_ui_ux', 'missing_seo', 'weak_branding',
            'lead_score', 'priority_level', 'priority_country'
        ]
        
        existing_cols = [col for col in ml_cols if col in df.columns]
        ml_df = df[existing_cols].copy()
        
        bool_cols = ml_df.select_dtypes(include=['bool']).columns
        for col in bool_cols:
            ml_df[col] = ml_df[col].astype(int)
        
        for col in ml_df.columns:
            ml_df[col] = ml_df[col].apply(self.clean_value)
        
        ml_df.to_csv(OUTPUT_ML, index=False, encoding='utf-8')
        logger.info(f"Saved: {OUTPUT_ML} ({len(ml_df)} records)")
    
    def generate_scored_leads(self, df: pd.DataFrame) -> None:
        """Generate scored_leads.csv"""
        logger.info("Generating scored_leads.csv...")
        
        if 'lead_score' in df.columns:
            scored_df = df.sort_values('lead_score', ascending=False)
        else:
            scored_df = df
        
        score_cols = [
            'company_name', 'website_url', 'location', 'lead_score',
            'priority_level', 'qualification_reasons', 'lead_insight',
            'ai_recommendation', 'has_business_email', 'has_phone',
            'has_linkedin', 'has_founder', 'has_ceo', 'decision_makers_count'
        ]
        
        existing_cols = [col for col in score_cols if col in scored_df.columns]
        export_df = scored_df[existing_cols].copy()
        
        for col in export_df.columns:
            export_df[col] = export_df[col].apply(self.clean_value)
        
        export_df.to_csv(OUTPUT_SCORED, index=False, encoding='utf-8')
        logger.info(f"Saved: {OUTPUT_SCORED} ({len(export_df)} records)")
    
    def generate_sales_ready_dataset(self, df: pd.DataFrame) -> None:
        """Generate sales_ready_dataset.xlsx"""
        logger.info("Generating sales_ready_dataset.xlsx...")
        
        sales_cols = [
            'company_name', 'website_url', 'location',
            'business_emails', 'contact_emails', 'phones', 'whatsapp',
            'contact_form', 'description',
            'linkedin_url', 'linkedin_industry', 'linkedin_company_size',
            'founder', 'founder_linkedin', 'ceo', 'ceo_linkedin',
            'cto', 'cto_linkedin', 'managing_director', 'managing_director_linkedin',
            'lead_score', 'priority_level', 'ai_recommendation', 'lead_insight'
        ]
        
        existing_cols = [col for col in sales_cols if col in df.columns]
        sales_df = df[existing_cols].copy()
        
        if 'priority_level' in sales_df.columns:
            sales_df = sales_df[sales_df['priority_level'] == 'High']
        
        for col in sales_df.columns:
            sales_df[col] = sales_df[col].apply(self.clean_value)
        
        sales_df.to_excel(OUTPUT_SALES, index=False)
        logger.info(f"Saved: {OUTPUT_SALES} ({len(sales_df)} High Priority records)")
    
    def generate_final_database(self, df: pd.DataFrame) -> None:
        """Generate final_database.csv"""
        logger.info("Generating final_database.csv...")
        
        final_df = df.copy()
        
        for col in final_df.columns:
            final_df[col] = final_df[col].apply(self.clean_value)
        
        final_df.to_csv(OUTPUT_FINAL, index=False, encoding='utf-8')
        logger.info(f"Saved: {OUTPUT_FINAL} ({len(final_df)} records)")
    
    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """Generate summary report."""
        total = len(df)
        
        high_priority = len(df[df['priority_level'] == 'High']) if 'priority_level' in df.columns else 0
        medium_priority = len(df[df['priority_level'] == 'Medium']) if 'priority_level' in df.columns else 0
        low_priority = len(df[df['priority_level'] == 'Low']) if 'priority_level' in df.columns else 0
        
        has_email = len(df[df['has_business_email'] == True]) if 'has_business_email' in df.columns else 0
        has_phone = len(df[df['has_phone'] == True]) if 'has_phone' in df.columns else 0
        has_linkedin = len(df[df['has_linkedin'] == True]) if 'has_linkedin' in df.columns else 0
        has_founder = len(df[df['has_founder'] == True]) if 'has_founder' in df.columns else 0
        
        return f"""
{"="*70}
DATASET GENERATION AGENT - SUMMARY REPORT
{"="*70}

Total Companies: {total}

PRIORITY DISTRIBUTION:
- High Priority: {high_priority}
- Medium Priority: {medium_priority}  
- Low Priority: {low_priority}

DATA QUALITY:
- Companies with Email: {has_email} ({(has_email/total*100):.1f}%)
- Companies with Phone: {has_phone} ({(has_phone/total*100):.1f}%)
- Companies with LinkedIn: {has_linkedin} ({(has_linkedin/total*100):.1f}%)
- Companies with Founder: {has_founder} ({(has_founder/total*100):.1f}%)

OUTPUT FILES:
1. {OUTPUT_EXCEL} - Business Leads (Excel)
2. {OUTPUT_CLEANED} - Cleaned Leads (CSV)
3. {OUTPUT_ML} - ML Ready Dataset (CSV)
4. {OUTPUT_SCORED} - Scored Leads (CSV)
5. {OUTPUT_SALES} - Sales Ready Dataset (Excel)
6. {OUTPUT_FINAL} - Final Database (CSV)

{"="*70}
"""
    
    def run(self) -> Dict[str, pd.DataFrame]:
        """Run the Dataset Generation Agent."""
        logger.info("Starting Dataset Generation Agent...")
        
        self.load_data()
        
        merged_df = self.merge_all_data()
        
        if merged_df.empty:
            logger.error("No data to export")
            return {}
        
        self.generate_business_leads(merged_df)
        self.generate_cleaned_leads(merged_df)
        self.generate_ml_ready_dataset(merged_df)
        self.generate_scored_leads(merged_df)
        self.generate_sales_ready_dataset(merged_df)
        self.generate_final_database(merged_df)
        
        report = self.generate_summary_report(merged_df)
        logger.info(report)
        print(report)
        
        return {
            'merged': merged_df,
            'business_leads': pd.read_excel(OUTPUT_EXCEL) if OUTPUT_EXCEL.exists() else pd.DataFrame(),
            'cleaned_leads': pd.read_csv(OUTPUT_CLEANED) if OUTPUT_CLEANED.exists() else pd.DataFrame(),
            'ml_ready': pd.read_csv(OUTPUT_ML) if OUTPUT_ML.exists() else pd.DataFrame(),
            'scored_leads': pd.read_csv(OUTPUT_SCORED) if OUTPUT_SCORED.exists() else pd.DataFrame(),
            'sales_ready': pd.read_excel(OUTPUT_SALES) if OUTPUT_SALES.exists() else pd.DataFrame(),
            'final_database': pd.read_csv(OUTPUT_FINAL) if OUTPUT_FINAL.exists() else pd.DataFrame()
        }


def main():
    try:
        agent = DatasetGenerationAgent()
        results = agent.run()
        
        print("\n" + "="*70)
        print("DATASET GENERATION AGENT - COMPLETED")
        print("="*70)
        print(f"All datasets saved to: {DATA_EXPORTS}")
        print("\nFiles Generated:")
        print(f"  1. business_leads.xlsx")
        print(f"  2. cleaned_leads.csv")
        print(f"  3. ml_ready_dataset.csv")
        print(f"  4. scored_leads.csv")
        print(f"  5. sales_ready_dataset.xlsx")
        print(f"  6. final_database.csv")
        print("="*70)
        
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()