import requests
import time
import random
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SimpleTikTokViewer:
    def __init__(self):
        self.session = requests.Session()
        
    def watch_video(self, session_id, video_url, watch_time):
        try:
            logger.info(f"Starting video watch: {video_url}")
            
            # Extract video ID from URL
            video_id = self.extract_video_id(video_url)
            if not video_id:
                return False, "Invalid TikTok video URL"
            
            # Prepare headers with session ID
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cookie': f'sessionid={session_id}'
            }
            
            # First, check if session is valid by accessing TikTok
            logger.info("Validating session...")
            check_response = self.session.get(
                'https://www.tiktok.com/foryou',
                headers=headers,
                timeout=10
            )
            
            if check_response.status_code != 200:
                return False, "Invalid session ID or session expired"
            
            # Access the video page
            logger.info(f"Accessing video: {video_url}")
            response = self.session.get(
                video_url,
                headers=headers,
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                # Simulate watching time
                actual_time = int(watch_time) if watch_time != 'full' else 30
                
                logger.info(f"Video accessed successfully, simulating watch time: {actual_time}s")
                
                # Multiple requests to simulate watching behavior
                for i in range(actual_time // 5):
                    if i > 0:  # Don't make request on first iteration
                        time.sleep(5)
                        
                        # Make additional request to simulate engagement
                        try:
                            self.session.get(video_url, headers=headers, timeout=5)
                        except:
                            pass
                    
                return True, f"Video watched for {actual_time} seconds"
            else:
                return False, f"Failed to access video (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            return False, "Request timeout - check your internet connection"
        except requests.exceptions.ConnectionError:
            return False, "Connection error - cannot reach TikTok"
        except Exception as e:
            logger.error(f"Error watching video: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def extract_video_id(self, url):
        """Extract video ID from TikTok URL"""
        try:
            # Handle different TikTok URL formats
            if '/video/' in url:
                parts = url.split('/video/')
                if len(parts) > 1:
                    video_part = parts[1]
                    # Remove query parameters
                    video_id = video_part.split('?')[0]
                    return video_id if video_id.isdigit() else None
            return None
        except:
            return None
    
    def validate_session(self, session_id):
        """Validate if session ID is working"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
                'Cookie': f'sessionid={session_id}'
            }
            
            response = self.session.get(
                'https://www.tiktok.com/foryou',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        except:
            return False
