import type { SourcePassage } from '../lib/types';
import { MapPin, Tag } from 'lucide-react';

interface SourceCardProps {
  source: SourcePassage;
}

export function SourceCard({ source }: SourceCardProps) {
  const { metadata, similarity, rank, text } = source;
  const matchPercentage = Math.round(similarity * 100);

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center space-x-2">
          <span className="flex items-center justify-center bg-primary-100 text-primary-700 font-bold text-xs w-5 h-5 rounded-full">
            {rank}
          </span>
          <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded">
            {matchPercentage}% Match
          </span>
        </div>
        <span className="text-xs font-medium text-slate-400">KCC Record</span>
      </div>
      
      <p className="text-sm text-slate-700 mb-3 leading-relaxed">"{text}"</p>
      
      <div className="flex flex-wrap gap-2 text-xs text-slate-600 mt-auto pt-3 border-t border-slate-100">
        {metadata.Crop && (
          <div className="flex items-center bg-green-50 px-2 py-1 rounded text-green-700">
            <LeafIcon className="w-3 h-3 mr-1" />
            {metadata.Crop}
          </div>
        )}
        {(metadata.DistrictName || metadata.StateName) && (
          <div className="flex items-center bg-blue-50 px-2 py-1 rounded text-blue-700">
            <MapPin className="w-3 h-3 mr-1" />
            {[metadata.DistrictName, metadata.StateName].filter(Boolean).join(', ')}
          </div>
        )}
        {metadata.QueryType && (
          <div className="flex items-center bg-orange-50 px-2 py-1 rounded text-orange-700">
            <Tag className="w-3 h-3 mr-1" />
            {metadata.QueryType}
          </div>
        )}
      </div>
    </div>
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
