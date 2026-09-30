import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  TrendingUp, 
  Users, 
  Database, 
  BrainCircuit, 
  LineChart, 
  AlertTriangle, 
  Settings, 
  LogOut, 
  FileSpreadsheet,
  ChevronDown
} from 'lucide-react';

interface SidebarLayoutProps {
  children: React.ReactNode;
}

export const SidebarLayout: React.FC<SidebarLayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const menuItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Sales Performance', path: '/sales', icon: TrendingUp },
    { name: 'Customer Analytics', path: '/customers', icon: Users },
    { name: 'Product Analytics', path: '/products', icon: FileSpreadsheet },
    { name: 'Sales Forecasting', path: '/forecast', icon: LineChart },
    { name: 'Anomaly Detection', path: '/anomalies', icon: AlertTriangle },
    { name: 'AI Business Analyst', path: '/ai-analyst', icon: BrainCircuit },
    { name: 'Manage Datasets', path: '/datasets', icon: Database },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  const handleLogout = () => {
    // Basic logout logic placeholder
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-brand-950 font-sans text-brand-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-brand-900 border-r border-brand-800 flex flex-col justify-between">
        <div>
          {/* Header/Logo */}
          <div className="p-6 border-b border-brand-800 flex items-center gap-3">
            <div className="p-2 bg-accent-600 rounded-lg text-white">
              <BrainCircuit size={20} />
            </div>
            <div>
              <h1 className="font-bold text-sm leading-tight text-white">SalesAI</h1>
              <span className="text-[10px] text-brand-400 font-medium">Enterprise Analytics</span>
            </div>
          </div>

          {/* Dataset Selector Dropdown */}
          <div className="p-4 border-b border-brand-800">
            <label className="block text-[10px] text-brand-400 font-semibold mb-1 uppercase tracking-wider">
              Active Dataset
            </label>
            <button className="w-full flex items-center justify-between px-3 py-2 bg-brand-950 border border-brand-800 rounded-lg text-xs text-brand-300 hover:border-brand-700 transition-all">
              <span className="truncate">sample_sales.csv</span>
              <ChevronDown size={14} className="text-brand-400" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive 
                      ? 'bg-accent-600 text-white shadow-md shadow-accent-600/10' 
                      : 'text-brand-300 hover:bg-brand-850 hover:text-white'
                  }`}
                >
                  <Icon size={16} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer info & Logout */}
        <div className="p-4 border-t border-brand-800 space-y-3">
          <div className="flex items-center gap-3 px-2">
            <div className="w-8 h-8 rounded-full bg-accent-600 flex items-center justify-center font-bold text-xs text-white">
              JD
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold text-white truncate">John Doe</p>
              <p className="text-[10px] text-brand-400 truncate">john.doe@company.com</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium text-red-400 hover:bg-red-950/20 hover:text-red-300 transition-all"
          >
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-brand-950 overflow-y-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
};
