import type { Message } from '../lib/types';
import { User, Sparkles, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <motion.div 
      layout
      initial={{ opacity: 0, scale: 0.96, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.4, type: "spring", bounce: 0.2 }}
      className={`py-4 px-4 flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex gap-4 max-w-2xl ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className="flex-shrink-0 mt-1">
          {isUser ? (
            <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center shadow-sm">
              <User className="w-4 h-4 text-white" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shadow-sm">
              <Sparkles className="w-4 h-4 text-primary-600" />
            </div>
          )}
        </div>
        
        <div className={`flex flex-col space-y-4 ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-5 py-3.5 rounded-2xl shadow-sm ${
            isUser 
              ? 'bg-slate-800 text-white rounded-tr-sm' 
              : 'bg-slate-50 border border-slate-100 rounded-tl-sm'
          }`}>
            <p className={`leading-relaxed whitespace-pre-wrap ${isUser ? 'text-white' : 'text-slate-800'}`}>
              {message.content}
            </p>
          </div>
          
          {message.responseDetails && !message.responseDetails.grounded && (
            <div className="flex items-center text-amber-700 bg-amber-50 px-4 py-3 rounded-lg border border-amber-200 max-w-sm">
              <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0" />
              <p className="text-sm">Insufficient evidence in KCC database. Answer may not be fully grounded.</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
