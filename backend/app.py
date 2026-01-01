import os
import uuid
import time
import logging

from flask import Flask, after_this_request, request, send_file, jsonify, make_response
from flask_cors import CORS
from downloader_service import AudioDownloader

#Configuração de logs: registra o horário, o nível do erro e a mensagem
logging.basicConfig(level=logging.INFO, format='%(asctime)s -%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, expose_headers=["X-Filename"])

downloader = AudioDownloader(download_folder='downloads')

@app.route('/convert', methods = ['POST'])
def convert_video():
    data = request.json
    video_url = data.get('url')

    quality = data.get('quality', '192k')

    if not video_url:
        logger.warning("Tentativa de conversão sem URL")
        return jsonify({'error': 'URL é obrigatória'}), 400
    
    #Chama o serviço para realizar download e a conversão
    try:
        result = downloader.process_url(video_url, quality)
        file_path = result['path']
        display_name = result['display_name']

        abs_file_path = os.path.abspath(file_path)
        #Inicia a lógica de Auto-Limpeza
        #Evita que o servidor não acumule arquivos
        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(abs_file_path):
                    os.remove(abs_file_path)
                    logger.info(f"Arquivo temporário removido do servidor: {file_path}")
            except Exception as e:
                logger.error(f"Falha ao deletar arquivo pós-processamento: {e}")
            return response

        #Retorna o arquivo MP3 para o navegador
        response = make_response(send_file(
            abs_file_path, 
            as_attachment=True, 
            download_name=display_name, 
            mimetype='audio/mpeg'))

        response.headers['X-Filename'] = display_name
        return response

    except Exception as e:
        #Registra o erro detalhado no log do servidor
        logger.error(f"Erro ao processar requisição: {str(e)}")
        return jsonify({'error': 'Falha interna ao converter áudio. Verifique o link.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)