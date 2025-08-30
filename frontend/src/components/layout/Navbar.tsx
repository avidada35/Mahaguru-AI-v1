import { useState, useEffect } from 'react';
import { Menu, X, BookOpen } from 'lucide-react';

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header 
      className={`fixed z-50 transition-all duration-300 ml-[72px] md:ml-[72px] right-0 ${
        isScrolled 
          ? 'bg-white/90 backdrop-blur-md shadow-sm' 
          : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Left: Empty space (profile moved to left rail) */}
          <div className="flex-shrink-0 flex items-center">
            {/* Profile icon removed to prevent overlap with left rail */}
          </div>

          {/* Center: intentionally empty per new spec */}
          <div className="flex-1 flex justify-center">
            {/* Center intentionally empty per new spec */}
          </div>

          {/* Right: Brand Name */}
          <div className="flex-shrink-0 flex items-center">
            <span className="text-xl font-serif font-medium text-ink">Mahaguru AI</span>
          </div>
        </div>
      </nav>

      {/* Mobile menu button */}
      <div className="md:hidden absolute top-4 right-4">
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="inline-flex items-center justify-center p-2 rounded-md text-ink hover:text-primary focus:outline-none"
        >
          <span className="sr-only">Open main menu</span>
          {isMobileMenuOpen ? (
            <X className="block h-6 w-6" aria-hidden="true" />
          ) : (
            <Menu className="block h-6 w-6" aria-hidden="true" />
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white shadow-lg rounded-b-lg mt-16">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <a
              href="#"
              className="block px-3 py-2 rounded-md text-base font-medium text-ink hover:bg-sky-50 hover:text-primary"
            >
              <BookOpen className="w-5 h-5 inline-block mr-2" />
              Classroom
            </a>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
