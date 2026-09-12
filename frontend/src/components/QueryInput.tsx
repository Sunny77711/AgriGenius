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
    <div className="glass border-t border-white/40 p-4 sticky bottom-0">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="relative group">
          <div className="overflow-hidden rounded-2xl border-2 border-transparent bg-white shadow-sm focus-within:border-primary-500 focus-within:shadow-md transition-all duration-300 bg-clip-padding relative">
            <textarea
              rows={2}
              className="block w-full resize-none border-0 bg-transparent py-4 pl-4 pr-32 text-slate-900 placeholder:text-slate-400 focus:ring-0 sm:text-sm sm:leading-6"
              placeholder="Ask a farming question in English or Hindi..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              disabled={disabled}
            />
            
            <div className="absolute inset-y-0 right-0 flex items-center py-2 pr-2">
              <div className="flex items-center space-x-2">
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value as any)}
                  className="h-8 text-xs bg-slate-50 border border-slate-200 rounded-md text-slate-600 focus:ring-primary-500 focus:border-primary-500"
                  disabled={disabled}
                >
                  <option value="auto">Auto</option>
                  <option value="en">English</option>
                  <option value="hi">हिंदी</option>
                </select>
                
                <button
                  type="button"
                  title="Voice input coming soon"
                  className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors cursor-not-allowed"
                >
                  <Mic className="w-5 h-5" />
                </button>
                
                <button
                  type="submit"
                  disabled={disabled || !query.trim()}
                  className="inline-flex items-center justify-center p-2 bg-primary-600 text-white rounded-full hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="w-4 h-4 ml-0.5" />
                </button>
              </div>
            </div>
          </div>
          <div className="mt-2 flex justify-between items-center text-xs text-slate-400 px-2">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span>English-Hindi multilingual ready</span>
          </div>
        </form>
      </div>
    </div>
  );
}
