import os
import uuid
import yt_dlp

class AudioDownloader:
    def __init__(self, download_folder='downloads'):
        self.download_folder = download_folder
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def _get_options(self, file_id):
        output_template = os.path.join(self.download_folder, f'{file_id}.%(ext)s')

        return {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': "FFmpegExtractAudio",
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnigs': True
        }
    
    def process_url(self, url: str) -> dict:
        file_id = str(uuid.uuid4())
        opts = self._get_options(file_id)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download= True)
                title = info.get('title', 'audio_desconhecido')

                final_path = os.path.join(self.download_folder, f"{file_id}.mp3")

                return {
                    "path": final_path, 
                    "title": f"{title}.mp3"
                }
        except Exception as e:
            print(f"[Erro Interno]: {e}")
            raise Exception("Falha no download ou conversão")