import { useState } from 'react';
import { Send, Mic } from 'lucide-react';

interface QueryInputProps {
  onSend: (query: string, language: "auto" | "en" | "hi") => void;
  disabled: boolean;
}

export function QueryInput({ onSend, disabled }: QueryInputProps) {
  const [query, setQuery] = useState('');
  const [language, setLanguage] = useState<"auto" | "en" | "hi">('auto');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSend(query.trim(), language);
      setQuery('');
    }
  };

  return (
    <div className="absolute bottom-6 left-0 right-0 px-4 pointer-events-none">
      <div className="max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="relative group pointer-events-auto">
          <div className="glass-input overflow-hidden rounded-full p-1 flex items-center">
            <textarea
              rows={1}
              className="block w-full resize-none border-0 bg-transparent py-3 pl-5 pr-4 text-slate-900 placeholder:text-slate-400 focus:ring-0 sm:text-sm sm:leading-6 min-h-[44px] max-h-[120px]"
              placeholder="Ask a farming question..."
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
            
            <div className="flex items-center space-x-2 pr-1">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as any)}
                className="h-9 px-2 text-xs font-medium bg-slate-100/50 border border-slate-200/50 rounded-full text-slate-600 focus:ring-primary-500 focus:border-primary-500 hover:bg-slate-200/50 transition-colors cursor-pointer"
                disabled={disabled}
              >
                <option value="auto">Auto</option>
                <option value="en">EN</option>
                <option value="hi">HI</option>
              </select>
              
              <button
                type="button"
                title="Voice input coming soon"
                className="p-2.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-full transition-colors cursor-not-allowed"
              >
                <Mic className="w-4 h-4" />
              </button>
              
              <button
                type="submit"
                disabled={disabled || !query.trim()}
                className="inline-flex items-center justify-center p-2.5 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-full hover:shadow-lg hover:shadow-primary-500/30 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
              >
                <Send className="w-4 h-4 ml-0.5" />
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
