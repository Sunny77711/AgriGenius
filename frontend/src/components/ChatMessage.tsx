import type { Message } from '../lib/types';
import { User, Sparkles, AlertTriangle } from 'lucide-react';
import { SourceCard } from './SourceCard';
import { motion } from 'framer-motion';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`py-8 ${isUser ? 'bg-transparent' : 'glass-panel mx-4 rounded-2xl my-2'}`}
    >
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 flex gap-6">
        <div className="flex-shrink-0 mt-1">
          {isUser ? (
            <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
              <User className="w-5 h-5 text-slate-600" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
          )}
        </div>
        
        <div className="flex-1 space-y-4">
          <div className="prose prose-slate max-w-none">
            <p className="text-slate-800 leading-relaxed whitespace-pre-wrap">{message.content}</p>
          </div>
          
          {message.responseDetails && (
            <div className="mt-6 space-y-4">
              {!message.responseDetails.grounded && (
                <div className="flex items-center text-amber-700 bg-amber-50 px-4 py-3 rounded-lg border border-amber-200">
                  <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0" />
                  <p className="text-sm">Insufficient evidence in KCC database. Answer may not be fully grounded in advisory records.</p>
                </div>
              )}
              
              {message.responseDetails.sources.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wider">Sources Retrieved</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {message.responseDetails.sources.map((source, idx) => (
                      <SourceCard key={idx} source={source} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
