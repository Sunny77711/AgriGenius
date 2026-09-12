import { motion } from 'framer-motion';
import { Header } from '../components/Header';
import { ChatShell } from '../components/ChatShell';
import { StatusPanel } from '../components/StatusPanel';
import { EvaluationPanel } from '../components/EvaluationPanel';

export function ChatPage() {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="flex flex-col h-screen gradient-mesh overflow-hidden font-sans relative"
    >
      {/* Background decoration */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary-200/30 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-200/20 blur-[100px] pointer-events-none" />

      <Header />
      
      <div className="flex-1 flex overflow-hidden relative z-10">
        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col relative h-full">
          <ChatShell />
        </main>
        
        {/* Right Sidebar - Info Panel */}
        <aside className="w-[340px] glass-panel p-6 overflow-y-auto hidden lg:block">
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <h2 className="text-lg font-bold text-slate-800 mb-2">About AgriGenius</h2>
            <p className="text-sm text-slate-600 leading-relaxed">
              This prototype demonstrates Retrieval-Augmented Generation (RAG) using real Kisan Call Centre advisory records to answer farmer queries accurately.
            </p>
          </motion.div>
          
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
            <StatusPanel />
          </motion.div>
          
          <div className="my-6" />
          
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
            <EvaluationPanel />
          </motion.div>
        </aside>
      </div>
    </motion.div>
  );
}
