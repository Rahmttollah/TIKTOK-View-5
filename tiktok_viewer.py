from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import logging
import os

logger = logging.getLogger(__name__)

class TikTokViewer:
    def __init__(self):
        self.driver = None
    
    def setup_driver(self):
        try:
            chrome_options = Options()
            
            # Render settings
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Anti-detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Install and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            logger.error(f"Driver setup error: {str(e)}")
            return False
    
    def watch_video(self, session_id, video_url, watch_time):
        try:
            logger.info("Setting up browser...")
            if not self.setup_driver():
                return False, "Browser setup failed"
            
            # First, set cookies on TikTok domain
            logger.info("Setting session cookie...")
            self.driver.get("https://www.tiktok.com")
            time.sleep(2)
            
            # Add session cookie
            self.driver.add_cookie({
                'name': 'sessionid',
                'value': session_id,
                'domain': '.tiktok.com',
                'path': '/',
                'secure': True,
                'httpOnly': True
            })
            
            logger.info(f"Navigating to video: {video_url}")
            self.driver.get(video_url)
            time.sleep(5)  # Wait for page load
            
            # Try to find and play video
            try:
                wait = WebDriverWait(self.driver, 10)
                video_element = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
                
                # Play video
                self.driver.execute_script("arguments[0].play();", video_element)
                logger.info("Video started playing")
                
            except Exception as e:
                logger.warning(f"Could not play video automatically: {str(e)}")
                # Continue even if auto-play fails
            
            # Calculate watch time
            if watch_time == 'full':
                try:
                    video_duration = self.driver.execute_script("return arguments[0].duration;", video_element)
                    actual_watch_time = min(video_duration, 120)  # Max 2 minutes
                except:
                    actual_watch_time = 30  # Default 30 seconds
            else:
                actual_watch_time = int(watch_time)
            
            logger.info(f"Watching for {actual_watch_time} seconds")
            time.sleep(actual_watch_time)
            
            return True, f"Video watched for {actual_watch_time} seconds"
            
        except Exception as e:
            logger.error(f"Video watching error: {str(e)}")
            return False, f"Failed to watch video: {str(e)}"
        
        finally:
            self.close_driver()
    
    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
