# 🤖 AI Sales Intelligence & Lead Generation Agent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-b2b-lead-generation-agent-4sdmxh5sangfbr64wtrxhu.streamlit.app)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Overview

A **production-ready AI-powered lead generation platform** that automatically discovers B2B companies, collects business intelligence, identifies decision-makers, analyzes websites, qualifies leads, and generates sales-ready datasets with minimal manual effort.

Built as a **3-day Machine Learning internship project** for **SoftCr8ors**.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🌍 **Global Discovery** | Discover businesses from any country |
| 🏢 **Website Intelligence** | Extract emails, phones, WhatsApp, social links |
| 🔗 **LinkedIn Intelligence** | Find LinkedIn company pages and extract data |
| 👤 **Decision Maker Finder** | Identify Founders, CEOs, CTOs, and more |
| 🤖 **AI Website Analysis** | Detect UI/UX issues, missing SEO, weak branding |
| 🎯 **Lead Qualification** | Score leads (0-100) with priority levels |
| 📁 **Dataset Generation** | Export clean, sales-ready datasets |

---

## 📊 Results Summary

| Metric | Value |
|--------|-------|
| **Total Companies Discovered** | 362 |
| **High Priority Leads** | 170 |
| **Medium Priority Leads** | 3 |
| **Companies with Email** | 173 (47.8%) |
| **Companies with Phone** | 173 (47.8%) |
| **Companies with LinkedIn** | 112 (30.9%) |
| **Founders Identified** | 13 |

---

## 🏗️ Architecture  

  ┌─────────────────────────────────────────────────────────────────┐  
│ AI Sales Intelligence Agent │  
├─────────────────────────────────────────────────────────────────┤  
│ │  
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │  
│ │ Module 1 │ │ Module 2 │ │ Module 3 │ │  
│ │ Business │───▶│ Website │───▶│ LinkedIn │ │   
│ │ Discovery │ │ Intelligence │ │ Intelligence│ │  
│ └──────────────┘ └──────────────┘ └──────────────┘ │  
│ │ │ │ │  
│ ▼ ▼ ▼ │  
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │    
│ │ Module 4 │ │ Module 5 │ │ Module 6 │ │  
│ │ Decision │───▶│ Website │───▶│ Lead │ │  
│ │ Maker Finder│ │ Analysis │ │ Qualification│ │  
│ └──────────────┘ └──────────────┘ └──────────────┘ │  
│ │ │  
│ ▼ │  
│ ┌──────────────┐ │  
│ │ Module 7 │ │  
│ │ Dataset │ │  
│ │ Generation │ │  
│ └──────────────┘ │  
│ │ │  
│ ▼ │  
│ ┌──────────────┐ │  
│ │ Sales-Ready│ │  
│ │ Datasets │ │  
│ └──────────────┘ │  
└─────────────────────────────────────────────────────────────────┘  

  

---

## 📁 Project Structure

  AI-B2B-Lead-Generation-Agent/   
├── data/    
│ ├── raw/  
│ │ └── all_countries_leads.csv # Module 1  
│ ├── processed/  
│ │ ├── website_intelligence.csv # Module 2  
│ │ ├── linkedin_data.csv # Module 3  
│ │ ├── decision_makers.csv # Module 4  
│ │ ├── website_analysis.csv # Module 5  
│ │ └── qualified_leads.csv # Module 6  
│ └── exports/  
│ ├── business_leads.xlsx # Module 7  
│ ├── cleaned_leads.csv    
│ ├── ml_ready_dataset.csv  
│ ├── scored_leads.csv  
│ ├── sales_ready_dataset.xlsx  
│ └── final_database.csv  
├── src/  
│ └── agents/  
│ ├── business_discovery.py # Module 1  
│ ├── website_agent.py # Module 2  
│ ├── linkedin_agent.py # Module 3  
│ ├── decision_maker_agent.py # Module 4  
│ ├── website_analysis_agent.py # Module 5  
│ ├── lead_qualification_agent.py # Module 6  
│ └── dataset_generation_agent.py # Module 7  
├── deployment/  
│ ├── streamlit/  
│ │ └── app.py  
│ └── requirements.txt  
├── logs/  
├── notebooks/  
├── video/  
├── docs/  
│ ├── project_report.md  
│ └── architecture.md  
├── streamlit_app.py # Main App  
├── requirements.txt  
├── .gitignore  
├── README.md  
└── LICENSE  

---

## 🛠️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/SoftCr8orsOfficial/AI-B2B-Lead-Generation-Agent.git
cd AI-B2B-Lead-Generation-Agent

Create Virtual Environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

3️⃣ Install Dependencies
bash
pip install -r requirements.txt
4️⃣ Install Playwright
bash
playwright install
🚀 How to Run
Run All Modules (Recommended)
bash
python run_all.py
Run Individual Modules
bash
# Module 1: Business Discovery
python src/agents/business_discovery.py

# Module 2: Website Intelligence
python src/agents/website_agent.py

# Module 3: LinkedIn Intelligence
python src/agents/linkedin_agent.py

# Module 4: Decision Maker Finder
python src/agents/decision_maker_agent.py

# Module 5: Website Analysis
python src/agents/website_analysis_agent.py

# Module 6: Lead Qualification
python src/agents/lead_qualification_agent.py

# Module 7: Dataset Generation
python src/agents/dataset_generation_agent.py
Run Streamlit Dashboard
bash
streamlit run streamlit_app.py
🌍 Deployment
Live Demo
https://ai-b2b-lead-generation-agent-4sdmxh5sangfbr64wtrxhu.streamlit.app

Deploy on Streamlit Cloud
Push code to GitHub

Go to share.streamlit.io

Select repository and branch

Set main file: streamlit_app.py

Click Deploy

🧠 Lead Scoring Rules
Criteria	Points
Website Available	+10
Business Email	+10
Contact Email	+10
Phone Number	+10
WhatsApp	+5
Contact Form	+10
LinkedIn Company	+10
Founder Found	+15
CEO Found	+15
Other Decision Makers	+5 each
Priority Country	+20
Company Size >20	+10
SSL	+5
Blog	+5
Social Links	+5
Mobile App	+5
AI Features	+5
Priority Levels:

🔴 High: 70-100

🟡 Medium: 40-69

🟢 Low: 0-39

🌍 Priority Countries
🇺🇸 United States

🇨🇦 Canada

🇬🇧 United Kingdom

🇦🇺 Australia

🇩🇪 Germany

🇳🇱 Netherlands

🇦🇪 United Arab Emirates

🇸🇦 Saudi Arabia

🇶🇦 Qatar

🇰🇼 Kuwait

🇴🇲 Oman

🇸🇬 Singapore

🇵🇰 Pakistan

📁 Datasets Generated
File	Format	Records	Description
business_leads.xlsx	Excel	362	All business leads
cleaned_leads.csv	CSV	362	Deduplicated leads
ml_ready_dataset.csv	CSV	362	ML-ready features
scored_leads.csv	CSV	362	Leads sorted by score
sales_ready_dataset.xlsx	Excel	170	High-priority leads
final_database.csv	CSV	362	Complete database
🛠️ Tech Stack
Category	Technologies
Language	Python 3.11+
Web Scraping	Playwright, BeautifulSoup4, Requests
Data Processing	Pandas, NumPy
Deployment	Streamlit, FastAPI, Docker
ML/AI	Scikit-learn
📹 Demo Video
https://img.youtube.com/vi/VIDEO_ID/0.jpg

Watch the complete project demo above.

📝 Deliverables Checklist
Complete Source Code (7 Modules)

Complete Datasets (6 files)

README.md

requirements.txt

.gitignore

run_all.py

Streamlit Dashboard

GitHub Repository

Demo Video

Project Report

📊 Modules
Module	Description	Status
Module 1	Business Discovery Agent	✅
Module 2	Website Intelligence Agent	✅
Module 3	LinkedIn Intelligence Agent	✅
Module 4	Decision Maker Finder	✅
Module 5	AI Website Analysis Agent	✅
Module 6	AI Lead Qualification Agent	✅
Module 7	Dataset Generation Agent	✅
👨‍💻 Author
Muhammad Usman
Machine Learning Intern
SoftCr8ors

📝 License
MIT License

🙏 Acknowledgments
SoftCr8ors for the opportunity and guidance

Open-source libraries used in this project

📞 Contact
GitHub: SoftCr8orsOfficial

Live Demo: Streamlit App



