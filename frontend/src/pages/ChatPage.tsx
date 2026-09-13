import { ChatShell } from '../components/ChatShell';
import { motion } from 'framer-motion';

export function ChatPage() {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className="flex h-screen overflow-hidden font-sans"
    >
      <ChatShell />
    </motion.div>
  );
}
