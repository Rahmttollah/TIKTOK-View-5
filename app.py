from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tiktok_viewer import TikTokViewer
import os

app = Flask(__name__)

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
        data = request.get_json()
        session_id = data.get('sessionId', '').strip()
        video_url = data.get('videoUrl', '').strip()
        watch_time = data.get('watchTime', '20')
        
        if not session_id or not video_url:
            return jsonify({'success': False, 'error': 'Session ID and Video URL required'})
        
        success, message = viewer.watch_video(session_id, video_url, watch_time)
        
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
