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
            
            # Production settings
            if os.environ.get('RENDER'):
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
            
            # Anti-detection settings
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # Setup driver
            if os.environ.get('RENDER'):
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set session cookie
            self.driver.get("https://www.tiktok.com")
            self.driver.add_cookie({
                'name': 'sessionid',
                'value': session_id,
                'domain': '.tiktok.com',
                'path': '/',
                'secure': True
            })
            
            logger.info("Driver setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Driver setup failed: {str(e)}")
            return False
    
    def watch_video(self, session_id, video_url, watch_time):
        try:
            # Setup driver
            if not self.setup_driver(session_id):
                return False, "Failed to setup browser"
            
            # Navigate to video
            logger.info(f"Navigating to video: {video_url}")
            self.driver.get(video_url)
            
            # Wait for video to load
            wait = WebDriverWait(self.driver, 15)
            video_element = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # Play video
            self.driver.execute_script("arguments[0].play();", video_element)
            logger.info("Video started playing")
            
            # Get video duration for full video watch
            if watch_time == 'full':
                video_duration = self.driver.execute_script("return arguments[0].duration;", video_element)
                actual_watch_time = min(video_duration, 300)  # Max 5 minutes even for full video
                logger.info(f"Full video duration: {video_duration}s, watching for: {actual_watch_time}s")
            else:
                actual_watch_time = int(watch_time)
                logger.info(f"Watching for custom time: {actual_watch_time}s")
            
            # Watch for specified time
            time.sleep(actual_watch_time)
            
            # Take screenshot for debugging (optional)
            if os.environ.get('DEBUG'):
                self.driver.save_screenshot('video_watched.png')
            
            logger.info(f"Successfully watched video for {actual_watch_time} seconds")
            return True, f"Video watched for {actual_watch_time} seconds"
            
        except Exception as e:
            logger.error(f"Error watching video: {str(e)}")
            return False, f"Failed to watch video: {str(e)}"
        
        finally:
            self.close_driver()
    
    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing driver: {str(e)}")