import { useNavigate } from 'react-router-dom';
import HeroSection from '@/components/home/HeroSection';
import TrainingGrounds from '@/components/home/TrainingGrounds';

interface HomePageProps {}

const HomePage: React.FC<HomePageProps> = () => {
  const navigate = useNavigate();

  const handleSearch = (query: string) => {
    if (query.trim()) {
      // TODO: Call search API and navigate based on response type
      // For now, just navigate to a sample classroom
      navigate('/classroom/sample');
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <div className="relative bg-gradient-to-b from-sky-50 via-sky-50 to-white overflow-hidden">
        {/* Neural Pattern Overlay */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
          <svg className="w-full h-full" viewBox="0 0 1200 800">
            <defs>
              <pattern id="neural" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
                {/* Neural nodes */}
                <circle cx="20" cy="20" r="1.5" fill="#3A82F7" opacity="0.6"/>
                <circle cx="80" cy="30" r="1.2" fill="#3A82F7" opacity="0.5"/>
                <circle cx="40" cy="70" r="1.8" fill="#3A82F7" opacity="0.4"/>
                <circle cx="90" cy="80" r="1.3" fill="#3A82F7" opacity="0.5"/>
                
                {/* Synaptic connections */}
                <path d="M20 20 Q50 25 80 30" stroke="#3A82F7" strokeWidth="0.8" opacity="0.3" fill="none"/>
                <path d="M20 20 Q30 45 40 70" stroke="#3A82F7" strokeWidth="0.6" opacity="0.25" fill="none"/>
                <path d="M80 30 Q65 55 90 80" stroke="#3A82F7" strokeWidth="0.7" opacity="0.3" fill="none"/>
                <path d="M40 70 Q65 75 90 80" stroke="#3A82F7" strokeWidth="0.5" opacity="0.2" fill="none"/>
              </pattern>
            </defs>
            <rect width="1200" height="800" fill="url(#neural)" />
          </svg>
        </div>

        {/* Mandala Rings */}
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 opacity-[0.02] pointer-events-none">
          <svg className="w-96 h-96" viewBox="0 0 100 100">
            {/* Outer ring */}
            <circle cx="50" cy="50" r="45" fill="none" stroke="#3A82F7" strokeWidth="0.3"/>
            {/* Middle ring */}
            <circle cx="50" cy="50" r="30" fill="none" stroke="#3A82F7" strokeWidth="0.2"/>
            {/* Inner ring */}
            <circle cx="50" cy="50" r="15" fill="none" stroke="#3A82F7" strokeWidth="0.15"/>
            {/* Center dot */}
            <circle cx="50" cy="50" r="2" fill="#3A82F7" opacity="0.4"/>
          </svg>
        </div>

        {/* Secondary mandala (smaller, offset) */}
        <div className="absolute top-20 right-20 opacity-[0.015] pointer-events-none">
          <svg className="w-64 h-64" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="35" fill="none" stroke="#3A82F7" strokeWidth="0.25"/>
            <circle cx="50" cy="50" r="20" fill="none" stroke="#3A82F7" strokeWidth="0.15"/>
            <circle cx="50" cy="50" r="8" fill="none" stroke="#3A82F7" strokeWidth="0.1"/>
          </svg>
        </div>

        <HeroSection onSearch={handleSearch} />
        <TrainingGrounds />
        
        {/* Call to Action Section */}
        <section className="py-16 bg-white relative z-10">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-serif font-bold text-ink mb-4">Begin Your Journey</h2>
              <p className="text-muted max-w-2xl mx-auto">
                Join thousands of seekers who are transforming their lives with the wisdom of the ages.
              </p>
              <button 
                onClick={() => navigate('/register')}
                className="mt-6 inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-full text-white bg-primary hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors duration-200"
              >
                Start Your Sadhana Today
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default HomePage;
