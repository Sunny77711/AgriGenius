import { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { checkHealth } from '../lib/api';
import type { HealthResponse } from '../lib/types';

export function StatusPanel() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    checkHealth().then(setHealth).catch(console.error);
  }, []);

  return (
    <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300 flex-1 flex flex-col justify-between">
      <div className="space-y-5">
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500 dark:text-neutral-400">Corpus Size</span>
          <span className="font-medium text-slate-700 dark:text-neutral-200">
            {health ? health.collection_count.toLocaleString() : '---'} KCC records
          </span>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500 dark:text-neutral-400">Retrieval Model</span>
          <span className="font-medium text-slate-700 dark:text-neutral-200 text-right max-w-[150px] truncate" title={health?.model}>
            {health?.model || '---'}
          </span>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500 dark:text-neutral-400">Vector DB</span>
          <span className="font-medium text-slate-700 dark:text-neutral-200">ChromaDB</span>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500 dark:text-neutral-400">LLM Engine</span>
          <span className="font-medium text-slate-700 dark:text-neutral-200">Gemini</span>
        </div>
      </div>
      
      <div className="mt-5 pt-4 border-t border-slate-100 dark:border-neutral-800">
        <div className="flex items-center text-xs text-primary-700 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-3 py-2 rounded-lg">
          <ShieldCheck className="w-4 h-4 mr-2" />
          <span>Responses grounded in KCC data</span>
        </div>
      </div>
    </div>
  );
}
