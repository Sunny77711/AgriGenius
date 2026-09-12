import type { SourcePassage } from '../lib/types';
import { MapPin, Tag } from 'lucide-react';
import { motion } from 'framer-motion';

interface SourceCardProps {
  source: SourcePassage;
}

export function SourceCard({ source }: SourceCardProps) {
  const { metadata, similarity, rank, text } = source;
  const matchPercentage = Math.round(similarity * 100);
  const radius = 14;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (matchPercentage / 100) * circumference;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -4, scale: 1.02 }}
      className="glass-card rounded-xl p-4 transition-all group overflow-hidden relative cursor-default"
    >
      <div className="flex justify-between items-start mb-3 relative z-10">
        <div className="flex items-center space-x-3">
          <span className="flex items-center justify-center bg-gradient-to-br from-primary-400 to-primary-600 text-white font-bold text-xs w-6 h-6 rounded-full shadow-sm shadow-primary-500/20">
            {rank}
          </span>
          <div className="flex items-center space-x-2">
            <div className="relative w-8 h-8 flex items-center justify-center">
              <svg className="transform -rotate-90 w-8 h-8">
                <circle cx="16" cy="16" r={radius} stroke="currentColor" strokeWidth="3" fill="transparent" className="text-slate-200" />
                <circle cx="16" cy="16" r={radius} stroke="currentColor" strokeWidth="3" fill="transparent" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} className="text-primary-500 transition-all duration-1000 ease-out" />
              </svg>
              <span className="absolute text-[10px] font-bold text-primary-700">{matchPercentage}</span>
            </div>
          </div>
        </div>
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider bg-white/60 px-2.5 py-1 rounded-full border border-slate-200/50 shadow-sm">KCC Record</span>
      </div>
      
      <p className="text-sm text-slate-700 mb-4 leading-relaxed line-clamp-4 group-hover:line-clamp-none transition-all duration-300 relative z-10">
        "{text}"
      </p>
      
      <div className="flex flex-wrap gap-2 text-[11px] font-medium text-slate-600 mt-auto pt-3 border-t border-slate-200/60 relative z-10">
        {metadata.Crop && (
          <div className="flex items-center bg-primary-50/80 px-2.5 py-1.5 rounded-md text-primary-700 border border-primary-100">
            <LeafIcon className="w-3 h-3 mr-1.5" />
            {metadata.Crop}
          </div>
        )}
        {(metadata.DistrictName || metadata.StateName) && (
          <div className="flex items-center bg-blue-50/80 px-2.5 py-1.5 rounded-md text-blue-700 border border-blue-100">
            <MapPin className="w-3 h-3 mr-1.5" />
            {[metadata.DistrictName, metadata.StateName].filter(Boolean).join(', ')}
          </div>
        )}
        {metadata.QueryType && (
          <div className="flex items-center bg-amber-50/80 px-2.5 py-1.5 rounded-md text-amber-700 border border-amber-100">
            <Tag className="w-3 h-3 mr-1.5" />
            {metadata.QueryType}
          </div>
        )}
      </div>
      
      <div className="absolute inset-0 bg-gradient-to-tr from-primary-50/0 to-primary-100/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </motion.div>
  );
}

function LeafIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
    </svg>
  );
}
