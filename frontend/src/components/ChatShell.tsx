import { useState, useRef, useEffect } from 'react';
import type { Message } from '../lib/types';
import { sendChatMessage } from '../lib/api';
import { ChatMessage } from './ChatMessage';
import { QueryInput } from './QueryInput';
import { EmptyState } from './EmptyState';
import { AnimatePresence, motion } from 'framer-motion';

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
    <div className="flex flex-col h-full bg-transparent relative">
      <div className="noise-overlay" />
      <div className="flex-1 overflow-y-auto relative z-10 scrollbar-hide">
        {messages.length === 0 ? (
          <EmptyState onSelectQuery={(q) => handleSendMessage(q, 'auto')} />
        ) : (
          <div className="pb-36 pt-8">
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
                  <div className="flex gap-4 max-w-4xl flex-row">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shadow-sm">
                        <div className="w-3 h-3 bg-primary-500 rounded-full animate-ping"></div>
                      </div>
                    </div>
                    <div className="flex flex-col space-y-4 items-start">
                      <div className="px-5 py-3.5 rounded-2xl shadow-sm glass rounded-tl-sm w-48">
                        <div className="flex space-x-2 items-center h-5">
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
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
  );
}
