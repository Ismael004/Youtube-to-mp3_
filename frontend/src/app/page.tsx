'use client';

import { useState } from 'react';
import { Download, Loader2, Music2, Youtube, Settings2 } from 'lucide-react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [quality, setQuality] = useState('192k');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [progress, setProgress] = useState(0);

  // Extrai ID do vídeo para o Preview
  const getYouTubeID = (url: string) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  const videoId = getYouTubeID(url);

  const startSimulatedProgress = () => {
    setProgress(0);
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 92) {
          clearInterval(interval);
          return prev;
        }
        return prev + (prev < 60 ? 3 : 0.5); // Avança rápido no download, lento na conversão
      });
    }, 200);
    return interval;
  };

  const handleConvert = async () => {
    if (!url) return;

    setStatus('loading');
    setMessage('Conectando ao YouTube...');
    const progressInterval = startSimulatedProgress();

    try {
      const response = await fetch('/api/convert', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, quality }),
      });

      if (!response.ok) throw new Error('Falha na conversão');

      setMessage('Finalizando metadados e baixando...');

      //Ler o nome do arquivo do cabeçalho 
      const filename = response.headers.get('X-Filename') || 'SomTube_Audio.mp3';

      const blob = await response.blob();
      
      clearInterval(progressInterval);
      setProgress(100);

      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename; 
      document.body.appendChild(a);
      a.click();
      a.remove();

      setStatus('success');
      setMessage('Música baixada com sucesso!');
    } catch (err) {
      clearInterval(progressInterval);
      setStatus('error');
      setMessage('Erro ao converter. Verifique o link.');
    } finally {
      setTimeout(() => {
        if (status !== 'loading') {
          setStatus('idle');
          setProgress(0);
        }
      }, 5000);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans p-4 flex flex-col items-center justify-center relative overflow-hidden selection:bg-red-500/30">
      
      {/* Background Effects */}
      <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-red-600/20 blur-[120px] pointer-events-none rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-blue-600/15 blur-[120px] pointer-events-none rounded-full" />

      <div className="w-full max-w-xl z-10 space-y-8">
        
        {/* Header */}
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="bg-red-600 p-4 rounded-2xl shadow-[0_0_40px_rgba(220,38,38,0.5)] transform hover:scale-105 transition-transform duration-300">
            <Music2 className="text-white w-8 h-8" strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="text-5xl font-black tracking-tighter">
              <span className="text-white">Som</span>
              <span className="text-red-500">Tube</span>
            </h1>
            <p className="text-zinc-500 font-medium mt-2">
              Cole o link. Baixe o MP3. Sem complicação.
            </p>
          </div>
        </div>

        {/* Card Principal */}
        <div className="bg-[#0A0A0A]/80 border border-white/5 backdrop-blur-2xl p-6 rounded-3xl shadow-2xl space-y-5 relative overflow-hidden">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1px] bg-gradient-to-r from-transparent via-red-500/50 to-transparent" />

          {/* Input Area */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-4 flex items-center text-zinc-500 group-focus-within:text-red-500 transition-colors">
              <Youtube size={20} />
            </div>
            <input 
              type="text"
              placeholder="https://www.youtube.com/watch?..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full bg-[#121212] border border-zinc-800 rounded-xl py-4 pl-12 pr-32 text-sm outline-none focus:border-red-500/50 focus:ring-1 focus:ring-red-500/50 transition-all placeholder:text-zinc-600"
            />
            
            <div className="absolute inset-y-2 right-2">
              <select 
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                className="h-full bg-zinc-900 text-xs font-medium text-zinc-300 rounded-lg px-3 border border-zinc-700 hover:border-zinc-500 focus:border-red-500 outline-none cursor-pointer transition-colors"
              >
                <option value="128k">128k</option>
                <option value="192k">192k</option>
                <option value="320k">320k</option>
              </select>
            </div>
          </div>

          {/* Video Preview Section */}
          {videoId && (
            <div className="animate-in fade-in zoom-in-95 duration-500">
              <div className="aspect-video w-full rounded-xl overflow-hidden border border-zinc-800 shadow-lg bg-black">
                <iframe 
                  width="100%" height="100%"
                  src={`https://www.youtube.com/embed/${videoId}`}
                  title="YouTube video player"
                  frameBorder="0"
                  referrerPolicy="strict-origin-when-cross-origin"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen
                />
              </div>
            </div>
          )}

          {/* Botão de Ação */}
          <button 
            onClick={handleConvert}
            disabled={status === 'loading' || !url}
            className={`w-full py-4 rounded-xl font-bold text-base flex items-center justify-center gap-2 transition-all active:scale-[0.98]
              ${status === 'loading' 
                ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed' 
                : 'bg-white text-black hover:bg-gray-200 shadow-[0_0_20px_rgba(255,255,255,0.05)]'
              }`}
          >
            {status === 'loading' ? <Loader2 className="animate-spin w-5 h-5" /> : <Download className="w-5 h-5" />}
            {status === 'loading' ? 'Processando...' : 'Converter Agora'}
          </button>

          {/* Barra de Progresso */}
          {status === 'loading' && (
            <div className="space-y-2 animate-in fade-in slide-in-from-top-2 pt-2">
              <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider text-zinc-500">
                <span>{message}</span>
                <span className="text-red-500">{Math.round(progress)}%</span>
              </div>
              <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-600 transition-all duration-300 ease-out shadow-[0_0_10px_rgba(220,38,38,0.8)]"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Rodapé Info */}
        <p className="text-center text-zinc-600 text-xs font-medium">
          © 2026 SomTube. Downloads seguros e rápidos.
        </p>
      </div>
    </div>
  );
}