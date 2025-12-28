'use client'

import {useState} from 'react';

export default function Home(){
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState('parado');

  const BACKEND_URL = 'https://verbose-space-rotary-phone-7gx4x5p995pfp4xg-5000.app.github.dev'

  async function converterVideo(){
    if (!url) return alert('Coloque um link!');

    setStatus('Processando no Python')

    try{
      const resposta = await fetch(`${BACKEND_URL}/convert`, {
        method: 'POST', 
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({url:url})
      });

      if (!resposta.ok) throw new Error('Erro no servidor');

      setStatus('Baixando o arquivo');
      const blob = await resposta.blob();
      const linkDownload = window.URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = linkDownload;
      a.download = "musica_baixada.mp3";
      document.body.appendChild(a);
      a.click();
      a.remove();

      setStatus('Sucesso');

    } catch(erro){
      console.error(erro);
      setStatus('Deu erro. Olhe o console')
    }
  }

  return (
    <div style = {{
      padding: '50px',
      fontFamily: 'sans-serif',
      textAlign: 'center'
    }}>
      <h1>Testador de Conversão</h1>
      <div style = {{display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px', margin: '0 auto'}}>
        <input type="text" 
        placeholder="Cole o link aqui" 
        value={url} 
        onChange = {(e) => setUrl(e.target.value)}
        style = {{padding: '10px', fontSize: '16px'}}
        />

        <button 
        onClick = {converterVideo}
        style={{ padding: '15px', backgroundColor: 'blue', color: 'white', border : 'none', cursor: 'pointer', fontSize: '16px'}}>
          Converter agora
        </button>

        <div style = {{marginTop: '20px', fontWeight: 'bold'}}>
          Status: {status}
        </div>
      </div>
    </div>
  );
}