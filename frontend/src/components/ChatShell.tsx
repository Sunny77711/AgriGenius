import { useState, useRef, useEffect } from 'react';
import type { Message } from '../lib/types';
import { ChatMessage } from './ChatMessage';
import { QueryInput } from './QueryInput';
import { EmptyState } from './EmptyState';
import { AnimatePresence, motion } from 'framer-motion';
import { Leaf, Plus, MessageSquare } from 'lucide-react';
import { SourceCard } from './SourceCard';
import { Link } from 'react-router-dom';

export function ChatShell() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const activeMessageWithSources = [...messages].reverse().find(m => m.responseDetails?.sources && m.responseDetails.sources.length > 0);
  const activeSources = activeMessageWithSources?.responseDetails?.sources || [];

  const handleSendMessage = async (query: string, language: "auto" | "en" | "hi") => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
    };
    
    const assistantId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
    };
    
    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);

    try {
      const { streamChatMessage } = await import('../lib/api');
      
      await streamChatMessage(
        { query, language, top_k: 5 },
        (chunk) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantId 
                ? { ...msg, content: msg.content + chunk } 
                : msg
            )
          );
        },
        (sources) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantId 
                ? { ...msg, responseDetails: { ...msg.responseDetails, sources, grounded: true, query, answer: msg.content, source_count: sources.length, collection_count: 0 } as any } 
                : msg
            )
          );
        },
        (error) => {
          console.error('Failed to send message:', error);
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantId 
                ? { ...msg, content: 'Sorry, I encountered an error while trying to process your request. Please try again.' } 
                : msg
            )
          );
          setIsLoading(false);
        },
        () => {
          setIsLoading(false);
        }
      );
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => 
        prev.map(msg => 
          msg.id === assistantId 
            ? { ...msg, content: 'Sorry, I encountered an error while trying to process your request. Please try again.' } 
            : msg
        )
      );
      setIsLoading(false);
    }
  };

  return (
    <div className="flex w-full h-full bg-slate-50 overflow-hidden font-sans">
      {/* LEFT SIDEBAR - Dark Theme */}
      <div className="w-64 bg-slate-900 text-slate-300 flex flex-col h-full shrink-0 border-r border-slate-800">
        <div className="p-4 flex items-center space-x-3 mb-4">
          <div className="bg-primary-600 p-2 rounded-lg">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">AgriGenius</h1>
            <p className="text-[10px] uppercase tracking-wider text-primary-400 font-bold">Fiduciary Lens Ref</p>
          </div>
        </div>
        
        <div className="px-4 mb-6">
          <button onClick={() => setMessages([])} className="w-full bg-slate-800 hover:bg-slate-700 text-white rounded-lg py-2.5 px-4 flex items-center justify-center font-medium transition-colors border border-slate-700">
            <Plus className="w-4 h-4 mr-2" />
            New Query
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 pb-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Today</div>
          {messages.length > 0 ? (
            <div className="flex items-center space-x-3 text-sm text-slate-300 bg-slate-800/50 p-2.5 rounded-lg cursor-pointer border border-slate-700">
              <MessageSquare className="w-4 h-4 shrink-0" />
              <span className="truncate">{messages[0].content}</span>
            </div>
          ) : (
            <div className="text-sm text-slate-600 italic">No queries yet</div>
          )}
        </div>
        
        <div className="p-4 border-t border-slate-800">
          <Link to="/about" className="text-sm hover:text-white transition-colors">
            About & System Status
          </Link>
        </div>
      </div>

      {/* CENTER CHAT AREA */}
      <div className="flex-1 flex flex-col h-full bg-white relative shadow-[0_0_40px_rgba(0,0,0,0.05)] z-10 border-r border-slate-200">
        <div className="flex-1 overflow-y-auto relative scrollbar-hide">
          {messages.length === 0 ? (
            <EmptyState onSelectQuery={(q) => handleSendMessage(q, 'auto')} />
          ) : (
            <div className="pb-36 pt-8 max-w-4xl mx-auto w-full px-4">
              <AnimatePresence mode="popLayout">
                {messages.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
                {isLoading && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="py-4 px-4 flex w-full justify-start"
                  >
                    <div className="flex gap-4 max-w-2xl flex-row">
                      <div className="flex flex-col space-y-4 items-start">
                        <div className="px-5 py-3.5 rounded-2xl shadow-sm bg-slate-50 border border-slate-100 rounded-tl-sm w-24">
                          <div className="flex space-x-2 items-center h-5">
                            <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div ref={messagesEndRef} className="h-4" />
            </div>
          )}
        </div>
        <QueryInput onSend={handleSendMessage} disabled={isLoading} />
      </div>

      {/* RIGHT SIDEBAR - Sources */}
      <div className="w-80 bg-slate-50 flex flex-col h-full shrink-0">
        <div className="p-4 border-b border-slate-200 bg-white">
          <h2 className="text-sm font-semibold text-slate-800 flex items-center">
            Sources
            <span className="ml-2 text-[10px] uppercase tracking-wider text-slate-400 font-bold bg-slate-100 px-2 py-0.5 rounded-full">Verified</span>
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {activeSources.length > 0 ? (
            activeSources.map((source, idx) => (
              <SourceCard key={idx} source={source} />
            ))
          ) : (
            <div className="text-sm text-slate-500 text-center mt-10">
              Sources will appear here when available.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
