import { Search } from 'lucide-react';

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
          <button
            key={idx}
            onClick={() => onSelectQuery(query)}
            className="flex items-center text-sm bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-full hover:bg-primary-50 hover:border-primary-200 hover:text-primary-700 transition-colors shadow-sm"
          >
            <Search className="w-3.5 h-3.5 mr-2 opacity-50" />
            {query}
          </button>
        ))}
      </div>
    </div>
  );
}
