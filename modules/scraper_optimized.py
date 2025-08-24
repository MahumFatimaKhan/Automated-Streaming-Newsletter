"""
Optimized TVInsider scraper using JavaScript batch extraction
"""

import logging
import os
import time
import urllib3
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from config import Config

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class TVInsiderScraperOptimized:
    """Optimized scraper using JavaScript for batch extraction."""
    
    def __init__(self):
        self.base_url = Config.TVINSIDER_BASE_URL
        self.timeout = Config.SCRAPING_TIMEOUT
        self.headless = Config.HEADLESS_BROWSER
        
    def _init_driver(self):
        """Initialize Selenium WebDriver with Chrome."""
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--log-level=3')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        if self.headless:
            options.add_argument('--headless=new')
        
        chrome_driver_path = r"chromedriver-win64\chromedriver.exe"
        
        if not os.path.exists(chrome_driver_path):
            raise Exception(f"ChromeDriver not found at {chrome_driver_path}")
        
        service = Service(chrome_driver_path)
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(self.timeout)
            return driver
        except WebDriverException as e:
            raise Exception(f"Failed to start Chrome: {str(e)}")
    
    def scrape_date_range(self, start_date, end_date):
        """Scrape content using optimized JavaScript extraction."""
        driver = None
        
        try:
            driver = self._init_driver()
            
            # Convert dates for filtering
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            current_year = datetime.now().year
            
            logger.info(f"Loading calendar page: {self.base_url}")
            driver.get(self.base_url)
            time.sleep(3)  # Initial load
            
            # Scroll to load content
            logger.info("Scrolling to load more content...")
            max_scrolls = 10
            for i in range(max_scrolls):
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    logger.info(f"Reached end after {i+1} scrolls")
                    break
            
            # Extract ALL data in one JavaScript call
            logger.info("Extracting all data with JavaScript...")
            all_data = driver.execute_script("""
                function extractAllData() {
                    const results = [];
                    const section = document.querySelector('main section');
                    if (!section) return results;
                    
                    let currentDate = '';
                    const elements = section.children;
                    
                    for (let i = 0; i < elements.length; i++) {
                        const elem = elements[i];
                        
                        // If it's a date header (H6)
                        if (elem.tagName === 'H6') {
                            currentDate = elem.textContent.trim();
                        }
                        // If it's a show/movie link (A)
                        else if (elem.tagName === 'A' && currentDate) {
                            try {
                                const item = {
                                    date_header: currentDate,
                                    name: elem.querySelector('div h3')?.textContent || '',
                                    type: elem.querySelector('div h5')?.textContent || '',
                                    description: elem.querySelector('div p')?.textContent || '',
                                    channel: elem.querySelector('img:first-child')?.alt || '',
                                    channel_image: elem.querySelector('img:first-child')?.src || '',
                                    show_image: elem.querySelector('img:nth-child(2)')?.src || '',
                                    website: elem.href || ''
                                };
                                
                                // Skip empty items
                                if (item.name) {
                                    results.push(item);
                                }
                            } catch (e) {
                                console.error('Error extracting item:', e);
                            }
                        }
                    }
                    
                    return results;
                }
                
                return extractAllData();
            """)
            
            logger.info(f"Extracted {len(all_data)} items from page")
            
            # Process dates and filter
            filtered_data = []
            for item in all_data:
                # Parse the date header
                date_text = item.get('date_header', '')
                parsed_date = self._parse_date(date_text, current_year)
                
                if parsed_date:
                    item['date'] = parsed_date
                    
                    # Filter by date range
                    try:
                        item_date = datetime.strptime(parsed_date, '%Y-%m-%d')
                        if start <= item_date <= end:
                            # Clean up item
                            item.pop('date_header', None)  # Remove temporary field
                            item['channel'] = item['channel'].replace("Parmount+", "Paramount+")
                            filtered_data.append(item)
                    except:
                        pass
            
            # Filter out excluded content
            filtered_data = self._filter_excluded_content(filtered_data)
            
            logger.info(f"Filtered to {len(filtered_data)} items in date range")
            return filtered_data
            
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            raise
        finally:
            if driver:
                driver.quit()
    
    def _parse_date(self, date_text, current_year):
        """Parse various date formats and return YYYY-MM-DD."""
        if not date_text:
            return None
            
        date_text = date_text.strip().title()  # Normalize case
        
        # Try different date formats
        formats = [
            "%A, %B %d, %Y",  # Friday, December 15, 2024
            "%B %d, %Y",      # December 15, 2024
            "%A, %B %d",      # Friday, August 21
            "%B %d"           # August 21
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_text, fmt)
                
                # Add year if not present
                if "%Y" not in fmt:
                    date_obj = date_obj.replace(year=current_year)
                    
                    # Check if date is too far in the past (probably next year)
                    today = datetime.now()
                    if date_obj < today - timedelta(days=30):
                        date_obj = date_obj.replace(year=current_year + 1)
                
                return date_obj.strftime("%Y-%m-%d")
            except:
                continue
        
        return None
    
    def _filter_excluded_content(self, items):
        """Filter out sports and other excluded content."""
        excluded_keywords = [
            'Sports', 'VOD / Buy / Rent', 'YouTube', 'Fox Soccer Plus',
            'ESPN', 'Gold Channel', 'Baseball', 'Cup', 'Football', 'Championship',
            'WWE', 'NFL', 'Tennis', 'Formula 1', 'NBA', 'Apple TV+', 'Soccer',
            'Boxing', 'UFC', 'MMA', 'Golf', 'Hockey', 'Cricket', 'Rugby'
        ]
        
        filtered = []
        for item in items:
            content_text = f"{item.get('name', '')} {item.get('type', '')} {item.get('channel', '')}"
            
            if not any(keyword.lower() in content_text.lower() for keyword in excluded_keywords):
                filtered.append(item)
        
        return filtered