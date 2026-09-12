import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Leaf, ArrowRight, ShieldCheck, Database, Zap } from 'lucide-react';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen gradient-mesh flex flex-col relative overflow-hidden">
      {/* Navbar */}
      <nav className="glass sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-3"
            >
              <div className="bg-gradient-to-br from-primary-400 to-primary-600 p-2.5 rounded-xl shadow-lg shadow-primary-500/30">
                <Leaf className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 tracking-tight">
                AgriGenius
              </span>
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex items-center justify-center relative z-10 px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-semibold bg-white/80 text-primary-700 border border-primary-200/50 shadow-sm mb-8 backdrop-blur-sm">
              <span className="flex h-2 w-2 relative mr-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
              </span>
              Powered by KCC RAG Intelligence
            </span>
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl font-extrabold text-slate-900 tracking-tight mb-8 leading-tight"
          >
            Your Expert <br/>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-emerald-400">
              Farming Assistant
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-slate-600 mb-12 max-w-2xl mx-auto leading-relaxed"
          >
            Get instant, evidence-based answers to your agricultural queries in English and Hindi. Grounded in 340,000+ authentic Kisan Call Centre advisory records.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <button 
              onClick={() => navigate('/chat')}
              className="group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white transition-all duration-200 bg-primary-600 font-pj rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-600 hover:bg-primary-700 hover:shadow-xl hover:shadow-primary-500/30 hover:-translate-y-1"
            >
              Start Consulting Now
              <ArrowRight className="w-5 h-5 ml-3 group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>
        </div>
      </main>

      {/* Feature grid */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<ShieldCheck className="w-6 h-6 text-emerald-600" />}
            title="Evidence-Based"
            desc="Every answer is directly grounded in verified KCC data, reducing hallucinations."
            delay={0.4}
          />
          <FeatureCard 
            icon={<Zap className="w-6 h-6 text-amber-500" />}
            title="Bilingual Ready"
            desc="Supports both English and Hindi queries seamlessly with cross-lingual RAG."
            delay={0.5}
          />
          <FeatureCard 
            icon={<Database className="w-6 h-6 text-blue-500" />}
            title="Massive Knowledge Base"
            desc="Searches through 347,944 historical advisory records in milliseconds."
            delay={0.6}
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, desc, delay }: { icon: React.ReactNode, title: string, desc: string, delay: number }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -5 }}
      className="glass-card p-6 rounded-2xl"
    >
      <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center mb-6">
        {icon}
      </div>
      <h3 className="text-xl font-bold text-slate-800 mb-3">{title}</h3>
      <p className="text-slate-600 leading-relaxed">{desc}</p>
    </motion.div>
  );
}
