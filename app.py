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

# Rate limiting setup
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"],
    storage_uri="memory://"
)

# Initialize TikTok viewer
viewer = TikTokViewer()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/watch', methods=['POST'])
@limiter.limit("8 per minute")
def watch_video():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        session_id = data.get('sessionId', '').strip()
        video_url = data.get('videoUrl', '').strip()
        watch_time = data.get('watchTime', '30')
        
        # Validation
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID is required'})
        
        if not video_url:
            return jsonify({'success': False, 'error': 'Video URL is required'})
        
        if not video_url.startswith('https://www.tiktok.com/') or '/video/' not in video_url:
            return jsonify({'success': False, 'error': 'Invalid TikTok URL'})
        
        logger.info(f"Processing video: {video_url[:50]}...")
        
        # Watch video
        success, message = viewer.watch_video(session_id, video_url, watch_time)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'watchTime': watch_time
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            })
            
    except Exception as e:
        logger.error(f"Error in watch_video: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'TikTok Viewer is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)