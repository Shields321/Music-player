import yt_dlp as youtube_dl
import os

class MusicDownload:
    def __init__(self) -> None:
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'youtube_downloaded/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],    
        }
        self.title_opts = {
            'quiet': True,              
        }
        self.file_name = None
        
    def download(self, url):
        if self.is_downloaded(url):
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])
        else:
            return "file already downloaded"
            
    def is_downloaded(self, url):
        self.file_name_from_url(url)
        if self.file_name is not None:     
            downloaded_files = self.get_downloaded()
            for name in downloaded_files:                
                # Normalize the filenames by replacing or removing problematic characters
                normalized_name = name.replace('⧸', '/').strip()
                normalized_file_name = self.file_name.replace('⧸', '/').strip()
                
                if normalized_file_name == normalized_name:
                    return False                       
        return True
            
    def get_downloaded(self):        
        files = []
        folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'youtube_downloaded'))  
        if os.path.exists(folder_path):
            for entry in os.listdir(folder_path):
                if entry.lower().endswith(('.ogg', '.wav', '.mp3')):                    
                    files.append(entry)
        return files

    def file_name_from_url(self, url):
        with youtube_dl.YoutubeDL(self.title_opts) as ydl:  # No specific options to ensure full metadata extraction
            info = ydl.extract_info(url, download=False)            
            self.file_name = f"{info.get('title', 'unknown')}.mp3"
            return self.file_name
        
# Example usage

