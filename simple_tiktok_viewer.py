import requests
import time
import logging

logger = logging.getLogger(__name__)

class SimpleTikTokViewer:
    def watch_video(self, session_id, video_url, watch_time):
        try:
            # Simple HTTP request based approach
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Cookie': f'sessionid={session_id}'
            }
            
            # Make request to video URL
            response = requests.get(video_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Simulate watching time
                actual_time = int(watch_time) if watch_time != 'full' else 30
                time.sleep(actual_time)
                return True, f"Video accessed for {actual_time} seconds"
            else:
                return False, f"Failed to access video: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
