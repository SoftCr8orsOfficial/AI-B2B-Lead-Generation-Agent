# System Architecture

## Overview

The AI Sales Intelligence Agent follows a modular pipeline architecture with 7 independent modules.

## Architecture Diagram
  
  ┌─────────────────────────────────────────────────────────────────────────────┐
│ USER INPUT / FILTERS │
│ (Country, City, Industry, Keyword) │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MODULE 1: BUSINESS DISCOVERY │
│ Google Maps | Yelp | Clutch | GoodFirms | Crunchbase │
│ Output: all_countries_leads.csv │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MODULE 2: WEBSITE INTELLIGENCE │
│ Emails | Phones | WhatsApp | Social Links | SSL | Technologies │
│ Output: website_intelligence.csv │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MODULE 3: LINKEDIN INTELLIGENCE │
│ LinkedIn URL | Description | Industry | Size | Employees │
│ Output: linkedin_data.csv │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MODULE 4: DECISION MAKER FINDER │
│ Founder | CEO | CTO | COO | Director | Head of Engineering │
│ Output: decision_makers.csv │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MODULE 5: AI WEBSITE ANALYSIS │
│ UI/UX | SEO | Branding | Mobile App | AI Features | Automation │
│ Output: website_analysis.csv │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MODULE 6: AI LEAD QUALIFICATION │
│ Lead Score (0-100) | Priority (High/Medium/Low) │
│ Output: qualified_leads.csv │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MODULE 7: DATASET GENERATION │
│ Excel | CSV | ML-Ready | Sales-Ready | Final Database │
│ Output: 6 files in data/exports/ │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STREAMLIT DASHBOARD │
│ Filters | Charts | Data Table | Download (CSV + Excel) │
└─────────────────────────────────────────────────────────────────────────────┘