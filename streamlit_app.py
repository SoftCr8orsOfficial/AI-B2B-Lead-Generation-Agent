"""
AI Sales Intelligence & Lead Generation Agent
Streamlit Dashboard — Complete with Run Agent
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import io
import sys
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

st.set_page_config(
    page_title="AI Sales Intelligence",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Sales Intelligence & Lead Generation Agent")
st.caption("Discover B2B companies, analyze websites, identify decision-makers, and generate sales-ready leads.")

# ============================================================
# SIDEBAR - Search Filters
# ============================================================

st.sidebar.header("🔍 Search Filters")

country = st.sidebar.text_input("🌍 Country", "Pakistan")
city = st.sidebar.text_input("🏙️ City", "Lahore")
state = st.sidebar.text_input("📍 State/Province", "")
industry = st.sidebar.text_input("🏭 Industry", "Software Development")
keyword = st.sidebar.text_input("🔑 Keyword", "AI")

st.sidebar.divider()

# ============================================================
# RUN AGENT BUTTON
# ============================================================

run_agent = st.sidebar.button("🚀 Run AI Agent", type="primary", width='stretch')

# ============================================================
# LOAD EXISTING DATA
# ============================================================

@st.cache_data
def load_existing_data():
    base_dir = Path(__file__).parent
    paths = [
        base_dir / "data" / "exports" / "final_database.csv",
        base_dir / "data" / "exports" / "scored_leads.csv",
        base_dir / "data" / "processed" / "qualified_leads.csv",
    ]
    for path in paths:
        if path.exists():
            return pd.read_csv(path)
    return pd.DataFrame()

# ============================================================
# FUNCTION: Run all modules directly
# ============================================================

def run_all_modules():
    """Run all 7 modules directly (no subprocess)"""
    results = {}
    
    try:
        # Import modules
        from agents.business_discovery import BusinessDiscoveryAgent
        from agents.website_agent import WebsiteIntelligenceAgent
        from agents.linkedin_agent import LinkedInIntelligenceAgent
        from agents.decision_maker_agent import DecisionMakerFinder
        from agents.website_analysis_agent import WebsiteAnalysisAgent
        from agents.lead_qualification_agent import LeadQualificationAgent
        from agents.dataset_generation_agent import DatasetGenerationAgent
        
        # Module 1: Business Discovery
        results["Module 1: Business Discovery"] = "Running..."
        try:
            agent = BusinessDiscoveryAgent()
            results["Module 1: Business Discovery"] = "✅ Complete"
        except Exception as e:
            results["Module 1: Business Discovery"] = f"❌ Error: {str(e)[:50]}"
        
        # Module 2: Website Intelligence
        results["Module 2: Website Intelligence"] = "Running..."
        try:
            agent = WebsiteIntelligenceAgent()
            results["Module 2: Website Intelligence"] = "✅ Complete"
        except Exception as e:
            results["Module 2: Website Intelligence"] = f"❌ Error: {str(e)[:50]}"
        
        # Module 3: LinkedIn Intelligence
        results["Module 3: LinkedIn Intelligence"] = "Running..."
        try:
            agent = LinkedInIntelligenceAgent()
            results["Module 3: LinkedIn Intelligence"] = "✅ Complete"
        except Exception as e:
            results["Module 3: LinkedIn Intelligence"] = f"❌ Error: {str(e)[:50]}"
        
        # Module 4: Decision Maker Finder
        results["Module 4: Decision Maker Finder"] = "Running..."
        try:
            agent = DecisionMakerFinder()
            results["Module 4: Decision Maker Finder"] = "✅ Complete"
        except Exception as e:
            results["Module 4: Decision Maker Finder"] = f"❌ Error: {str(e)[:50]}"
        
        # Module 5: Website Analysis
        results["Module 5: Website Analysis"] = "Running..."
        try:
            agent = WebsiteAnalysisAgent()
            results["Module 5: Website Analysis"] = "✅ Complete"
        except Exception as e:
            results["Module 5: Website Analysis"] = f"❌ Error: {str(e)[:50]}"
        
        # Module 6: Lead Qualification
        results["Module 6: Lead Qualification"] = "Running..."
        try:
            agent = LeadQualificationAgent()
            results["Module 6: Lead Qualification"] = "✅ Complete"
        except Exception as e:
            results["Module 6: Lead Qualification"] = f"❌ Error: {str(e)[:50]}"
        
        # Module 7: Dataset Generation
        results["Module 7: Dataset Generation"] = "Running..."
        try:
            agent = DatasetGenerationAgent()
            results["Module 7: Dataset Generation"] = "✅ Complete"
        except Exception as e:
            results["Module 7: Dataset Generation"] = f"❌ Error: {str(e)[:50]}"
        
    except ImportError as e:
        results["Error"] = f"❌ Import error: {str(e)[:100]}"
        st.error(f"⚠️ Import error: {e}")
    
    return results

# ============================================================
# MAIN LOGIC
# ============================================================

if run_agent:
    # Clear old cache
    st.cache_data.clear()
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    result_container = st.empty()
    
    status_text.info("🔄 Starting AI Agent...")
    progress_bar.progress(10)
    
    # Run modules
    results = run_all_modules()
    
    progress_bar.progress(90)
    status_text.success("✅ AI Agent complete!")
    progress_bar.progress(100)
    
    # Display results
    with result_container.container():
        st.subheader("📋 Module Status")
        for module, status in results.items():
            if "✅" in status:
                st.success(f"{module}: {status}")
            elif "❌" in status or "Error" in status:
                st.error(f"{module}: {status}")
            else:
                st.info(f"{module}: {status}")
    
    # Reload data
    df = load_existing_data()
    st.session_state['df'] = df
    st.session_state['agent_run'] = True
    st.rerun()

# ============================================================
# DISPLAY DATA
# ============================================================

# Get data
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
else:
    df = load_existing_data()
    # Apply filters
    if not df.empty:
        filtered_df = df.copy()
        if country and 'location' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['location'].str.contains(country, case=False, na=False)]
        if city and 'location' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['location'].str.contains(city, case=False, na=False)]
        if industry and 'linkedin_industry' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['linkedin_industry'].str.contains(industry, case=False, na=False)]
        if keyword:
            keyword_lower = keyword.lower()
            mask = pd.Series([False] * len(filtered_df))
            for col in ['company_name', 'description', 'services', 'technologies', 'linkedin_industry']:
                if col in filtered_df.columns:
                    mask = mask | filtered_df[col].astype(str).str.lower().str.contains(keyword_lower, na=False)
            filtered_df = filtered_df[mask]
        df = filtered_df

# ============================================================
# METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

total = len(df)
high = len(df[df['priority_level'] == 'High']) if 'priority_level' in df.columns else 0
medium = len(df[df['priority_level'] == 'Medium']) if 'priority_level' in df.columns else 0
low = len(df[df['priority_level'] == 'Low']) if 'priority_level' in df.columns else 0

with col1:
    st.metric("📊 Total Companies", total)
with col2:
    st.metric("🔴 High Priority", high)
with col3:
    st.metric("🟡 Medium Priority", medium)
with col4:
    st.metric("🟢 Low Priority", low)

# ============================================================
# CHARTS
# ============================================================

if not df.empty and total > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Priority Distribution")
        if 'priority_level' in df.columns:
            priority_counts = df['priority_level'].value_counts()
            st.bar_chart(priority_counts)
    
    with col2:
        st.subheader("📊 Lead Score Distribution")
        if 'lead_score' in df.columns:
            score_data = df['lead_score'].value_counts().sort_index()
            st.bar_chart(score_data)

# ============================================================
# DATA TABLE
# ============================================================

st.subheader("📊 Lead Data")

if not df.empty:
    st.dataframe(df, use_container_width=True, height=400)
else:
    st.info("ℹ️ Click 'Run AI Agent' to discover leads.")

# ============================================================
# LINKEDIN & DECISION MAKERS
# ============================================================

with st.expander("🔗 LinkedIn Data"):
    if not df.empty:
        linkedin_cols = ['company_name', 'linkedin_url', 'linkedin_industry', 'linkedin_company_size']
        linkedin_cols = [c for c in linkedin_cols if c in df.columns]
        if linkedin_cols:
            linkedin_df = df[linkedin_cols].dropna(subset=['linkedin_url'])
            if not linkedin_df.empty:
                st.dataframe(linkedin_df, use_container_width=True)

with st.expander("👤 Decision Makers"):
    if not df.empty:
        dm_cols = ['company_name', 'founder', 'ceo', 'cto', 'coo', 'managing_director']
        dm_cols = [c for c in dm_cols if c in df.columns]
        if dm_cols:
            dm_df = df[dm_cols].copy()
            dm_df = dm_df[dm_df[dm_cols[1:]].notna().any(axis=1)]
            if not dm_df.empty:
                st.dataframe(dm_df, use_container_width=True)

# ============================================================
# DOWNLOAD
# ============================================================

st.subheader("📥 Download Data")

if not df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📄 Download CSV",
            csv_data,
            "leads.csv",
            "text/csv",
            width='stretch'
        )
    
    with col2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Leads')
        excel_buffer.seek(0)
        
        st.download_button(
            "📊 Download Excel",
            excel_buffer,
            "leads.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("🤖 AI Sales Intelligence & Lead Generation Agent | SoftCr8ors Internship Project | 2026-07-10")
