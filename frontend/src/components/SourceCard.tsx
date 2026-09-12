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
      className="bg-white border border-slate-200 rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2 text-xs font-medium text-slate-500">
          <FileText className="w-3 h-3 text-slate-400" />
          <span>Source {rank}</span>
        </div>
        <span className="text-[10px] font-bold text-slate-400 uppercase bg-slate-100 px-1.5 py-0.5 rounded">
          {matchPercentage}% Match
        </span>
      </div>
      
      <p className="text-xs text-slate-700 leading-relaxed mb-3 line-clamp-4 hover:line-clamp-none transition-all cursor-default">
        "{text}"
      </p>
      
      <div className="flex flex-col gap-1.5 text-[10px] text-slate-500 pt-2 border-t border-slate-100">
        <span className="flex items-center">
          <Tag className="w-3 h-3 mr-1.5 text-slate-400 shrink-0" />
          <span className="truncate">{metadata.Crop || 'Unknown Crop'} &bull; {metadata.QueryType || 'General'}</span>
        </span>
        <span className="flex items-center">
          <MapPin className="w-3 h-3 mr-1.5 text-slate-400 shrink-0" />
          <span className="truncate">{[metadata.DistrictName, metadata.StateName].filter(Boolean).join(', ')}</span>
        </span>
      </div>
    </motion.div>
  );
}

