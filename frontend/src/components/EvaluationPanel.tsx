import { BarChart3 } from 'lucide-react';

export function EvaluationPanel() {
  return (
    <div className="glass-card rounded-xl p-5 hover:shadow-lg transition-shadow duration-300">
      <h3 className="text-sm font-semibold text-slate-800 mb-4 flex items-center">
        <BarChart3 className="w-4 h-4 mr-2 text-primary-600" />
        Demo Evaluation
      </h3>
      
      <div className="space-y-4">
        <div>
          <div className="flex justify-between items-end mb-1">
            <span className="text-xs text-slate-500">Crop Hit Rate @ 5</span>
            <span className="text-sm font-medium text-slate-700">6/6 (100%)</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5">
            <div className="bg-primary-500 h-1.5 rounded-full" style={{ width: '100%' }}></div>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between items-end mb-1">
            <span className="text-xs text-slate-500">Category Hit Rate @ 5</span>
            <span className="text-sm font-medium text-slate-700">6/6 (100%)</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5">
            <div className="bg-primary-500 h-1.5 rounded-full" style={{ width: '100%' }}></div>
          </div>
        </div>
        
        <p className="text-xs text-slate-400 mt-2 italic">
          * Based on demo set. Full benchmark evaluation planned.
        </p>
      </div>
    </div>
  );
}
