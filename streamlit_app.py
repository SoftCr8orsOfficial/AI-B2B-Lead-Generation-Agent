"""
AI Sales Intelligence & Lead Generation Agent
Streamlit Dashboard — Complete with Run Agent
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import io
import subprocess
import sys
import os
import time

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

# Filters
country = st.sidebar.text_input("🌍 Country", "Pakistan")
city = st.sidebar.text_input("🏙️ City", "Lahore")
state = st.sidebar.text_input("📍 State/Province", "")
industry = st.sidebar.text_input("🏭 Industry", "Software Development")
keyword = st.sidebar.text_input("🔑 Keyword", "AI")

st.sidebar.divider()

# ============================================================
# RUN AGENT BUTTON
# ============================================================

run_agent = st.sidebar.button("🚀 Run AI Agent", type="primary", use_container_width=True)

# ============================================================
# LOAD EXISTING DATA (for display when no agent run)
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
# MAIN LOGIC
# ============================================================

if run_agent:
    # ──────────────────────────────────────────────────────────
    # STEP 1: Clear old cache
    # ──────────────────────────────────────────────────────────
    st.cache_data.clear()
    
    # ──────────────────────────────────────────────────────────
    # STEP 2: Show progress
    # ──────────────────────────────────────────────────────────
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # ──────────────────────────────────────────────────────────
    # STEP 3: Run all modules
    # ──────────────────────────────────────────────────────────
    modules = [
        ('business_discovery.py', 'Business Discovery', 1),
        ('website_agent.py', 'Website Intelligence', 2),
        ('linkedin_agent.py', 'LinkedIn Intelligence', 3),
        ('decision_maker_agent.py', 'Decision Maker Finder', 4),
        ('website_analysis_agent.py', 'Website Analysis', 5),
        ('lead_qualification_agent.py', 'Lead Qualification', 6),
        ('dataset_generation_agent.py', 'Dataset Generation', 7),
    ]
    
    results = {}
    
    for module, name, step in modules:
        status_text.info(f"⏳ Running {name}...")
        progress_bar.progress((step - 1) / len(modules))
        
        try:
            result = subprocess.run(
                [sys.executable, f'src/agents/{module}'],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode == 0:
                results[name] = "✅ Success"
            else:
                results[name] = f"❌ Failed: {result.stderr[:100]}"
        except subprocess.TimeoutExpired:
            results[name] = "⏰ Timeout"
        except Exception as e:
            results[name] = f"❌ Error: {str(e)[:50]}"
        
        progress_bar.progress(step / len(modules))
        time.sleep(1)
    
    # ──────────────────────────────────────────────────────────
    # STEP 4: Show results
    # ──────────────────────────────────────────────────────────
    status_text.success("✅ All modules complete!")
    progress_bar.progress(1.0)
    
    # ──────────────────────────────────────────────────────────
    # STEP 5: Load new data
    # ──────────────────────────────────────────────────────────
    df = load_existing_data()
    
    # ──────────────────────────────────────────────────────────
    # STEP 6: Filter data based on user inputs
    # ──────────────────────────────────────────────────────────
    filtered_df = df.copy()
    
    if not filtered_df.empty:
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
    
    # ──────────────────────────────────────────────────────────
    # STEP 7: Display results
    # ──────────────────────────────────────────────────────────
    st.session_state['df'] = filtered_df
    st.session_state['results'] = results
    st.session_state['agent_run'] = True

# ──────────────────────────────────────────────────────────────
# DISPLAY DATA
# ──────────────────────────────────────────────────────────────

# Check if data exists
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
elif 'df' not in st.session_state:
    df = load_existing_data()
    # Apply filters if data exists
    if not df.empty:
        country = st.sidebar.text_input("🌍 Country", "Pakistan")
        city = st.sidebar.text_input("🏙️ City", "Lahore")
        industry = st.sidebar.text_input("🏭 Industry", "Software Development")
        keyword = st.sidebar.text_input("🔑 Keyword", "AI")
        
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
else:
    df = load_existing_data()

# ──────────────────────────────────────────────────────────────
# METRICS
# ──────────────────────────────────────────────────────────────

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

# ──────────────────────────────────────────────────────────────
# CHARTS
# ──────────────────────────────────────────────────────────────

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

# ──────────────────────────────────────────────────────────────
# DATA TABLE
# ──────────────────────────────────────────────────────────────

st.subheader("📊 Lead Data")

if not df.empty:
    st.dataframe(df, use_container_width=True, height=400)
else:
    st.info("ℹ️ Click 'Run AI Agent' to discover leads.")

# ──────────────────────────────────────────────────────────────
# LINKEDIN & DECISION MAKERS
# ──────────────────────────────────────────────────────────────

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

# ──────────────────────────────────────────────────────────────
# DOWNLOAD
# ──────────────────────────────────────────────────────────────

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
            use_container_width=True
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
            use_container_width=True
        )

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────

st.divider()
st.caption("🤖 AI Sales Intelligence & Lead Generation Agent | SoftCr8ors Internship Project | 2026-07-10")