# backend/downloader_service.py
import os
import uuid
import subprocess
import logging
from typing import Dict, Optional
from pytubefix import YouTube

#Configuração de logs: registra o horário, o nível do erro e a mensagem
logging.basicConfig(level=logging.INFO, format='%(asctime)s -%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioDownloader:
    def __init__(self, download_folder: str ='downloads'):
        self.download_folder = os.path.abspath(download_folder)
        os.makedirs(self.download_foder, exist_ok=True)

    def _sanitize_title(self, title:str) -> str:
        return "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()

    def _get_youtube_instance(self, url:str) -> YouTube:
        return YouTube(url, use_oauth=True, allow_oauth_cache=True)
    
    def _convert_to_mp3(self, input_path: str, output_path: str) -> None:
        command = [
            'ffmpeg', '-y', input_path, 
            '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k',
            output_path
        ]

        try:
            subprocess.run(command, check= True, capture_output=True, timeout=self.ffmpeg_timeout)
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout na conversão: {input_path}")
            raise Exception("A conversão demorou demais.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro no FFmpef: {e.stderr.decode()}")
            raise Exception("Erro técnico na conversão do áudio.")
        
    def process_url(self, url: str) -> Dict[str, str]:
        temp_path: Optional[str] = None
        file_id = str(uuid.uuid4())

        try:
            yt = self._get_youtube_instance(url)
            clean_title = self._sanitize_title(yt.title)

            audio_stream = yt.streams.get_audio_only()
            if not audio_stream:
                raise ValueError("Áudio não disponível para este vídeo.")
            
            temp_path = audio_stream.download(
                output_path=self.download_folder, filename=f"{file_id}_base"
            )

            mp3_path = os.path.join(self.download_folder, f"{file_id}.mp3")
            self._convert_to_mp3(temp_path, mp3_path)

            logger.info(f"Sucesso: {clean_title} ({file_id})")

            return{
                "path": mp3_path,
                "display_name": f"{clean_title}.mp3",
                "id": file_id
            }
        except Exception as e:
            logger.error(f"Falha ao processar URL {url}: {str(e)}")
            raise e
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)