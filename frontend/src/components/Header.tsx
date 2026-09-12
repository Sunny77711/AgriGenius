import { Leaf } from 'lucide-react';

export function Header() {
  return (
    <header className="glass sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-primary-400 to-primary-600 p-2 rounded-lg shadow-sm shadow-primary-500/20">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 tracking-tight">AgriGenius</h1>
              <p className="text-[10px] uppercase tracking-wider text-primary-600 font-bold">Bilingual AI Assistant</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-50 text-primary-700 border border-primary-200">
              Prototype V1
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
