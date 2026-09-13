import { useState, useRef, useEffect } from 'react';
import type { Message } from '../lib/types';
import { ChatMessage } from './ChatMessage';
import { QueryInput } from './QueryInput';
import { EmptyState } from './EmptyState';
import { AnimatePresence, motion } from 'framer-motion';
import { Leaf, Plus, MessageSquare, FileText, X, Menu } from 'lucide-react';
import { SourceCard } from './SourceCard';
import { Link } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';

export function ChatShell() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

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
    <div className="flex w-full h-full bg-slate-50 dark:bg-black overflow-hidden font-sans relative text-slate-900 dark:text-white">
      {/* MOBILE OVERLAY */}
      {isSidebarOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-20" 
          onClick={() => setIsSidebarOpen(false)} 
        />
      )}

      {/* LEFT SIDEBAR - Dark Theme */}
      <div className={`absolute md:relative z-30 w-64 bg-primary-900 dark:bg-black text-slate-300 flex flex-col h-full shrink-0 border-r border-primary-900 dark:border-neutral-800 transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'} transition-transform overflow-hidden`}>
        <div className="p-4 flex items-center space-x-3 mb-4">
          <div className="bg-primary-600 p-2 rounded-lg">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">AgriGenius</h1>
            <p className="text-[10px] uppercase tracking-wider text-primary-400 font-bold">RAG Assistant</p>
          </div>
        </div>
        
        <div className="px-4 mb-6">
          <motion.button 
            whileTap={{ scale: 0.95 }}
            onClick={() => setMessages([])}
            className="w-full bg-primary-800 dark:bg-neutral-900 hover:bg-primary-700 dark:hover:bg-neutral-800 text-white rounded-lg py-2.5 px-4 flex items-center justify-center font-medium transition-colors border border-primary-700 dark:border-neutral-800"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Query
          </motion.button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 pb-4">
          <div className="text-xs font-semibold text-primary-400/70 dark:text-neutral-400 uppercase tracking-wider mb-3">Today</div>
          {messages.length > 0 ? (
            <div className="flex items-center space-x-3 text-sm text-white bg-primary-800/80 dark:bg-neutral-900 p-2.5 rounded-lg cursor-pointer border border-primary-700 dark:border-neutral-800">
              <MessageSquare className="w-4 h-4 shrink-0" />
              <span className="truncate">{messages[0].content}</span>
            </div>
          ) : (
            <div className="text-sm text-primary-300/60 dark:text-neutral-500 italic">No queries yet</div>
          )}
        </div>
        <div className="p-4 border-t border-primary-900 dark:border-neutral-800">
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.95 }}>
            <Link to="/about" className="text-sm text-primary-200 dark:text-neutral-400 hover:text-white transition-colors">
              About & Status
            </Link>
          </motion.div>
        </div>
      </div>

      {/* CENTER CHAT AREA */}
      <div className={`flex-1 flex flex-col h-full relative shadow-[0_0_40px_rgba(0,0,0,0.05)] z-10 border-r border-slate-200 dark:border-neutral-800 w-full min-w-0 bg-transparent`}>
        
        {/* Top Bar for Sources Toggle */}
        <div className="absolute top-4 left-4 right-4 z-20 flex justify-between items-center pointer-events-none">
          {/* Mobile Menu Button */}
          <motion.button 
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsSidebarOpen(true)}
            className="md:hidden pointer-events-auto flex items-center justify-center p-2 bg-white/80 backdrop-blur-sm border border-slate-200 text-slate-700 rounded-lg shadow-sm hover:bg-white"
          >
            <Menu className="w-5 h-5" />
          </motion.button>
          
          <div className="flex-1"></div>

          <div className="flex items-center space-x-3">
            <div className="pointer-events-auto">
              <ThemeToggle />
            </div>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowSources(!showSources)}
              className={`pointer-events-auto flex items-center space-x-2 px-3 py-1.5 rounded-lg shadow-sm transition-colors border ${showSources ? 'bg-primary-50 dark:bg-neutral-800 border-primary-200 dark:border-neutral-700 text-primary-700 dark:text-primary-400' : 'bg-white/80 dark:bg-neutral-900 backdrop-blur-sm border-slate-200 dark:border-neutral-800 text-slate-700 dark:text-neutral-300 hover:bg-white dark:hover:bg-neutral-800'}`}
            >
            <FileText className="w-4 h-4" />
            <span className="text-sm font-medium">Sources</span>
            {activeSources.length > 0 && (
              <span className={`text-xs font-bold px-1.5 py-0.5 rounded-full ${showSources ? 'bg-primary-200 text-primary-800' : 'bg-slate-100 text-slate-600'}`}>
                {activeSources.length}
              </span>
            )}
            </motion.button>
          </div>
        </div>

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
      <AnimatePresence>
        {showSources && (
          <motion.div 
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute md:relative right-0 z-30 flex flex-col h-full w-[320px] max-w-[85vw] shrink-0 shadow-xl border-l border-slate-200 dark:border-neutral-800 overflow-hidden bg-slate-50 dark:bg-black"
          >
            <motion.button 
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowSources(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 dark:text-neutral-400 dark:hover:text-neutral-200 z-10"
            >
              <X className="w-4 h-4" />
            </motion.button>
            <div className="p-4 border-b border-slate-200 dark:border-neutral-800 bg-transparent pr-12 shrink-0">
              <h2 className="text-sm font-semibold text-slate-800 dark:text-neutral-100 flex items-center">
                Sources
                <span className="ml-2 text-[10px] uppercase tracking-wider text-slate-400 dark:text-neutral-500 font-bold bg-slate-100 dark:bg-neutral-900 border dark:border-neutral-800 px-2 py-0.5 rounded-full">Verified</span>
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4 min-w-[320px]">
          {activeSources.length > 0 ? (
            activeSources.map((source, idx) => (
              <SourceCard key={idx} source={source} />
            ))
          ) : (
            <div className="text-sm text-slate-500 dark:text-neutral-500 text-center mt-10">
              Sources will appear here when available.
            </div>
          )}
        </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
