from flask import Flask, request, jsonify, send_file, after_this_request, Response
from pytube import YouTube
import os
import re
import json
from dotenv import load_dotenv
import tempfile
from flask_cors import CORS  # Add this import

load_dotenv()

app = Flask(__name__)
CORS(app)  # Now this will work

DOWNLOAD_FOLDER = tempfile.gettempdir()

# ... rest of your code ...

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    def generate():
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            yield json.dumps({'error': 'URL is required'})
            return
        
        try:
            # Progress updates
            yield json.dumps({'progress': 10, 'message': 'Connecting to YouTube...'})
            
            yt = YouTube(url)
            
            yield json.dumps({'progress': 30, 'message': 'Fetching video info...'})
            
            video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
            audio_streams = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc()
            
            yield json.dumps({'progress': 60, 'message': 'Preparing formats...'})
            
            formats = []
            
            for stream in video_streams:
                formats.append({
                    'itag': stream.itag,
                    'type': 'video',
                    'format': 'mp4',
                    'quality': stream.resolution,
                    'label': f'MP4 {stream.resolution}',
                    'size': stream.filesize_mb
                })
            
            if audio_streams:
                best_audio = audio_streams.first()
                formats.append({
                    'itag': best_audio.itag,
                    'type': 'audio',
                    'format': 'mp3',
                    'quality': best_audio.abr,
                    'label': f'MP3 {best_audio.abr}',
                    'size': best_audio.filesize_mb
                })
            
            yield json.dumps({
                'progress': 100,
                'title': yt.title,
                'thumbnail': yt.thumbnail_url,
                'duration': str(yt.length // 60).zfill(2) + ':' + str(yt.length % 60).zfill(2),
                'views': f"{yt.views:,} views",
                'formats': formats
            })
        
        except Exception as e:
            yield json.dumps({'error': str(e)})

    return Response(generate(), mimetype='application/json')

@app.route('/api/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    itag = request.args.get('itag')
    format_type = request.args.get('format')
    
    if not url or not itag:
        return jsonify({'error': 'URL and itag are required'}), 400
    
    try:
        yt = YouTube(url)
        
        if format_type == 'mp3':
            stream = yt.streams.get_by_itag(itag)
            if not stream:
                return jsonify({'error': 'Requested stream not found'}), 404
            
            temp_file = stream.download(output_path=DOWNLOAD_FOLDER)
            base, _ = os.path.splitext(temp_file)
            new_file = base + '.mp3'
            os.rename(temp_file, new_file)
            
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(new_file)
                except Exception as e:
                    app.logger.error(f"Error removing file {new_file}: {e}")
                return response
            
            filename = sanitize_filename(yt.title) + '.mp3'
            return send_file(new_file, as_attachment=True, download_name=filename, mimetype='audio/mpeg')
        
        else:
            stream = yt.streams.get_by_itag(itag)
            if not stream:
                return jsonify({'error': 'Requested stream not found'}), 404
            
            filename = sanitize_filename(yt.title) + '.mp4'
            temp_file = stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
            
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    app.logger.error(f"Error removing file {temp_file}: {e}")
                return response
            
            return send_file(temp_file, as_attachment=True, download_name=filename, mimetype='video/mp4')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)