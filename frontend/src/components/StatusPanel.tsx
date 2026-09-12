import { useEffect, useState } from 'react';
import { Database, ShieldCheck } from 'lucide-react';
import { checkHealth } from '../lib/api';
import type { HealthResponse } from '../lib/types';

export function StatusPanel() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    checkHealth().then(setHealth).catch(console.error);
  }, []);

  return (
    <div className="glass-card rounded-xl p-5 mb-4 hover:shadow-lg transition-shadow duration-300">
      <h3 className="text-sm font-semibold text-slate-800 mb-4 flex items-center">
        <Database className="w-4 h-4 mr-2 text-primary-600" />
        System Status
      </h3>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500">Corpus Size</span>
          <span className="font-medium text-slate-700">
            {health ? health.collection_count.toLocaleString() : '---'} KCC records
          </span>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500">Retrieval Model</span>
          <span className="font-medium text-slate-700 text-right max-w-[150px] truncate" title={health?.model}>
            {health?.model || '---'}
          </span>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500">Vector DB</span>
          <span className="font-medium text-slate-700">ChromaDB</span>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-500">LLM Engine</span>
          <span className="font-medium text-slate-700">Gemini</span>
        </div>
      </div>
      
      <div className="mt-5 pt-4 border-t border-slate-100">
        <div className="flex items-center text-xs text-primary-700 bg-primary-50 px-3 py-2 rounded-lg">
          <ShieldCheck className="w-4 h-4 mr-2" />
          <span>Responses grounded in KCC data</span>
        </div>
      </div>
    </div>
  );
}
