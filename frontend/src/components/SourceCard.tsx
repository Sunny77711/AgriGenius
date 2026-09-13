import type { SourcePassage } from '../lib/types';
import { MapPin, Tag, FileText } from 'lucide-react';
import { motion } from 'framer-motion';

interface SourceCardProps {
  source: SourcePassage;
}

export function SourceCard({ source }: SourceCardProps) {
  const { metadata, similarity, rank, text } = source;
  const matchPercentage = Math.round(similarity * 100);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2 text-xs font-medium text-slate-500 dark:text-neutral-400">
          <FileText className="w-3 h-3 text-slate-400 dark:text-neutral-500" />
          <span>Source {rank}</span>
        </div>
        <span className="text-[10px] font-bold text-slate-400 dark:text-neutral-500 uppercase bg-slate-100 dark:bg-neutral-800 px-1.5 py-0.5 rounded">
          {matchPercentage}% Match
        </span>
      </div>
      
      <p className="text-xs text-slate-700 dark:text-neutral-300 leading-relaxed mb-3 line-clamp-4 hover:line-clamp-none transition-all cursor-default">
        "{text}"
      </p>
      
      <div className="flex flex-col gap-1.5 text-[10px] text-slate-500 dark:text-neutral-400 pt-2 border-t border-slate-100 dark:border-neutral-800">
        <span className="flex items-center">
          <Tag className="w-3 h-3 mr-1.5 text-slate-400 dark:text-neutral-500 shrink-0" />
          <span className="truncate">{metadata.Crop || 'Unknown Crop'} &bull; {metadata.QueryType || 'General'}</span>
        </span>
        <span className="flex items-center">
          <MapPin className="w-3 h-3 mr-1.5 text-slate-400 dark:text-neutral-500 shrink-0" />
          <span className="truncate">{[metadata.DistrictName, metadata.StateName].filter(Boolean).join(', ')}</span>
        </span>
      </div>
    </motion.div>
  );
}

