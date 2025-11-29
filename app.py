from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tiktok_viewer import TikTokViewer
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"],
    storage_uri="memory://"
)

viewer = TikTokViewer()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/watch', methods=['POST'])
@limiter.limit("5 per minute")
def watch_video():
    try:
        # Log the request
        logger.info("Received watch request")
        
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'success': False, 'error': 'No data received'})
        
        session_id = data.get('sessionId', '').strip()
        video_url = data.get('videoUrl', '').strip()
        watch_time = data.get('watchTime', '20')
        
        logger.info(f"Session ID: {session_id[:10]}...")
        logger.info(f"Video URL: {video_url}")
        logger.info(f"Watch Time: {watch_time}")
        
        # Validation
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID is required'})
        
        if not video_url:
            return jsonify({'success': False, 'error': 'Video URL is required'})
        
        if not video_url.startswith('https://www.tiktok.com/'):
            return jsonify({'success': False, 'error': 'Invalid TikTok URL'})
        
        # Process video
        logger.info("Starting video processing...")
        success, message = viewer.watch_video(session_id, video_url, watch_time)
        
        response_data = {
            'success': success, 
            'message': message
        }
        
        logger.info(f"Response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/test')
def test():
    return jsonify({'status': 'working', 'message': 'Server is running'})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
