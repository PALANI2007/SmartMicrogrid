import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  LayoutDashboard, 
  Sun, 
  Zap, 
  Battery as BatteryIcon, 
  CalendarClock, 
  ArrowRightLeft, 
  FlaskConical, 
  BellRing, 
  Settings, 
  HelpCircle,
  Menu,
  X,
  TriangleAlert,
} from 'lucide-react';

const Layout = () => {
  const { t, i18n } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'ta' : 'en';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  const navItems = [
    { to: '/dashboard', icon: <LayoutDashboard size={20} />, label: t('nav.dashboard') },
    { to: '/forecast', icon: <Sun size={20} />, label: t('nav.forecast') },
    { to: '/loads', icon: <Zap size={20} />, label: t('nav.loads') },
    { to: '/battery', icon: <BatteryIcon size={20} />, label: t('nav.battery') },
    { to: '/scheduler', icon: <CalendarClock size={20} />, label: t('nav.scheduler') },
    { to: '/comparison', icon: <ArrowRightLeft size={20} />, label: t('nav.comparison') },
    { to: '/experiments', icon: <FlaskConical size={20} />, label: t('nav.experiments') },
    { to: '/alerts', icon: <BellRing size={20} />, label: t('nav.alerts') },
    { to: '/edge-cases', icon: <TriangleAlert size={20} />, label: t('edgeCases.title') },
    { to: '/settings', icon: <Settings size={20} />, label: t('nav.settings') },
    { to: '/help', icon: <HelpCircle size={20} />, label: t('nav.help') },
  ];

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-20 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-30 w-64 bg-slate-900 border-r border-slate-800 transform transition-transform duration-300 lg:translate-x-0 lg:static lg:inset-auto ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-slate-800">
          <span className="text-xl font-bold text-primary-400">Microgrid Smart</span>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-slate-400 hover:text-white">
            <X size={24} />
          </button>
        </div>
        <nav className="p-4 space-y-1 overflow-y-auto h-[calc(100vh-4rem)]">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
                  isActive 
                    ? 'bg-primary-600/10 text-primary-400 font-semibold' 
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        <header className="h-16 flex items-center justify-between px-6 bg-slate-900/50 backdrop-blur-sm border-b border-slate-800 z-10 sticky top-0">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-slate-400 hover:text-white">
            <Menu size={24} />
          </button>
          
          <div className="ml-auto flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-slate-400">EN</span>
              <button 
                onClick={toggleLanguage}
                className="w-12 h-6 bg-slate-700 rounded-full p-1 relative transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-slate-900"
                aria-label="Toggle Language"
              >
                <div className={`w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-200 ease-in-out ${i18n.language === 'ta' ? 'translate-x-6' : 'translate-x-0'}`} />
              </button>
              <span className="text-sm font-medium text-slate-400">தமிழ்</span>
            </div>
          </div>
        </header>
        
        <div className="flex-1 overflow-y-auto p-6 bg-slate-950">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
