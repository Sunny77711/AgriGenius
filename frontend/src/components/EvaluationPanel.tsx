
import { motion } from 'framer-motion';

export function EvaluationPanel() {
  return (
    <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300 flex-1 flex flex-col justify-between">
      <div className="space-y-7">
        <div>
          <div className="flex justify-between items-end mb-2">
            <span className="text-xs font-semibold text-slate-500 dark:text-neutral-400 uppercase tracking-wider">Crop Hit Rate @ 5</span>
            <span className="text-xs font-bold text-slate-800 dark:text-neutral-200 bg-white/60 dark:bg-neutral-800/60 px-2 py-0.5 rounded shadow-sm">6/6 (100%)</span>
          </div>
          <div className="w-full bg-slate-200/50 dark:bg-neutral-800/50 rounded-full h-2 shadow-inner overflow-hidden relative">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 1, delay: 0.5, type: 'spring' }}
              className="bg-gradient-to-r from-primary-400 to-primary-600 h-2 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]" 
            />
          </div>
        </div>
        
        <div className="group">
          <div className="flex justify-between items-end mb-2">
            <span className="text-xs font-semibold text-slate-500 dark:text-neutral-400 uppercase tracking-wider">Category Hit Rate @ 5</span>
            <span className="text-xs font-bold text-slate-800 dark:text-neutral-200 bg-white/60 dark:bg-neutral-800/60 px-2 py-0.5 rounded shadow-sm">6/6 (100%)</span>
          </div>
          <div className="w-full bg-slate-200/50 dark:bg-neutral-800/50 rounded-full h-2 shadow-inner overflow-hidden relative">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 1, delay: 0.7, type: 'spring' }}
              className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]" 
            />
          </div>
        </div>
      </div>
      <p className="text-xs text-slate-400 dark:text-neutral-500 mt-6 pt-4 border-t border-slate-100 dark:border-neutral-800 italic">
        * Based on demo set. Full benchmark evaluation planned.
      </p>
    </div>
  );
}
