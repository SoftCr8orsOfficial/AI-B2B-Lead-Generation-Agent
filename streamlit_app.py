"""
AI Sales Intelligence & Lead Generation Agent
Streamlit Dashboard - No Warnings
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import io

st.set_page_config(
    page_title="AI Sales Intelligence",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Sales Intelligence & Lead Generation Agent")
st.caption("Discover B2B companies, analyze websites, identify decision-makers, and generate sales-ready leads.")

@st.cache_data
def load_data():
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

df = load_data()

# ============================================================
# SIDEBAR - Filters
# ============================================================

st.sidebar.header("🔍 Search Filters")

countries = []
cities = []
industries = []

if not df.empty:
    if 'location' in df.columns:
        countries = df['location'].str.split(',').str[-1].str.strip().unique()
        countries = sorted([c for c in countries if c and c != ''])
        cities = df['location'].str.split(',').str[0].str.strip().unique()
        cities = sorted([c for c in cities if c and c != ''])
    
    if 'linkedin_industry' in df.columns:
        industries = df['linkedin_industry'].dropna().unique()
        industries = sorted([i for i in industries if i and str(i) != 'nan'])

country = st.sidebar.selectbox("🌍 Country", ["All"] + list(countries))
city = st.sidebar.selectbox("🏙️ City", ["All"] + list(cities))
industry = st.sidebar.selectbox("🏭 Industry", ["All"] + list(industries))
keyword = st.sidebar.text_input("🔑 Keywords", placeholder="e.g., AI, Mobile App, ERP")

st.sidebar.divider()
if st.sidebar.button("🔄 Refresh Data", width='stretch'):
    st.cache_data.clear()
    st.rerun()
st.sidebar.caption("Data is pre-generated from 7 modules. Click Refresh to reload.")

# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if not df.empty:
    if country != "All" and 'location' in df.columns:
        filtered_df = filtered_df[filtered_df['location'].str.split(',').str[-1].str.strip() == country]
    
    if city != "All" and 'location' in df.columns:
        filtered_df = filtered_df[filtered_df['location'].str.split(',').str[0].str.strip() == city]
    
    if industry != "All" and 'linkedin_industry' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['linkedin_industry'] == industry]
    
    if keyword:
        keyword_lower = keyword.lower()
        mask = pd.Series([False] * len(filtered_df))
        for col in ['company_name', 'description', 'services', 'technologies', 'linkedin_industry']:
            if col in filtered_df.columns:
                mask = mask | filtered_df[col].astype(str).str.lower().str.contains(keyword_lower, na=False)
        filtered_df = filtered_df[mask]

# ============================================================
# METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

total = len(filtered_df)
high = len(filtered_df[filtered_df['priority_level'] == 'High']) if 'priority_level' in filtered_df.columns else 0
medium = len(filtered_df[filtered_df['priority_level'] == 'Medium']) if 'priority_level' in filtered_df.columns else 0
low = len(filtered_df[filtered_df['priority_level'] == 'Low']) if 'priority_level' in filtered_df.columns else 0

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

if not filtered_df.empty and total > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Priority Distribution")
        if 'priority_level' in filtered_df.columns:
            priority_counts = filtered_df['priority_level'].value_counts()
            st.bar_chart(priority_counts)
    
    with col2:
        st.subheader("📊 Lead Score Distribution")
        if 'lead_score' in filtered_df.columns:
            score_data = filtered_df['lead_score'].value_counts().sort_index()
            st.bar_chart(score_data)

# ============================================================
# DATA TABLE
# ============================================================

st.subheader("📊 Lead Data")

if not filtered_df.empty:
    st.dataframe(filtered_df, width='stretch', height=400)
else:
    st.info("ℹ️ No data found. Please run modules locally first.")

# ============================================================
# LINKEDIN TABLE
# ============================================================

with st.expander("🔗 LinkedIn Data"):
    if not filtered_df.empty:
        linkedin_cols = ['company_name', 'linkedin_url', 'linkedin_industry', 'linkedin_company_size']
        linkedin_cols = [c for c in linkedin_cols if c in filtered_df.columns]
        if linkedin_cols:
            linkedin_df = filtered_df[linkedin_cols].dropna(subset=['linkedin_url'])
            if not linkedin_df.empty:
                st.dataframe(linkedin_df, width='stretch')
            else:
                st.info("No LinkedIn data available")

# ============================================================
# DECISION MAKERS TABLE
# ============================================================

with st.expander("👤 Decision Makers"):
    if not filtered_df.empty:
        dm_cols = ['company_name', 'founder', 'ceo', 'cto', 'coo', 'managing_director']
        dm_cols = [c for c in dm_cols if c in filtered_df.columns]
        if dm_cols:
            dm_df = filtered_df[dm_cols].copy()
            dm_df = dm_df[dm_df[dm_cols[1:]].notna().any(axis=1)]
            if not dm_df.empty:
                st.dataframe(dm_df, width='stretch')
            else:
                st.info("No decision makers found")

# ============================================================
# DOWNLOAD
# ============================================================

st.subheader("📥 Download Data")

if not filtered_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = filtered_df.to_csv(index=False)
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
            filtered_df.to_excel(writer, index=False, sheet_name='Leads')
        excel_buffer.seek(0)
        
        st.download_button(
            "📊 Download Excel",
            excel_buffer,
            "leads.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )
else:
    st.info("ℹ️ No data to download. Run modules first.")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("🤖 AI Sales Intelligence & Lead Generation Agent | SoftCr8ors Internship Project | 2026-07-10")
