import { Search } from 'lucide-react';
import { motion } from 'framer-motion';

interface ExampleQueriesProps {
  onSelectQuery: (query: string) => void;
}

export function ExampleQueries({ onSelectQuery }: ExampleQueriesProps) {
  const queries = [
    "गेहूं की फसल में सिंचाई कब करनी चाहिए?",
    "How do I control pests in mango trees?",
    "What is the seed rate for groundnut crop?",
    "धान की फसल में खरपतवार को कैसे नियंत्रित करें?"
  ];

  return (
    <div className="w-full max-w-2xl mx-auto mt-8">
      <p className="text-sm text-slate-500 mb-3 text-center">Try asking about your crops:</p>
      <div className="flex flex-wrap gap-2 justify-center">
        {queries.map((query, idx) => (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.95 }}
            key={idx}
            onClick={() => setTimeout(() => onSelectQuery(query), 200)}
            className="flex items-center text-sm bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 text-slate-700 dark:text-neutral-300 px-4 py-2 rounded-full hover:bg-primary-50 dark:hover:bg-neutral-800 hover:border-primary-200 dark:hover:border-neutral-700 hover:text-primary-700 dark:hover:text-white transition-colors shadow-sm"
          >
            <Search className="w-3.5 h-3.5 mr-2 opacity-50" />
            {query}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
