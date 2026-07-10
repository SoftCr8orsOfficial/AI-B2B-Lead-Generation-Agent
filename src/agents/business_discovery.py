"""
Business Discovery Agent — Complete Working with All Countries
Author: Muhammad Usman | SoftCr8ors
"""

import pandas as pd
import re
import time
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class BusinessDiscovery:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.all_results = []

    def search_google_maps(self, query, location):
        """Scrape Google Maps with updated selectors and timeout"""
        print(f"  [1/4] Google Maps: {location}...", end=" ")
        results = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)  # headless=True for faster
                page = browser.new_page()
                
                search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}+in+{location.replace(' ', '+')}"
                page.goto(search_url, timeout=60000)  # 60 seconds timeout
                page.wait_for_timeout(5000)
                
                # Scroll to load all results
                for i in range(4):
                    page.mouse.wheel(0, 8000)
                    page.wait_for_timeout(2000)
                
                # Updated selectors
                cards = page.query_selector_all('.Nv2PK')
                
                for card in cards[:30]:
                    try:
                        # Name
                        name_elem = card.query_selector('.qBF1Pd')
                        name = name_elem.inner_text().strip() if name_elem else ""
                        
                        if not name:
                            continue
                        
                        # Address
                        address_elem = card.query_selector('.W4Efsd > span:last-child')
                        address = address_elem.inner_text().strip() if address_elem else ""
                        
                        # Phone
                        phone_elem = card.query_selector('.UsdlK')
                        phone = phone_elem.inner_text().strip() if phone_elem else ""
                        
                        # Website
                        website_elem = card.query_selector('a[data-value="Website"]')
                        website = website_elem.get_attribute('href') if website_elem else ""
                        
                        # Rating
                        rating_elem = card.query_selector('.UY7F9')
                        rating = rating_elem.inner_text().strip() if rating_elem else ""
                        
                        # Reviews
                        reviews_elem = card.query_selector('.MW4etd')
                        reviews = reviews_elem.inner_text().strip() if reviews_elem else ""
                        
                        results.append({
                            "company_name": name,
                            "address": address,
                            "phone": phone,
                            "website": website,
                            "rating": rating,
                            "reviews": reviews,
                            "source": "Google Maps",
                            "location": location,
                            "date_collected": datetime.now().strftime("%Y-%m-%d")
                        })
                        
                    except Exception as e:
                        continue
                
                browser.close()
                
        except Exception as e:
            print(f"❌ Timeout/Error: {str(e)[:50]}...")
            return results
        
        print(f"✅ {len(results)} leads")
        return results

    def search_yelp(self, query, location):
        """Scrape Yelp"""
        print(f"  [2/4] Yelp: {location}...", end=" ")
        results = []
        try:
            url = f"https://www.yelp.com/search?find_desc={query.replace(' ', '+')}&find_loc={location.replace(' ', '+')}"
            res = self.session.get(url, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                cards = soup.find_all('div', {'class': re.compile('businessName')})[:30]
                for card in cards:
                    try:
                        name_elem = card.find('a')
                        if name_elem:
                            name = name_elem.get_text(strip=True)
                            if name:
                                results.append({
                                    "company_name": name,
                                    "source": "Yelp",
                                    "location": location,
                                    "date_collected": datetime.now().strftime("%Y-%m-%d")
                                })
                    except:
                        continue
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}...")
            return results
        print(f"✅ {len(results)} leads")
        return results

    def search_yellow_pages(self, query, location):
        """Scrape Yellow Pages"""
        print(f"  [3/4] Yellow Pages: {location}...", end=" ")
        results = []
        try:
            url = f"https://www.yellowpages.com/search?search_terms={query.replace(' ', '+')}&geo_location_terms={location.replace(' ', '+')}"
            res = self.session.get(url, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                cards = soup.find_all('div', class_=re.compile('result'))[:30]
                for card in cards:
                    try:
                        name_elem = card.find('a', class_=re.compile('business-name'))
                        if name_elem:
                            name = name_elem.get_text(strip=True)
                            if name:
                                results.append({
                                    "company_name": name,
                                    "source": "Yellow Pages",
                                    "location": location,
                                    "date_collected": datetime.now().strftime("%Y-%m-%d")
                                })
                    except:
                        continue
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}...")
            return results
        print(f"✅ {len(results)} leads")
        return results

    def search_clutch(self, query, location):
        """Clutch (TODO)"""
        print(f"  [4/4] Clutch: {location}... ⏳ Not implemented")
        return []

    def remove_duplicates(self, data):
        """Remove duplicates based on company name"""
        seen = set()
        unique = []
        for item in data:
            key = item.get('company_name', '').lower().strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(item)
        return unique

    def run(self, query, location):
        """Run all scrapers for a single location"""
        print(f"\n🔍 Searching: {query} in {location}")
        all_data = []
        
        # 1. Google Maps
        time.sleep(random.uniform(1, 3))
        all_data.extend(self.search_google_maps(query, location))
        
        # 2. Yelp
        time.sleep(random.uniform(1, 3))
        all_data.extend(self.search_yelp(query, location))
        
        # 3. Yellow Pages
        time.sleep(random.uniform(1, 3))
        all_data.extend(self.search_yellow_pages(query, location))
        
        # 4. Clutch
        all_data.extend(self.search_clutch(query, location))
        
        return all_data


# ============================================================
# RUN FOR ALL COUNTRIES (TASK + EXTRA)
# ============================================================
if __name__ == "__main__":
    agent = BusinessDiscovery()
    
    # ===== ALL COUNTRIES FROM TASK + EXTRA =====
    cities = [
        # PAKISTAN
        "Lahore, Pakistan",
        "Karachi, Pakistan",
        "Islamabad, Pakistan",
        "Faisalabad, Pakistan",
        
        # UAE
        "Dubai, UAE",
        "Abu Dhabi, UAE",
        
        # SAUDI ARABIA
        "Riyadh, Saudi Arabia",
        "Jeddah, Saudi Arabia",
        
        # QATAR
        "Doha, Qatar",
        
        # KUWAIT
        "Kuwait City, Kuwait",
        
        # OMAN
        "Muscat, Oman",
        
        # USA
        "New York, USA",
        "Los Angeles, USA",
        "Chicago, USA",
        "Houston, USA",
        "Miami, USA",
        
        # UK
        "London, UK",
        "Manchester, UK",
        
        # CANADA
        "Toronto, Canada",
        "Vancouver, Canada",
        
        # AUSTRALIA
        "Sydney, Australia",
        "Melbourne, Australia",
        
        # EUROPE
        "Berlin, Germany",
        "Amsterdam, Netherlands",
        
        # ASIA
        "Singapore",
        "Kuala Lumpur, Malaysia"
    ]
    
    SEARCH_QUERY = "software development company"
    all_results = []
    
    for city in cities:
        print(f"\n{'='*60}")
        print(f"STARTING: {city}")
        print("="*60)
        
        try:
            data = agent.run(SEARCH_QUERY, city)
            if data:
                all_results.extend(data)
                print(f"✅ {city}: {len(data)} leads found")
            else:
                print(f"⚠️ {city}: No leads found")
        except Exception as e:
            print(f"❌ Error in {city}: {e}")
        
        # Delay between cities to avoid blocking
        time.sleep(random.uniform(5, 10))
    
    # Save all results
    if all_results:
        unique_data = agent.remove_duplicates(all_results)
        df = pd.DataFrame(unique_data)
        
        # Ensure columns exist
        required_cols = ['company_name', 'address', 'phone', 'website', 'rating', 'reviews', 'source', 'location', 'date_collected']
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns
        df = df[required_cols]
        
        # Save
        df.to_csv('data/raw/all_countries_leads.csv', index=False)
        
        print(f"\n{'='*60}")
        print(f"🎉 DONE! Total leads collected: {len(df)}")
        print(f"📁 Saved to: data/raw/all_countries_leads.csv")
        print("="*60)
        
        # Summary by location
        print("\n📊 Summary by Location:")
        print(df['location'].value_counts().to_string())
    else:
        print("❌ No leads collected from any location")