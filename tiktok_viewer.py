from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import logging
import os
import subprocess

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
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-software-rasterizer')
            
            # Anti-detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Find Chrome path
            chrome_path = self.find_chrome_path()
            if chrome_path:
                chrome_options.binary_location = chrome_path
            
            # Setup ChromeDriver with direct path
            chrome_driver_path = "/usr/local/bin/chromedriver"
            
            if os.path.exists(chrome_driver_path):
                service = Service(chrome_driver_path)
            else:
                # Fallback to webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            logger.error(f"Driver setup error: {str(e)}")
            return False
    
    def find_chrome_path(self):
        """Find Chrome installation path"""
        possible_paths = [
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found Chrome at: {path}")
                return path
        
        logger.warning("Chrome not found in standard paths")
        return None
    
    def watch_video(self, session_id, video_url, watch_time):
        try:
            logger.info("Setting up browser...")
            if not self.setup_driver():
                return False, "Browser setup failed"
            
            # Set cookies on TikTok domain
            logger.info("Setting session cookie...")
            self.driver.get("https://www.tiktok.com")
            time.sleep(3)
            
            # Add session cookie
            self.driver.add_cookie({
                'name': 'sessionid',
                'value': session_id,
                'domain': '.tiktok.com',
                'path': '/',
                'secure': True
            })
            
            logger.info(f"Navigating to video: {video_url}")
            self.driver.get(video_url)
            time.sleep(5)  # Wait for page load
            
            # Try to find video element
            try:
                wait = WebDriverWait(self.driver, 15)
                video_element = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
                
                # Play video
                self.driver.execute_script("arguments[0].play();", video_element)
                logger.info("Video started playing")
                
            except Exception as e:
                logger.warning(f"Video auto-play failed: {str(e)}")
                # Continue without auto-play
            
            # Calculate watch time
            if watch_time == 'full':
                try:
                    video_duration = self.driver.execute_script("return arguments[0].duration;", video_element)
                    actual_watch_time = min(video_duration, 60)  # Max 1 minute
                    logger.info(f"Full video duration: {video_duration}s")
                except:
                    actual_watch_time = 30  # Default 30 seconds
            else:
                actual_watch_time = int(watch_time)
            
            logger.info(f"Watching for {actual_watch_time} seconds")
            time.sleep(actual_watch_time)
            
            return True, f"Successfully watched video for {actual_watch_time} seconds"
            
        except Exception as e:
            logger.error(f"Video watching error: {str(e)}")
            return False, f"Failed to watch video: {str(e)}"
        
        finally:
            self.close_driver()
    
    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")

    def check_chrome_installation(self):
        """Check if Chrome is properly installed"""
        try:
            result = subprocess.run(['which', 'google-chrome-stable'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Chrome found at: {result.stdout.strip()}")
                return True
            else:
                logger.error("Chrome not found in system PATH")
                return False
        except Exception as e:
            logger.error(f"Error checking Chrome: {str(e)}")
            return False
