import { useState } from 'react';
import { Send } from 'lucide-react';

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
    <div className="p-4 bg-white border-t border-slate-100 z-20">
      <div className="max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="relative group">
          <div className="overflow-hidden rounded-xl border border-slate-300 bg-white focus-within:border-slate-600 focus-within:ring-1 focus-within:ring-slate-600 transition-all flex items-end">
            <textarea
              rows={1}
              className="block w-full resize-none border-0 bg-transparent py-4 pl-5 pr-4 text-slate-900 placeholder:text-slate-400 focus:ring-0 sm:text-sm sm:leading-6 min-h-[56px] max-h-[120px]"
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
            
            <div className="flex items-center space-x-2 py-2 pr-2 shrink-0">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as any)}
                className="h-9 px-2 text-xs font-medium bg-white border border-slate-200 rounded-md text-slate-600 focus:ring-slate-500 focus:border-slate-500 hover:bg-slate-50 transition-colors cursor-pointer"
                disabled={disabled}
              >
                <option value="auto">Auto</option>
                <option value="en">EN</option>
                <option value="hi">HI</option>
              </select>
              
              <button
                type="submit"
                disabled={disabled || !query.trim()}
                className="inline-flex items-center justify-center p-2.5 bg-amber-600 text-white rounded-lg hover:bg-amber-700 focus:outline-none disabled:opacity-50 transition-colors cursor-pointer"
              >
                <Send className="w-4 h-4 ml-0.5" />
              </button>
            </div>
          </div>
        </form>
        <div className="text-center mt-3">
          <p className="text-[10px] text-slate-400">
            AgriGenius provides farming information based on KCC advisory records. It does not replace professional agricultural extension advice.
          </p>
        </div>
      </div>
    </div>
  );
}
