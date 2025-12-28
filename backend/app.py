import os
import uuid
import time

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from downloader_service import AudioDownloader

import yt_dlp

app = Flask(__name__)
CORS(app)

downloader = AudioDownloader(download_folder='downloads')

@app.route('/convert', methods = ['POST'])
def convert_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'URL é obrigatória'}), 400
    
    try:
        result = downloader.process_url(video_url)
        return send_file(
            result['path'],
            as_attachment=True,
            download_name=result['title'],
            mimetype='audio/mpeg'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5000, debug=True)
