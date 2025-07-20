import os
import time
import json
import hashlib
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup

class WebTextScraper:
    def __init__(self, base_url, output_folder="scraped_content"):
        self.base_url = base_url
        self.output_folder = output_folder
        self.visited_urls = set()
        self.failed_urls = set()
        self.session_file = os.path.join(output_folder, "scraping_session.json")
        
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(os.path.join(output_folder, "pages"), exist_ok=True)
        os.makedirs(os.path.join(output_folder, "metadata"), exist_ok=True)
        
        self.load_session()
        
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize the WebDriver with optimized settings"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
    
    def load_session(self):
        """Load previously visited URLs from session file"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    self.visited_urls = set(session_data.get('visited_urls', []))
                    self.failed_urls = set(session_data.get('failed_urls', []))
                print(f"Loaded session: {len(self.visited_urls)} visited URLs, {len(self.failed_urls)} failed URLs")
            except Exception as e:
                print(f"Error loading session: {e}")
    
    def save_session(self):
        """Save current session state"""
        session_data = {
            'visited_urls': list(self.visited_urls),
            'failed_urls': list(self.failed_urls),
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def generate_filename(self, url, title=None):
        """Generate a safe filename from URL and title"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        if title:
            # Clean title for filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:50]  # Limit length
            return f"{safe_title}_{url_hash}.txt"
        else:
            parsed_url = urlparse(url)
            path_name = parsed_url.path.replace('/', '_').strip('_')
            if not path_name:
                path_name = "homepage"
            return f"{path_name}_{url_hash}.txt"
    
    def extract_text_content(self, url):
        """Extract clean text content from a webpage"""
        try:
            self.driver.get(url)
            time.sleep(2)  # Allow page to load
            
            title = self.driver.title
            
            # Extract main content using multiple strategies
            content_selectors = [
                'main', 'article', '.content', '#content', '.main-content',
                '.post-content', '.entry-content', 'body'
            ]
            
            text_content = ""
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        html = elements[0].get_attribute('innerHTML')
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                            script.decompose()
                        
                        text_content = soup.get_text(separator='\n', strip=True)
                        break
                except:
                    continue
            
            if not text_content.strip():
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                text_content = soup.get_text(separator='\n', strip=True)
            
            return {
                'title': title,
                'content': text_content,
                'url': url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None
    
    def find_dropdown_links(self):
        """Find all dropdown menus and extract links"""
        dropdown_links = set()
        
        try:
            # Find dropdown triggers (common patterns)
            dropdown_selectors = [
                'select',  # Standard select dropdowns
                '.dropdown', '.dropdown-menu', '.dropdown-content',
                '[role="menu"]', '[role="listbox"]',
                'nav ul li ul', 'nav ol li ol',  # Nested navigation
                '.menu-item-has-children'
            ]
            
            for selector in dropdown_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        # Handle select dropdowns
                        if element.tag_name == 'select':
                            select_obj = Select(element)
                            for option in select_obj.options:
                                value = option.get_attribute('value')
                                if value and value.startswith(('http', '/')):
                                    dropdown_links.add(urljoin(self.base_url, value))
                        
                        # Handle other dropdown types
                        else:
                            # Try clicking to reveal dropdown
                            try:
                                self.driver.execute_script("arguments[0].click();", element)
                                time.sleep(1)
                            except:
                                pass
                            
                            # Extract links from dropdown
                            links = element.find_elements(By.TAG_NAME, 'a')
                            for link in links:
                                href = link.get_attribute('href')
                                if href and not href.startswith('javascript:'):
                                    dropdown_links.add(href)
                
                except Exception as e:
                    continue
            
            # Also find regular navigation links
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, 'nav a, .navigation a, .menu a')
            for link in nav_links:
                href = link.get_attribute('href')
                if href and not href.startswith('javascript:'):
                    dropdown_links.add(href)
            
        except Exception as e:
            print(f"Error finding dropdown links: {e}")
        
        # Filter to same domain links only
        same_domain_links = set()
        base_domain = urlparse(self.base_url).netloc
        
        for link in dropdown_links:
            try:
                link_domain = urlparse(link).netloc
                if not link_domain or link_domain == base_domain:
                    same_domain_links.add(urljoin(self.base_url, link))
            except:
                continue
        
        return same_domain_links
    
    def save_content(self, content_data):
        """Save extracted content to file"""
        if not content_data:
            return False
        
        filename = self.generate_filename(content_data['url'], content_data['title'])
        filepath = os.path.join(self.output_folder, "pages", filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {content_data['title']}\n")
                f.write(f"URL: {content_data['url']}\n")
                f.write(f"Scraped: {content_data['timestamp']}\n")
                f.write("=" * 80 + "\n\n")
                f.write(content_data['content'])
            
            # Save metadata
            metadata_file = os.path.join(self.output_folder, "metadata", f"{filename}.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'title': content_data['title'],
                    'url': content_data['url'],
                    'timestamp': content_data['timestamp'],
                    'filename': filename,
                    'content_length': len(content_data['content'])
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving {filename}: {e}")
            return False
    
    def scrape_website(self, max_pages=50, delay=2):
        """Main scraping function"""
        print(f"Starting scrape of {self.base_url}")
        print(f"Output folder: {self.output_folder}")
        
        try:
            # Start with base URL
            urls_to_visit = [self.base_url]
            
            # First, discover all dropdown/navigation links
            self.driver.get(self.base_url)
            time.sleep(3)
            
            discovered_links = self.find_dropdown_links()
            urls_to_visit.extend(discovered_links)
            
            print(f"Found {len(urls_to_visit)} URLs to process")
            
            successful_downloads = 0
            
            for i, url in enumerate(urls_to_visit[:max_pages]):
                if url in self.visited_urls:
                    print(f"⏭ Skipping already visited: {url}")
                    continue
                
                if url in self.failed_urls:
                    print(f"⏭ Skipping previously failed: {url}")
                    continue
                
                print(f"Processing ({i+1}/{min(len(urls_to_visit), max_pages)}): {url}")
                
                try:
                    content_data = self.extract_text_content(url)
                    
                    if content_data and content_data['content'].strip():
                        if self.save_content(content_data):
                            successful_downloads += 1
                            self.visited_urls.add(url)
                        else:
                            self.failed_urls.add(url)
                    else:
                        print(f"No content extracted from {url}")
                        self.failed_urls.add(url)
                
                except Exception as e:
                    print(f"✗ Error processing {url}: {e}")
                    self.failed_urls.add(url)
                
                # Save session periodically
                if i % 5 == 0:
                    self.save_session()
                
                time.sleep(delay)  # Rate limiting
            
            print(f"\nScraping complete!")
            print(f"Successfully downloaded: {successful_downloads} pages")
            print(f"Already visited: {len(self.visited_urls) - successful_downloads}")
            print(f"Failed: {len(self.failed_urls)}")
            
        finally:
            self.save_session()
            self.driver.quit()

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <website_url> [max_pages] [delay]")
        print("Example: python scraper.py https://example.com 50 2")
        sys.exit(1)
    
    website_url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    delay = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    if not website_url.startswith(('http://', 'https://')):
        website_url = 'https://' + website_url
    
    print(f"Target website: {website_url}")
    print(f"Max pages: {max_pages}")
    print(f"Delay between requests: {delay} seconds")
    print("-" * 50)
    
    scraper = WebTextScraper(website_url, "scraped_content")
    scraper.scrape_website(max_pages=max_pages, delay=delay)
