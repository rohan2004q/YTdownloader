import os
import re
from pytube import YouTube
import tempfile

class YouTubeDownloader:
    def __init__(self):
        self.download_folder = tempfile.gettempdir()
    
    def sanitize_filename(self, filename):
        """Sanitize the filename to remove invalid characters."""
        return re.sub(r'[\\/*?:"<>|]', "", filename)
    
    def get_video_info(self, url):
        """Get video information and available formats."""
        try:
            yt = YouTube(url)
            
            # Get available streams
            video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
            audio_streams = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc()
            
            # Prepare formats data
            formats = []
            
            # Add video formats
            for stream in video_streams:
                formats.append({
                    'itag': stream.itag,
                    'type': 'video',
                    'format': 'mp4',
                    'quality': stream.resolution,
                    'label': f'MP4 {stream.resolution}',
                    'size': stream.filesize_mb
                })
            
            # Add audio format
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
            
            # Prepare response
            response = {
                'title': yt.title,
                'thumbnail': yt.thumbnail_url,
                'duration': str(yt.length // 60).zfill(2) + ':' + str(yt.length % 60).zfill(2),
                'views': f"{yt.views:,} views",
                'formats': formats
            }
            
            return response
        
        except Exception as e:
            return {'error': str(e)}
    
    def download_video(self, url, itag, format_type, custom_filename=None):
        """Download video or audio from YouTube."""
        try:
            yt = YouTube(url)
            
            if format_type == 'mp3':
                stream = yt.streams.get_by_itag(itag)
                if not stream:
                    return {'error': 'Requested stream not found'}
                
                # Download audio
                temp_file = stream.download(output_path=self.download_folder)
                base, _ = os.path.splitext(temp_file)
                new_file = base + '.mp3'
                os.rename(temp_file, new_file)
                
                filename = custom_filename if custom_filename else self.sanitize_filename(yt.title) + '.mp3'
                final_path = os.path.join(self.download_folder, filename)
                
                # Rename to final filename
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(new_file, final_path)
                
                return {'success': True, 'filepath': final_path, 'filename': filename}
            
            else:
                # Download video
                stream = yt.streams.get_by_itag(itag)
                if not stream:
                    return {'error': 'Requested stream not found'}
                
                filename = custom_filename if custom_filename else self.sanitize_filename(yt.title) + '.mp4'
                final_path = os.path.join(self.download_folder, filename)
                
                # Remove if file already exists
                if os.path.exists(final_path):
                    os.remove(final_path)
                
                stream.download(output_path=self.download_folder, filename=filename)
                
                return {'success': True, 'filepath': final_path, 'filename': filename}
        
        except Exception as e:
            return {'error': str(e)}

# Example usage
if __name__ == '__main__':
    downloader = YouTubeDownloader()
    
    # Get video info
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    info = downloader.get_video_info(url)
    print("Video Info:", info)
    
    # Download video (uncomment to test)
    # if 'error' not in info:
    #     # Download highest quality video
    #     video_format = next(f for f in info['formats'] if f['type'] == 'video')
    #     result = downloader.download_video(url, video_format['itag'], video_format['format'])
    #     print("Download Result:", result)
    
    #     # Download audio
    #     audio_format = next(f for f in info['formats'] if f['type'] == 'audio')
    #     result = downloader.download_video(url, audio_format['itag'], audio_format['format'])
    #     print("Download Result:", result)