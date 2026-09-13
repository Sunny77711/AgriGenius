import { Leaf } from 'lucide-react';
import { ExampleQueries } from './ExampleQueries';

interface EmptyStateProps {
  onSelectQuery: (query: string) => void;
}

export function EmptyState({ onSelectQuery }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto text-center px-4">
      <div className="bg-primary-50 dark:bg-primary-900/30 w-20 h-20 rounded-full flex items-center justify-center mb-6">
        <Leaf className="w-10 h-10 text-primary-600 dark:text-primary-400" />
      </div>
      <h2 className="text-2xl font-semibold text-slate-800 dark:text-white mb-3">Welcome to AgriGenius</h2>
      <p className="text-slate-500 dark:text-neutral-400 mb-8 max-w-lg leading-relaxed">
        Ask any farming-related question in English or Hindi. The assistant retrieves authentic advisory records from the Kisan Call Centre database to provide accurate, grounded answers.
      </p>
      
      <ExampleQueries onSelectQuery={onSelectQuery} />
    </div>
  );
}
