import { StatusPanel } from '../components/StatusPanel';
import { EvaluationPanel } from '../components/EvaluationPanel';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans">
      <div className="max-w-4xl mx-auto">
        <Link to="/chat" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-primary-600 mb-8 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Chat
        </Link>
        
        <div className="mb-12">
          <h1 className="text-3xl font-bold text-slate-900 mb-4">About AgriGenius</h1>
          <p className="text-lg text-slate-600 leading-relaxed">
            AgriGenius is a bilingual AI farming assistant powered by a Retrieval-Augmented Generation (RAG) architecture. 
            It references real, vetted Kisan Call Centre advisory records to provide grounded answers to Indian farmers in English and Hindi.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-xl font-semibold text-slate-800 mb-4">System Status</h2>
            <StatusPanel />
          </div>
          
          <div>
            <h2 className="text-xl font-semibold text-slate-800 mb-4">Evaluation Metrics</h2>
            <EvaluationPanel />
          </div>
        </div>
      </div>
    </div>
  );
}
