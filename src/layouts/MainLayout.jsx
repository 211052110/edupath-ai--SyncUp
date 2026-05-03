import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-base text-text-primary flex">
      <Sidebar />
      <main className="flex-1 ml-[240px] relative">
        <div className="gradient-orb top-[-100px] right-[-100px] w-[300px] h-[300px] bg-primary"></div>
        <div className="gradient-orb bottom-[-100px] left-[-100px] w-[300px] h-[300px] bg-secondary"></div>
        <div className="noise-overlay z-0"></div>
        <div className="relative z-10 max-w-[1280px] mx-auto min-h-screen flex flex-col">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
