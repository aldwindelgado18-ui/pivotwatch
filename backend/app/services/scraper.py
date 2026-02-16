import asyncio
import hashlib
from datetime import datetime
from typing import Dict, Optional, Tuple
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import os
from ..core.config import settings

class WebsiteScraper:
    """Main scraper service for capturing website content"""
    
    def __init__(self):
        self.screenshot_dir = settings.SCREENSHOT_PATH
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    async def scrape(self, url: str, company_id: str) -> Dict:
        """
        Scrape a website and return structured content
        """
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='PivotWatch/1.0 (Competitor Monitoring Bot)'
            )
            page = await context.new_page()
            
            try:
                # Navigate to URL
                print(f"🌐 Scraping {url}...")
                response = await page.goto(url, wait_until='networkidle', timeout=30000)
                
                if not response.ok:
                    raise Exception(f"HTTP {response.status}: {response.status_text}")
                
                # Wait for page to stabilize
                await page.wait_for_timeout(2000)
                
                # Extract data
                title = await page.title()
                html_content = await page.content()
                
                # Clean HTML for storage (remove scripts, etc.)
                soup = BeautifulSoup(html_content, 'lxml')
                for script in soup(["script", "style", "meta", "link"]):
                    script.decompose()
                
                cleaned_html = str(soup)
                text_content = soup.get_text(separator='\n', strip=True)
                
                # Generate hash for comparison
                html_hash = hashlib.sha256(cleaned_html.encode()).hexdigest()
                
                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_filename = f"{company_id}_{timestamp}.png"
                screenshot_path = os.path.join(self.screenshot_dir, screenshot_filename)
                
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Get page metadata
                metadata = {
                    'url': url,
                    'status_code': response.status,
                    'load_time': await self._get_load_time(page),
                    'viewport_size': {'width': 1920, 'height': 1080},
                    'content_length': len(html_content),
                }
                
                return {
                    'success': True,
                    'title': title,
                    'html_content': cleaned_html,
                    'text_content': text_content,
                    'html_hash': html_hash,
                    'screenshot_path': screenshot_path,
                    'metadata': metadata,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                print(f"❌ Error scraping {url}: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'url': url,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            finally:
                await browser.close()
    
    async def _get_load_time(self, page: Page) -> float:
        """Get page load performance metrics"""
        try:
            metrics = await page.evaluate('''() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                return perfData ? perfData.loadEventEnd - perfData.startTime : 0;
            }''')
            return metrics
        except:
            return 0.0
    
    def compare_with_previous(self, current: Dict, previous: Dict) -> Dict:
        """
        Compare current scrape with previous version
        """
        if not previous:
            return {'has_changes': False, 'is_first': True}
        
        # Check if content changed
        html_changed = current['html_hash'] != previous.get('html_hash')
        
        if not html_changed:
            return {'has_changes': False}
        
        # Find differences in text
        from difflib import SequenceMatcher
        
        old_text = previous.get('text_content', '')
        new_text = current.get('text_content', '')
        
        matcher = SequenceMatcher(None, old_text, new_text)
        similarity_ratio = matcher.ratio()
        
        # Extract changed sections
        changes = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                changes.append({
                    'type': tag,  # 'replace', 'delete', 'insert'
                    'old_section': old_text[i1:i2][:200],  # Truncate for storage
                    'new_section': new_text[j1:j2][:200],
                    'old_context': old_text[max(0, i1-100):min(len(old_text), i2+100)],
                    'new_context': new_text[max(0, j1-100):min(len(new_text), j2+100)]
                })
        
        return {
            'has_changes': True,
            'similarity_ratio': similarity_ratio,
            'change_count': len(changes),
            'changes': changes[:10]  # Limit to top 10 changes
        }