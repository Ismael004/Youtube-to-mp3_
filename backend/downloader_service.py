# backend/downloader_service.py
import os
import uuid
import subprocess
from pytubefix import YouTube

class AudioDownloader:
    def __init__(self, download_folder='downloads'):
        self.download_folder = download_folder
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def process_url(self, url: str) -> dict:
        try:
            # 1. Cria objeto YouTube com a biblioteca pytubefix
            # 'on_progress_callback' é opcional, tiramos para simplificar
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
            
            title = yt.title.replace('/', '-').replace('\\', '-') # Limpa nome
            file_id = str(uuid.uuid4())
            
            # 2. Pega apenas o áudio (geralmente vem em .m4a ou .webm)
            audio_stream = yt.streams.get_audio_only()
            
            if not audio_stream:
                raise Exception("Não foi possível encontrar stream de áudio.")

            # 3. Baixa o arquivo temporário
            # O pytubefix baixa com o nome original. Vamos renomear depois.
            temp_filename = f"{file_id}_temp"
            downloaded_file_path = audio_stream.download(
                output_path=self.download_folder, 
                filename=temp_filename
            )

            # 4. Converte para MP3 usando FFmpeg (Comando de sistema)
            # Isso é mais robusto que bibliotecas python puras
            mp3_path = os.path.join(self.download_folder, f"{file_id}.mp3")
            
            command = [
                'ffmpeg', 
                '-i', downloaded_file_path,  # Entrada (m4a/webm)
                '-vn',                       # Ignorar vídeo (video null)
                '-ab', '192k',               # Qualidade 192kbps
                '-ar', '44100',              # Frequência
                '-y',                        # Sobrescrever se existir
                mp3_path                     # Saída
            ]
            
            # Executa a conversão silenciosamente
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 5. Remove o arquivo original (temp) para economizar espaço
            if os.path.exists(downloaded_file_path):
                os.remove(downloaded_file_path)

            return {
                "path": mp3_path,
                "title": f"{title}.mp3"
            }

        except Exception as e:
            print(f"Erro no pytubefix: {str(e)}")
            raise Exception(f"Erro ao processar: {str(e)}")