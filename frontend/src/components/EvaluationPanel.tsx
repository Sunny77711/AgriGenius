
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

export function EvaluationPanel() {
  const navigate = useNavigate();
  return (
    <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300 flex-1 flex flex-col justify-between">
      <div className="space-y-7">
        <div>
          <div className="flex justify-between items-end mb-2">
            <span className="text-xs font-semibold text-slate-500 dark:text-neutral-400 uppercase tracking-wider">Crop Hit Rate @ 5</span>
            <span className="text-xs font-bold text-slate-800 dark:text-neutral-200 bg-white/60 dark:bg-neutral-800/60 px-2 py-0.5 rounded shadow-sm">Pending</span>
          </div>
          <div className="w-full bg-slate-200/50 dark:bg-neutral-800/50 rounded-full h-2 shadow-inner overflow-hidden relative">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: '0%' }}
              transition={{ duration: 1, delay: 0.5, type: 'spring' }}
              className="bg-gradient-to-r from-primary-400 to-primary-600 h-2 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]" 
            />
          </div>
        </div>
        
        <div className="group">
          <div className="flex justify-between items-end mb-2">
            <span className="text-xs font-semibold text-slate-500 dark:text-neutral-400 uppercase tracking-wider">Category Hit Rate @ 5</span>
            <span className="text-xs font-bold text-slate-800 dark:text-neutral-200 bg-white/60 dark:bg-neutral-800/60 px-2 py-0.5 rounded shadow-sm">Pending</span>
          </div>
          <div className="w-full bg-slate-200/50 dark:bg-neutral-800/50 rounded-full h-2 shadow-inner overflow-hidden relative">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: '0%' }}
              transition={{ duration: 1, delay: 0.7, type: 'spring' }}
              className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]" 
            />
          </div>
        </div>
      </div>
      <p className="text-xs text-slate-400 dark:text-neutral-500 mt-6 pt-4 border-t border-slate-100 dark:border-neutral-800 italic">
        Retrieval hit rates are pending. Use LLM QA to compare three generators and review Gemini claim-level support estimates against KCC evidence.
      </p>
      <button type="button" onClick={() => navigate('/evaluation')} className="mt-4 rounded-xl bg-blue-700 hover:bg-blue-600 px-3 py-2 text-xs font-bold text-white transition-colors">
        Open LLM testing
      </button>
    </div>
  );
}
