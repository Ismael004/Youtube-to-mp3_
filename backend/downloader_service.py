# backend/downloader_service.py
import os
import uuid
import subprocess
import logging
import requests
from typing import Dict, Optional
from pytubefix import YouTube
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, error

#Configuração de logs: registra o horário, o nível do erro e a mensagem
logging.basicConfig(level=logging.INFO, format='%(asctime)s -%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#classe responsável por gerenciar o download do vídeo e em converter em MP3.
class AudioDownloader:
    #Inicia a classe, define a pasta e garante que ela exista.
    def __init__(self, download_folder: str ='downloads'):
        self.download_folder = os.path.abspath(download_folder)
        os.makedirs(self.download_folder, exist_ok=True)
        self.ffmpeg_timeout = 300

    #Limpa o título do vídeo para garantir que o nome do arquivo seja aceito
    #pelo sistema operacional, removendo caracteres especiais.
    def _sanitize_title(self, title:str) -> str:
        return "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()

    #Cria a conexão com o Youtube via Pytubefix
    def _get_youtube_instance(self, url:str) -> YouTube:
        return YouTube(url, use_oauth=True, allow_oauth_cache=True)
    
    #Executa o FFmpegem um processo separado para converter o áudio base
    #em um MP3 real de 192kbps
    def _convert_to_mp3(self, input_path: str, output_path: str, quality: str) -> None:
        command = [
            'ffmpeg', '-y', '-i', input_path, 
            '-vn', '-ar', '44100', '-ac', '2', 
            '-b:a', quality,
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
        
    def _inject_metadata(self, mp3_path: str, title: str, author: str, thumb_url: str) -> None:
        try:
            audio = MP3(mp3_path, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass

            audio.tags.add(TIT2(encoding=3, text=title))
            audio.tags.add(TPE1(encoding=3, text=author))

            if thumb_url:
                img_data = requests.get(thumb_url).content
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=img_data
                ))

            audio.save()
            logger.info(f"Metadados injetados em {os.path.basename(mp3_path)}")
        except Exception as e:
            logger.error(f"Falha ao injetar metadados: {str(e)}")

    def process_url(self, url: str, quality: str = '192k') -> Dict[str, str]:
        temp_path: Optional[str] = None
        file_id = str(uuid.uuid4())

        try:
            yt = self._get_youtube_instance(url)
            clean_title = self._sanitize_title(yt.title)
            author = yt.author

            audio_stream = yt.streams.get_audio_only()
            if not audio_stream:
                raise ValueError("Áudio não disponível para este vídeo.")
            
            temp_path = audio_stream.download(
                output_path=self.download_folder, filename=f"{file_id}_base"
            )

            mp3_path = os.path.join(self.download_folder, f"{file_id}.mp3")
            self._convert_to_mp3(temp_path, mp3_path, quality)

            self._inject_metadata(mp3_path, yt.title, author, yt.thumbnail_url)

            logger.info(f"Sucesso: {clean_title} [{quality}] ({file_id})")

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