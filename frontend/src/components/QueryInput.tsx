import { useState, useEffect } from 'react';
import { Send, Mic, MicOff } from 'lucide-react';
import { motion } from 'framer-motion';

interface QueryInputProps {
  onSend: (query: string, language: "auto" | "en" | "hi") => void;
  disabled: boolean;
}

export function QueryInput({ onSend, disabled }: QueryInputProps) {
  const [query, setQuery] = useState('');
  const [language, setLanguage] = useState<"auto" | "en" | "hi">('auto');
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = false;
        
        rec.onresult = (event: any) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          if (finalTranscript) {
            setQuery(prev => prev + (prev ? ' ' : '') + finalTranscript);
          }
        };
        
        rec.onerror = (event: any) => {
          console.error("Speech recognition error", event.error);
          setIsListening(false);
        };
        
        rec.onend = () => {
          setIsListening(false);
        };
        
        setRecognition(rec);
      }
    }
  }, []);

  // Update language of recognition when language dropdown changes
  useEffect(() => {
    if (recognition) {
      recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    }
  }, [language, recognition]);

  const toggleListening = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!recognition) {
      alert("Speech recognition is not supported in this browser. Try Chrome or Safari.");
      return;
    }
    
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      try {
        recognition.start();
        setIsListening(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSend(query.trim(), language);
      setQuery('');
      if (isListening) {
        recognition?.stop();
        setIsListening(false);
      }
    }
  };

  return (
    <div className="px-4 py-6 bg-transparent z-20 relative">
      <div className="max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="relative group">
          <div className={`overflow-hidden rounded-2xl border bg-white/95 dark:bg-neutral-900/95 backdrop-blur-sm shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all flex items-end ${isListening ? 'border-primary-500 ring-1 ring-primary-500 shadow-[0_0_20px_rgba(16,185,129,0.3)]' : 'border-white/60 dark:border-neutral-800 focus-within:border-primary-500 focus-within:ring-1 focus-within:ring-primary-500'}`}>
            <textarea
              rows={1}
              style={{ boxShadow: 'none' }}
              className="block w-full resize-none border-transparent focus:border-transparent focus:ring-0 outline-none focus:outline-none bg-transparent py-4 pl-5 pr-4 text-slate-900 dark:text-white placeholder:text-slate-400 sm:text-sm sm:leading-6 min-h-[56px] max-h-[120px]"
              placeholder={isListening ? "Listening..." : "Ask a farming question..."}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                  e.currentTarget.style.height = 'auto';
                }
              }}
              disabled={disabled}
            />
            
            <div className="flex items-center space-x-2 py-2 pr-2 shrink-0">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as any)}
                className="h-9 px-2 text-xs font-medium bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 rounded-md text-slate-600 dark:text-neutral-300 focus:ring-slate-500 focus:border-slate-500 hover:bg-slate-50 dark:hover:bg-neutral-800 transition-colors cursor-pointer outline-none"
                disabled={disabled}
              >
                <option value="auto">Auto</option>
                <option value="en">EN</option>
                <option value="hi">HI</option>
              </select>
              
              <motion.button
                whileTap={{ scale: 0.9 }}
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  setTimeout(() => toggleListening(e), 200);
                }}
                className={`inline-flex items-center justify-center p-2.5 rounded-lg focus:outline-none transition-colors cursor-pointer ${isListening ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse' : 'bg-slate-100 dark:bg-neutral-900 text-slate-600 dark:text-neutral-300 hover:bg-slate-200 dark:hover:bg-neutral-800'}`}
                title={isListening ? "Stop recording" : "Start recording"}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </motion.button>
              
              <motion.button
                whileTap={{ scale: 0.9 }}
                type="submit"
                disabled={disabled || !query.trim()}
                onClick={(e) => {
                  e.preventDefault();
                  setTimeout(() => handleSubmit(e as any), 200);
                }}
                className="inline-flex items-center justify-center p-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none disabled:opacity-50 transition-colors cursor-pointer"
              >
                <Send className="w-4 h-4 ml-0.5" />
              </motion.button>
            </div>
          </div>
        </form>
        <div className="text-center mt-4">
          <p className="text-[10px] text-slate-500/80 font-medium">
            AgriGenius provides farming information based on KCC advisory records. It does not replace professional agricultural extension advice.
          </p>
        </div>
      </div>
    </div>
  );
}
