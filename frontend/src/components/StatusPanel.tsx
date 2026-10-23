import { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { checkHealth } from '../lib/api';
import type { HealthResponse } from '../lib/types';

export function StatusPanel() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const backendConnected = health?.status === 'ok';

  useEffect(() => {
    checkHealth().then(setHealth).catch(console.error);
  }, []);

  return (
    <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300 flex-1 flex flex-col justify-between">
      <div className="space-y-5">
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500 dark:text-neutral-400">Corpus Size</span>
          <span className="font-medium text-slate-700 dark:text-neutral-200">
            {health?.collection_count?.toLocaleString() || 'Unavailable'} KCC records
          </span>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500 dark:text-neutral-400">Retrieval Model</span>
          <span className="font-medium text-slate-700 dark:text-neutral-200 text-right max-w-[150px] truncate" title={health?.model}>
            {health?.model || 'Unavailable'}
          </span>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500 dark:text-neutral-400">Reranker</span>
          <span className="font-medium text-slate-700 dark:text-neutral-200 text-right max-w-[150px] truncate" title={health?.reranker}>
            {health?.reranker || 'Unavailable'}
          </span>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500 dark:text-neutral-400">Vector DB</span>
          <span className="font-medium text-slate-700 dark:text-neutral-200">ChromaDB</span>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex justify-between items-center gap-2">
            <span className="text-slate-500 dark:text-neutral-400">Primary chat model</span>
            <span className="font-medium text-slate-700 dark:text-neutral-200 text-right max-w-[170px] truncate" title={health?.llm_models?.qwen || health?.llm_model}>
              {health?.llm_models?.qwen || health?.llm_model || 'Unavailable'}
            </span>
          </div>
          <div className="flex justify-between items-center gap-2">
            <span className="text-slate-500 dark:text-neutral-400">Fallback model</span>
            <span className="font-medium text-slate-700 dark:text-neutral-200 text-right max-w-[170px] truncate" title={health?.llm_models?.groq}>
              {health?.llm_models?.groq || 'Unavailable'}
            </span>
          </div>
          <div className="flex justify-between items-center gap-2">
            <span className="text-slate-500 dark:text-neutral-400">Comparison model</span>
            <span className="font-medium text-slate-700 dark:text-neutral-200 text-right max-w-[170px] truncate" title={health?.llm_models?.groq_120b}>
              {health?.llm_models?.groq_120b || 'Unavailable'}
            </span>
          </div>
          <div className="flex justify-between items-center gap-2">
            <span className="text-slate-500 dark:text-neutral-400">Evaluation judge</span>
            <span className="font-medium text-slate-700 dark:text-neutral-200 text-right max-w-[170px] truncate" title={health?.evaluation_judge}>
              {health?.evaluation_judge || 'Unavailable'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="mt-5 pt-4 border-t border-slate-100 dark:border-neutral-800">
        <div className="flex items-center text-xs text-primary-700 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-3 py-2 rounded-lg">
          <ShieldCheck className="w-4 h-4 mr-2" />
          <span>{backendConnected ? 'Live KCC backend connected' : 'Backend unavailable; no sample answers'}</span>
        </div>
      </div>
    </div>
  );
}
