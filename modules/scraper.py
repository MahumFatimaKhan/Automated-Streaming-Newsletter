import logging
import os
import time
import requests
from datetime import datetime, timedelta
import urllib3

# Disable SSL warnings for corporate networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from config import Config

logger = logging.getLogger(__name__)

class TVInsiderScraper:
    """Scraper for TVInsider.com calendar content."""
    
    def __init__(self):
        self.base_url = Config.TVINSIDER_BASE_URL
        self.timeout = Config.SCRAPING_TIMEOUT
        self.headless = Config.HEADLESS_BROWSER
        self.scrape_method = Config.SCRAPE_METHOD
        
    def _init_driver(self):
        """Initialize Selenium WebDriver with Chrome."""
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--log-level=3')
        
        # Add user agent to avoid detection
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if self.headless:
            options.add_argument('--headless=new')  # Use new headless mode
        
        # Use the ChromeDriver from chromedriver-win64 folder
        chrome_driver_path = r"chromedriver-win64\chromedriver.exe"
        
        if not os.path.exists(chrome_driver_path):
            logger.error(f"ChromeDriver not found at: {chrome_driver_path}")
            raise Exception(f"ChromeDriver not found at {chrome_driver_path}. Please ensure chromedriver.exe is in the chromedriver-win64 folder.")
        
        logger.info(f"Using ChromeDriver at: {chrome_driver_path}")
        service = Service(chrome_driver_path)
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            if not self.headless:
                driver.maximize_window()
            # Set timeouts
            driver.set_page_load_timeout(self.timeout)
            driver.implicitly_wait(10)  # Wait up to 10 seconds for elements
        except OSError as e:
            if "WinError 193" in str(e) or "not a valid Win32 application" in str(e):
                logger.error("ChromeDriver architecture mismatch")
                raise Exception(
                    "ChromeDriver architecture mismatch detected. "
                    "Please run 'python fix_chromedriver.py' to download the correct version for your system."
                )
            else:
                logger.error(f"OS error with Chrome driver: {str(e)}")
                raise Exception(f"Chrome driver error: {str(e)}")
        except WebDriverException as e:
            logger.error(f"Chrome driver error: {str(e)}")
            if "chromedriver" in str(e).lower():
                raise Exception(
                    "ChromeDriver not found or incompatible. "
                    "Please run 'python fix_chromedriver.py' to fix this issue."
                )
            else:
                raise Exception(f"Failed to start Chrome. Please ensure Chrome browser is installed. Error: {str(e)}")
        
        return driver
    
    def scrape_date_range(self, start_date, end_date):
        """Scrape content from TVInsider calendar for specific date range."""
        
        # First test if we can reach the website with requests
        try:
            logger.info("Testing network connectivity to TVInsider...")
            # Disable SSL verification for corporate networks with self-signed certificates
            response = requests.get(self.base_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, verify=False)
            if response.status_code == 200:
                logger.info("Network connectivity test successful")
            else:
                logger.warning(f"TVInsider returned status code: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Network connection error: {str(e)}")
            raise Exception("Cannot connect to TVInsider.com. Please check your internet connection.")
        except requests.exceptions.Timeout:
            logger.error("Connection to TVInsider timed out")
            raise Exception("Connection to TVInsider.com timed out. The site may be slow or unavailable.")
        except Exception as e:
            logger.warning(f"Network test warning: {str(e)}")
            # Continue anyway, Selenium might work
        
        if self.scrape_method == 'full_page':
            # Scrape the full calendar page and filter
            return self._scrape_full_calendar_and_filter(start_date, end_date)
        else:
            # Default: Navigate to each date individually
            return self._scrape_by_date_navigation(start_date, end_date)
    
    def _scrape_by_date_navigation(self, start_date, end_date):
        """Stay on base calendar URL and scrape content using optimized JavaScript extraction."""
        driver = None
        
        try:
            driver = self._init_driver()
            
            # Convert dates for filtering
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            current_year = datetime.now().year
            
            logger.info(f"Loading calendar page: {self.base_url}")
            try:
                driver.get(self.base_url)
                time.sleep(3)  # Initial load
            except Exception as e:
                if "timeout" in str(e).lower():
                    logger.error(f"Timeout loading page: {str(e)}")
                    raise Exception("Website timeout: The TVInsider website is not responding. Please try again later.")
                else:
                    raise
            
            logger.info(f"Scraping content from {start_date} to {end_date}")
            
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
            
            # Extract ALL data in one JavaScript call - OPTIMIZED
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
                                    website: elem.href || '',
                                    website_url: '',
                                    country: 'US'
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
                parsed_date = self._parse_date_optimized(date_text, current_year)
                
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
    
    def _scrape_full_calendar_and_filter(self, start_date, end_date):
        """Scrape the full calendar page using optimized JavaScript extraction."""
        # Use the same optimized method as _scrape_by_date_navigation
        return self._scrape_by_date_navigation(start_date, end_date)
    
    def _parse_date_optimized(self, date_text, current_year):
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
    
    
    
    def _filter_by_date_range(self, items, start_date, end_date):
        """Filter items by date range."""
        filtered = []
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            for item in items:
                if item.get('date'):
                    try:
                        item_date = datetime.strptime(item['date'], '%Y-%m-%d')
                        if start <= item_date <= end:
                            filtered.append(item)
                    except:
                        # If date parsing fails, include the item
                        filtered.append(item)
                else:
                    # If no date, include the item
                    filtered.append(item)
                    
        except Exception as e:
            logger.error(f"Error filtering by date: {str(e)}")
            return items
        
        return filtered
    
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
            # Check if any excluded keyword is in name, type, or channel
            content_text = f"{item.get('name', '')} {item.get('type', '')} {item.get('channel', '')}"
            
            if not any(keyword.lower() in content_text.lower() for keyword in excluded_keywords):
                filtered.append(item)
            else:
                logger.debug(f"Filtered out: {item.get('name', 'Unknown')}")
        
        return filtered