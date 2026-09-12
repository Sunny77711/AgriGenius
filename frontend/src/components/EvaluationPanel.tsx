import { BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';

export function EvaluationPanel() {
  return (
    <div className="glass-card rounded-xl p-5 hover:shadow-lg transition-shadow duration-300">
      <h3 className="text-sm font-semibold text-slate-800 mb-4 flex items-center">
        <BarChart3 className="w-4 h-4 mr-2 text-primary-600" />
        Demo Evaluation
      </h3>
      
      <div className="space-y-4">
        <div>
          <div className="flex justify-between items-end mb-2">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Crop Hit Rate @ 5</span>
            <span className="text-xs font-bold text-slate-800 bg-white/60 px-2 py-0.5 rounded shadow-sm">6/6 (100%)</span>
          </div>
          <div className="w-full bg-slate-200/50 rounded-full h-2 shadow-inner overflow-hidden relative">
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
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Category Hit Rate @ 5</span>
            <span className="text-xs font-bold text-slate-800 bg-white/60 px-2 py-0.5 rounded shadow-sm">6/6 (100%)</span>
          </div>
          <div className="w-full bg-slate-200/50 rounded-full h-2 shadow-inner overflow-hidden relative">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 1, delay: 0.7, type: 'spring' }}
              className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]" 
            />
          </div>
        </div>
        
        <p className="text-xs text-slate-400 mt-2 italic">
          * Based on demo set. Full benchmark evaluation planned.
        </p>
      </div>
    </div>
  );
}
