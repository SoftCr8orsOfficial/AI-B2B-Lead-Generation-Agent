"""
AI Sales Intelligence & Lead Generation Agent - Streamlit Dashboard
Author: Muhammad Usman
Company: SoftCr8ors
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.business_discovery import BusinessDiscoveryAgent
from src.agents.website_agent import WebsiteIntelligenceAgent
from src.agents.linkedin_agent import LinkedInIntelligenceAgent
from src.agents.decision_maker_agent import DecisionMakerFinderAgent
from src.agents.website_analysis_agent import WebsiteAnalysisAgent
from src.agents.lead_qualification_agent import LeadQualificationAgent
from src.agents.dataset_generator import DatasetGeneratorAgent
from src.config.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Sales Intelligence Agent",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 AI Sales Intelligence & Lead Generation Agent")
st.markdown("Discover businesses, collect intelligence, and generate sales-ready datasets.")

# Sidebar filters
st.sidebar.header("Search Filters")

country = st.sidebar.text_input("Country", "Pakistan")
city = st.sidebar.text_input("City", "Lahore")
state = st.sidebar.text_input("State/Province", "")
industry = st.sidebar.text_input("Industry", "Software Development")
keyword = st.sidebar.text_input("Keyword", "AI")

# Run button
run_agent = st.sidebar.button("🚀 Run AI Agent", type="primary")

# Main area
if run_agent:
    with st.spinner("Running AI Agent... This may take a few minutes."):
        # Step 1: Business Discovery
        st.info("🔍 Step 1: Discovering businesses...")
        discovery_agent = BusinessDiscoveryAgent()
        filters = {
            'country': country,
            'state': state,
            'city': city,
            'industry': industry,
            'keyword': keyword
        }
        leads = discovery_agent.run(filters)
        st.success(f"✅ Discovered {len(leads)} businesses")
        
        if not leads.empty:
            # Step 2: Website Intelligence
            st.info("🌐 Step 2: Analyzing websites...")
            website_agent = WebsiteIntelligenceAgent()
            leads_list = leads.to_dict('records')
            
            for lead in leads_list:
                website = lead.get('website')
                if website:
                    website_data = website_agent.visit_website(website)
                    lead.update(website_data)
            
            st.success(f"✅ Analyzed websites for {len(leads_list)} businesses")
            
            # Step 3: LinkedIn Intelligence
            st.info("🔗 Step 3: Finding LinkedIn companies...")
            linkedin_agent = LinkedInIntelligenceAgent()
            
            for lead in leads_list:
                if lead.get('website'):
                    linkedin_data = linkedin_agent.find_and_extract(
                        lead.get('name', ''),
                        lead.get('website')
                    )
                    lead.update(linkedin_data)
            
            st.success("✅ LinkedIn intelligence complete")
            
            # Step 4: Decision Maker Finder
            st.info("👤 Step 4: Finding decision makers...")
            decision_agent = DecisionMakerFinderAgent()
            
            for lead in leads_list:
                decision_makers = decision_agent.find_decision_makers(
                    lead.get('name', ''),
                    lead.get('website', '')
                )
                lead['decision_makers'] = decision_makers
            
            st.success("✅ Decision makers found")
            
            # Step 5: Website Analysis
            st.info("📊 Step 5: AI website analysis...")
            analysis_agent = WebsiteAnalysisAgent()
            
            for lead in leads_list:
                website = lead.get('website')
                if website:
                    analysis = analysis_agent.analyze_website(website)
                    lead['analysis_details'] = analysis['analysis_details']
                    lead['ai_opportunities'] = analysis['ai_opportunities']
                    lead['ai_recommendations'] = analysis['ai_recommendations']
            
            st.success("✅ Website analysis complete")
            
            # Step 6: Lead Qualification
            st.info("⭐ Step 6: Qualifying leads...")
            qualification_agent = LeadQualificationAgent()
            
            for lead in leads_list:
                qualified = qualification_agent.qualify_lead(lead)
                lead.update(qualified)
            
            st.success("✅ Lead qualification complete")
            
            # Step 7: Dataset Generation
            st.info("📁 Step 7: Generating datasets...")
            dataset_agent = DatasetGeneratorAgent()
            
            datasets = dataset_agent.generate_all_datasets(leads_list)
            
            # Export
            excel_path = dataset_agent.export_to_excel(datasets)
            csv_paths = dataset_agent.export_to_csv(datasets)
            
            st.success(f"✅ Datasets generated and exported")
            
            # Display results
            st.header("📊 Results")
            
            # Display sales dataset
            sales_df = datasets['sales_ready']
            st.subheader(f"Sales Ready Dataset ({len(sales_df)} leads)")
            
            # Priority distribution
            priority_counts = sales_df['Priority'].value_counts()
            col1, col2, col3 = st.columns(3)
            col1.metric("High Priority", priority_counts.get('High', 0))
            col2.metric("Medium Priority", priority_counts.get('Medium', 0))
            col3.metric("Low Priority", priority_counts.get('Low', 0))
            
            # Show table
            st.dataframe(sales_df)
            
            # Download buttons
            st.header("📥 Download Datasets")
            
            with open(excel_path, 'rb') as f:
                st.download_button(
                    label="📊 Download Excel Dataset",
                    data=f,
                    file_name=os.path.basename(excel_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            for name, path in csv_paths.items():
                with open(path, 'rb') as f:
                    st.download_button(
                        label=f"📄 Download {name.replace('_', ' ').title()} CSV",
                        data=f,
                        file_name=os.path.basename(path),
                        mime="text/csv"
                    )
        else:
            st.warning("No businesses found. Please try different filters.")

else:
    st.info("👈 Configure filters and click 'Run AI Agent' to start lead generation.")
    
    # Show example
    st.markdown("""
    ### How it works:
    1. **Enter search filters** (Country, City, Industry, Keyword)
    2. **Click 'Run AI Agent'** to start the automated lead generation
    3. **Wait** while the AI agent discovers businesses and collects intelligence
    4. **Download** the sales-ready dataset
    
    ### Features:
    - 🔍 **Business Discovery** - Google Maps, Clutch, GoodFirms, Yelp
    - 🌐 **Website Intelligence** - Emails, phones, contact forms
    - 🔗 **LinkedIn Intelligence** - Company pages, employee count
    - 👤 **Decision Maker Finder** - Founders, CEOs, CTOs
    - 📊 **AI Website Analysis** - SEO, UI/UX, recommendations
    - ⭐ **Lead Qualification** - Score, priority, recommendations
    - 📁 **Dataset Generation** - Excel/CSV export
    """)

# Footer
st.markdown("---")
st.caption("AI Sales Intelligence & Lead Generation Agent | SoftCr8ors")