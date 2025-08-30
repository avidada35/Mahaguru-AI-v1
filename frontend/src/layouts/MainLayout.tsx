import { Outlet } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import LeftRail from '@/components/layout/LeftRail';

export default function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1 ml-[72px] md:ml-[72px]">
        <Outlet />
      </main>
      <Footer />
      <Toaster />
      
      {/* Left Rail */}
      <LeftRail />
    </div>
  );
}
