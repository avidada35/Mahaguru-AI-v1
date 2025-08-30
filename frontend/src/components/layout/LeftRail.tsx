import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen, Plus, User, Settings, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useNavigate } from 'react-router-dom';

const LeftRail = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const railRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Handle responsive behavior
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Handle hover for desktop
  const handleMouseEnter = () => {
    if (!isMobile) {
      setIsExpanded(true);
    }
  };

  const handleMouseLeave = () => {
    if (!isMobile) {
      setIsExpanded(false);
    }
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape' && isExpanded) {
      setIsExpanded(false);
    }
  };

  // Handle new chat
  const handleNewChat = () => {
    // TODO: Implement new chat functionality
    console.log('New chat initiated');
  };

  // Handle classroom navigation
  const handleClassroom = () => {
    navigate('/classroom/sample');
  };

  // Handle profile
  const handleProfile = () => {
    // TODO: Implement profile functionality
    console.log('Profile clicked');
  };

  // Handle settings
  const handleSettings = () => {
    // TODO: Implement settings functionality
    console.log('Settings clicked');
  };

  // Mobile rail component
  if (isMobile) {
    return (
      <>
        {/* Mobile bottom mini-nav */}
        <div className="fixed bottom-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-t border-sky-200 shadow-lg">
          <div className="flex items-center justify-around h-16 px-4">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClassroom}
                    className="flex flex-col items-center space-y-1 text-muted hover:text-primary"
                    aria-label="Classroom"
                  >
                    <BookOpen className="w-5 h-5" />
                    <span className="text-xs">Classroom</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="top">Classroom</TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleNewChat}
                    className="flex flex-col items-center space-y-1 text-muted hover:text-primary"
                    aria-label="New conversation"
                  >
                    <Plus className="w-5 h-5" />
                    <span className="text-xs">New</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="top">Start new conversation</TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleProfile}
                    className="flex flex-col items-center space-y-1 text-muted hover:text-primary"
                    aria-label="Profile"
                  >
                    <User className="w-5 h-5" />
                    <span className="text-xs">Profile</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="top">Profile</TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleSettings}
                    className="flex flex-col items-center space-y-1 text-muted hover:text-primary"
                    aria-label="Settings"
                  >
                    <Settings className="w-6 h-6" />
                    <span className="text-xs">Settings</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="top">Settings</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>

        {/* Mobile flyout menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <motion.div
                initial={{ x: '-100%' }}
                animate={{ x: 0 }}
                exit={{ x: '-100%' }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="absolute left-0 top-0 h-full w-64 bg-white shadow-2xl"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="p-6">
                  <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary-600 flex items-center justify-center">
                        <span className="text-white font-serif font-bold text-lg">M</span>
                      </div>
                      <span className="text-xl font-serif font-bold text-ink">Mahaguru AI</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsMobileMenuOpen(false)}
                      aria-label="Close menu"
                    >
                      <X className="w-5 h-5" />
                    </Button>
                  </div>

                  <div className="space-y-4">
                    <Button
                      variant="ghost"
                      className="w-full justify-start text-left h-12"
                      onClick={handleClassroom}
                    >
                      <BookOpen className="w-5 h-5 mr-3" />
                      Classroom
                    </Button>

                    <Button
                      variant="ghost"
                      className="w-full justify-start text-left h-12"
                      onClick={handleNewChat}
                    >
                      <Plus className="w-5 h-5 mr-3" />
                      New
                    </Button>

                    <Button
                      variant="ghost"
                      className="w-full justify-start text-left h-12"
                      onClick={handleProfile}
                    >
                      <User className="w-5 h-5 mr-3" />
                      Profile
                    </Button>

                    <Button
                      variant="ghost"
                      className="w-full justify-start text-left h-12"
                      onClick={handleSettings}
                    >
                      <Settings className="w-6 h-6 mr-3" />
                      Settings
                    </Button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </>
    );
  }

  // Desktop rail component
  return (
    <TooltipProvider>
      <motion.div
        ref={railRef}
        className="fixed left-0 top-0 h-full z-40"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onKeyDown={handleKeyDown}
        initial={false}
        animate={{
          width: isExpanded ? 240 : 72,
        }}
        transition={{ duration: 0.18, ease: "easeOut" }}
      >
        <div className="h-full bg-white/80 backdrop-blur-md border-r border-sky-200 shadow-lg">
          <div className="flex flex-col h-full">
            {/* Mahaguru Logo & Name */}
            <div className="p-4 border-b border-sky-100">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary-600 flex items-center justify-center flex-shrink-0">
                  <span className="text-white font-serif font-bold text-lg">M</span>
                </div>
                <AnimatePresence>
                  {isExpanded && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      className="text-xl font-serif font-bold text-ink whitespace-nowrap"
                    >
                      Mahaguru AI
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Navigation Items */}
            <div className="flex-1 py-4 space-y-2">
              {/* Classroom */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    className={`w-full h-12 ${isExpanded ? 'justify-start px-4' : 'justify-center'}`}
                    onClick={handleClassroom}
                    aria-label="Classroom"
                  >
                    <BookOpen className="w-5 h-5" />
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.span
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -10 }}
                          className="ml-3 whitespace-nowrap"
                        >
                          Classroom
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </Button>
                </TooltipTrigger>
                {!isExpanded && <TooltipContent side="right">Classroom</TooltipContent>}
              </Tooltip>

              {/* New Chat */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    className={`w-full h-12 ${isExpanded ? 'justify-start px-4' : 'justify-center'} bg-gradient-to-br from-primary/10 to-primary-600/10 hover:from-primary/20 hover:to-primary-600/20`}
                    onClick={handleNewChat}
                    aria-label="Start new conversation"
                  >
                    <Plus className="w-5 h-5" />
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.span
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -10 }}
                          className="ml-3 whitespace-nowrap"
                        >
                          New
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </Button>
                </TooltipTrigger>
                {!isExpanded && <TooltipContent side="right">Start new conversation</TooltipContent>}
              </Tooltip>

              {/* Profile */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    className={`w-full h-12 ${isExpanded ? 'justify-start px-4' : 'justify-center'}`}
                    onClick={handleProfile}
                    aria-label="Profile"
                  >
                    <div className="relative">
                      <User className="w-5 h-5" />
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                    </div>
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.span
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -10 }}
                          className="ml-3 whitespace-nowrap"
                        >
                          Profile
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </Button>
                </TooltipTrigger>
                {!isExpanded && <TooltipContent side="right">Profile</TooltipContent>}
              </Tooltip>
            </div>

            {/* Settings at bottom */}
            <div className="p-4 border-t border-sky-100">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    className={`w-full h-12 ${isExpanded ? 'justify-start px-4' : 'justify-center'}`}
                    onClick={handleSettings}
                    aria-label="Open settings"
                  >
                    <Settings className="w-6 h-6" />
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.span
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -10 }}
                          className="ml-3 whitespace-nowrap"
                        >
                          Settings
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </Button>
                </TooltipTrigger>
                {!isExpanded && <TooltipContent side="right">Settings</TooltipContent>}
              </Tooltip>
            </div>
          </div>
        </div>
      </motion.div>
    </TooltipProvider>
  );
};

export default LeftRail;
