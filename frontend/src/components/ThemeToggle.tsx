import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useDarkMode } from '../hooks/useDarkMode';

export function ThemeToggle() {
  const { isDark, toggleDarkMode } = useDarkMode();
  const [isSpinning, setIsSpinning] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const handleToggle = () => {
    if (isSpinning) return;
    setIsSpinning(true);

    // Spin accelerates for 0.8 seconds: slow -> fast -> ultra fast
    setTimeout(() => {
      const isViewTransitionSupported = 'startViewTransition' in document;

      if (!isViewTransitionSupported || !buttonRef.current) {
        toggleDarkMode();
        setIsSpinning(false);
        return;
      }

      const rect = buttonRef.current.getBoundingClientRect();
      const x = rect.left + rect.width / 2;
      const y = rect.top + rect.height / 2;
      
      const right = window.innerWidth - x;
      const bottom = window.innerHeight - y;
      const maxRadius = Math.hypot(Math.max(x, right), Math.max(y, bottom));

      // Trigger the magnifying glass view transition (native DOM snapshot)
      const transition = (document as any).startViewTransition(() => {
        toggleDarkMode();
        setIsSpinning(false); // Stop spinning as the blast happens
      });

      transition.ready.then(() => {
        document.documentElement.animate(
          {
            clipPath: [
              `circle(0px at ${x}px ${y}px)`,
              `circle(${maxRadius}px at ${x}px ${y}px)`
            ]
          },
          {
            duration: 800, // snappier expansion
            easing: 'ease-in-out', // Fixes the stall at the end of the transition
            // Always expand the NEW theme over the OLD theme
            pseudoElement: '::view-transition-new(root)'
          }
        );
      });
    }, 800); // Trigger after 0.8s spin up
  };

  return (
    <button 
      ref={buttonRef}
      onClick={handleToggle}
      className="p-2 rounded-lg bg-white/50 hover:bg-white dark:bg-neutral-900/50 dark:hover:bg-neutral-900 shadow-sm relative flex items-center justify-center w-10 h-10 border border-slate-200 dark:border-neutral-800 overflow-hidden cursor-pointer z-50 backdrop-blur-sm"
      aria-label="Toggle Dark Mode"
    >
      <motion.div 
        animate={isSpinning ? { rotate: [0, 90, 360, 1080, 2160] } : { rotate: 0 }}
        transition={isSpinning ? { duration: 0.8, ease: "easeIn" } : { duration: 0 }}
        className="absolute inset-0 flex items-center justify-center"
      >
        {isDark ? <Sun className="w-5 h-5 text-amber-400 drop-shadow-[0_0_8px_rgba(251,191,36,0.6)]" /> : <Moon className="w-5 h-5 text-slate-700 dark:text-neutral-300" />}
      </motion.div>
    </button>
  );
}
