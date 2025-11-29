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
    
    def setup_driver(self, session_id):
        try:
            chrome_options = Options()
            
            # Render-specific settings
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            
            # Anti-detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--window-size=1920,1080")
            
            # User agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # ChromeDriver setup for Render
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set session cookie
            self.driver.get("https://www.tiktok.com")
            time.sleep(2)
            
            self.driver.add_cookie({
                'name': 'sessionid',
                'value': session_id,
                'domain': '.tiktok.com',
                'path': '/',
                'secure': True
            })
            
            logger.info("Driver setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Driver setup failed: {str(e)}")
            return False
    
    def watch_video(self, session_id, video_url, watch_time):
        try:
            if not self.setup_driver(session_id):
                return False, "Browser setup failed"
            
            logger.info(f"Opening video: {video_url}")
            self.driver.get(video_url)
            time.sleep(3)
            
            # Wait for video element
            wait = WebDriverWait(self.driver, 10)
            video_element = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # Play video
            self.driver.execute_script("arguments[0].play();", video_element)
            logger.info("Video started playing")
            
            # Calculate watch time
            if watch_time == 'full':
                video_duration = self.driver.execute_script("return arguments[0].duration;", video_element)
                actual_watch_time = min(video_duration, 180)  # Max 3 minutes
            else:
                actual_watch_time = int(watch_time)
            
            logger.info(f"Watching for {actual_watch_time} seconds")
            time.sleep(actual_watch_time)
            
            return True, f"Successfully watched for {actual_watch_time} seconds"
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False, f"Failed: {str(e)}"
        
        finally:
            self.close_driver()
    
    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
