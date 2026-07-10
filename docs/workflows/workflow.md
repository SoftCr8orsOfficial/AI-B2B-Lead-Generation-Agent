# Workflow Diagram

## Complete Lead Generation Workflow
  
  ┌─────────────────────────────────────┐
│ USER INPUTS FILTERS │
│ Country, City, Industry, Keyword │
└─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────┐
│ BUSINESS DISCOVERY │
│ Scrape Google Maps, Yelp, Clutch │
│ Output: Leads CSV │
└─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────┐
│ WEBSITE INTELLIGENCE │
│ Visit each website, extract data │
│ Emails, Phones, WhatsApp, Social │
└─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────┐
│ LINKEDIN INTELLIGENCE │
│ Find LinkedIn company pages │
│ Extract Description, Industry │
└─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────┐
│ DECISION MAKER FINDER │
│ Find Founder, CEO, CTO, COO │
│ Extract Name + LinkedIn URL │
└─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────┐
│ AI WEBSITE ANALYSIS │
│ Detect UI/UX, SEO, Branding │
│ Generate AI Recommendations │
└─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────┐
│ LEAD QUALIFICATION │
│ Score leads (0-100) │
│ Assign Priority (High/Medium/Low)│
└─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────┐
│ DATASET GENERATION │
│ 6 Files: Excel, CSV, ML-Ready │
│ Final Database + Sales Dataset │
└─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────┐
│ STREAMLIT DASHBOARD │
│ Filters | Charts | Data Table │
│ Download CSV + Excel │
└─────────────────────────────────────┘  
  
  
## Lead Scoring Flowchart
  
  ┌──────────────────────────────────────────────┐
│ LEAD SCORING │
│ (0-100 points) │
└──────────────────────────────────────────────┘
│
┌────────────────────────────┼────────────────────────────┐
│ │ │
▼ ▼ ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ High Priority │ │ Medium Priority│ │ Low Priority │
│ 70-100 │ │ 40-69 │ │ 0-39 │
│ 🔴 170 Leads │ │ 🟡 3 Leads │ │ 🟢 0 Leads │
└───────────────┘ └───────────────┘ └───────────────┘  
  
  
## Scoring Rules

| Criteria | Points |
|----------|--------|
| Website Available | +10 |
| Business Email | +10 |
| Phone Number | +10 |
| LinkedIn Company | +10 |
| Founder Found | +15 |
| CEO Found | +15 |
| Priority Country | +20 |
| Company Size >20 | +10 |
| SSL | +5 |
| Blog | +5 |
| Social Links | +5 |
| Mobile App | +5 |
| AI Features | +5 |  
