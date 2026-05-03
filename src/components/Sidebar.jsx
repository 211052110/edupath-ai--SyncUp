import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Target, Calculator, MessageSquare, Briefcase,
         Sparkles, Settings, BookOpen, Brain, Rocket } from 'lucide-react';

const NavItem = ({ to, icon: Icon, label }) => {
  const { pathname } = useLocation();
  const isActive = pathname === to || (to === '/dashboard' && pathname === '/');
  return (
    <Link to={to} className={`flex items-center gap-3 h-[44px] px-4 rounded-[10px] text-[14px] font-medium transition-all ${
      isActive ? 'bg-primary/10 border-l-[3px] border-primary text-text-primary'
               : 'text-text-secondary hover:bg-white/5 hover:text-text-primary'}`}>
      <Icon className={`w-5 h-5 ${isActive ? 'text-primary' : 'text-text-secondary'}`} />
      {label}
    </Link>
  );
};

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full w-[240px] bg-base border-r border-border flex flex-col z-50">
      <div className="flex items-center gap-2 px-6 h-[88px]">
        <Sparkles className="w-6 h-6 text-primary" />
        <span className="font-display font-bold text-xl text-text-primary tracking-tight">EduPath</span>
      </div>
      <nav className="flex-1 px-4 flex flex-col gap-1">
        <NavItem to="/dashboard"         icon={LayoutDashboard} label="Dashboard" />
        <NavItem to="/career-simulator"  icon={Rocket}          label="Career Simulator" />
        <NavItem to="/loan-score"        icon={Target}          label="Loan Score" />
        <NavItem to="/roi-calculator"    icon={Calculator}      label="ROI Calculator" />
        <NavItem to="/visa-chat"         icon={MessageSquare}   label="Visa Chat" />
        <NavItem to="/career-insights"   icon={Briefcase}       label="Career Insights" />
        <NavItem to="/university-qa"     icon={BookOpen}        label="University Q&A" />
        <NavItem to="/skill-gap"         icon={Brain}           label="Skill Gap" />
      </nav>
      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-3 p-2 rounded-[10px]">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white font-medium text-sm">S</div>
          <div className="flex-1 overflow-hidden">
            <p className="text-sm font-medium text-text-primary truncate">Student</p>
            <p className="text-xs text-text-secondary truncate">EduPath AI</p>
          </div>
          <Settings className="w-4 h-4 text-text-secondary" />
        </div>
      </div>
    </aside>
  );
}
