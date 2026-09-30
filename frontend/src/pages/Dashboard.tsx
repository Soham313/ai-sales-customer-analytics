import React, { useState, useEffect } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  BarChart, Bar, Cell 
} from 'recharts';
import { 
  TrendingUp, DollarSign, ShoppingBag, Percent, Sparkles, Filter, AlertCircle, RefreshCw 
} from 'lucide-react';
import { api } from '../services/api';

const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

const Dashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filter states
  const [region, setRegion] = useState('');
  const [category, setCategory] = useState('');

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      // Fetch datasets list first to get active dataset
      const dsRes = await api.get('/datasets');
      const datasets = dsRes.data;
      
      if (!datasets || datasets.length === 0) {
        setError('No dataset uploaded yet. Please upload a dataset on the Datasets page.');
        setLoading(false);
        return;
      }
      
      // Use latest mapped dataset
      const activeDataset = datasets.find((d: any) => d.status === 'mapped') || datasets[0];
      
      const queryParams = new URLSearchParams();
      if (region) queryParams.append('region', region);
      if (category) queryParams.append('category', category);

      const [dashRes, insightRes] = await Promise.all([
        api.get(`/dashboard/${activeDataset.id}?${queryParams.toString()}`),
        api.get(`/ai/${activeDataset.id}/insights`).catch(() => ({ data: { insights: [] } }))
      ]);

      setData(dashRes.data);
      setInsights(insightRes.data.insights || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [region, category]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <RefreshCw className="animate-spin text-accent-500" size={32} />
        <p className="text-xs text-brand-400 font-medium">Computing analytics engine metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel border-red-500/30 bg-red-950/20 p-8 text-center space-y-4">
        <AlertCircle className="mx-auto text-red-400" size={40} />
        <h2 className="text-lg font-bold text-white">Dashboard Notice</h2>
        <p className="text-xs text-brand-300 max-w-md mx-auto">{error}</p>
        <button 
          onClick={fetchDashboardData} 
          className="px-4 py-2 bg-brand-800 hover:bg-brand-700 text-xs font-semibold text-white rounded-xl transition-all"
        >
          Try Again
        </button>
      </div>
    );
  }

  const kpis = data?.kpis || {};

  return (
    <div className="space-y-8">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Executive Dashboard</h1>
          <p className="text-xs text-brand-400 mt-1">Real-time financial performance and quantitative metrics.</p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-brand-900 border border-brand-800 rounded-xl text-xs text-brand-400">
            <Filter size={14} />
            <span className="font-semibold">Filters:</span>
          </div>

          <select 
            value={region} 
            onChange={(e) => setRegion(e.target.value)}
            className="bg-brand-900 border border-brand-800 rounded-xl px-3 py-2 text-xs text-brand-200 focus:outline-none focus:border-accent-500 transition-all"
          >
            <option value="">All Regions</option>
            <option value="North">North</option>
            <option value="South">South</option>
            <option value="East">East</option>
            <option value="West">West</option>
          </select>

          <select 
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
            className="bg-brand-900 border border-brand-800 rounded-xl px-3 py-2 text-xs text-brand-200 focus:outline-none focus:border-accent-500 transition-all"
          >
            <option value="">All Categories</option>
            <option value="Electronics">Electronics</option>
            <option value="Furniture">Furniture</option>
            <option value="Office Supplies">Office Supplies</option>
            <option value="Clothing">Clothing</option>
          </select>
        </div>
      </div>

      {/* Automated AI Insights Banner */}
      {insights.length > 0 && (
        <div className="glass-panel bg-gradient-to-r from-accent-900/30 via-brand-900/40 to-brand-900/40 border-accent-500/30 p-5">
          <div className="flex items-center gap-2 mb-3 text-accent-400 font-semibold text-xs uppercase tracking-wider">
            <Sparkles size={16} />
            <span>Automated AI Executive Insights</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {insights.map((ins: any, idx: number) => (
              <div key={idx} className="flex items-start gap-2 text-brand-200">
                <span className="text-accent-400 font-bold">•</span>
                <span>{ins.fact}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Total Revenue', value: `$${kpis.total_revenue?.toLocaleString()}`, icon: DollarSign, color: 'text-purple-400' },
          { label: 'Total Profit', value: `$${kpis.total_profit?.toLocaleString()}`, icon: TrendingUp, color: 'text-emerald-400' },
          { label: 'Profit Margin', value: `${kpis.profit_margin}%`, icon: Percent, color: 'text-blue-400' },
          { label: 'Total Orders', value: kpis.total_orders?.toLocaleString(), icon: ShoppingBag, color: 'text-amber-400' },
        ].map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="glass-panel flex items-center justify-between">
              <div>
                <p className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider">{kpi.label}</p>
                <h3 className="text-2xl font-bold text-white mt-1.5 tracking-tight">{kpi.value}</h3>
              </div>
              <div className={`p-3 bg-brand-850 rounded-2xl ${kpi.color}`}>
                <Icon size={22} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue & Profit Trend Chart */}
        <div className="glass-panel lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Revenue & Profit Over Time</h2>
            <span className="text-[10px] text-brand-400">Aggregated Time Series</span>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.revenue_trend || []}>
                <defs>
                  <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                <Area type="monotone" dataKey="sales" name="Sales ($)" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorSales)" strokeWidth={2} />
                <Area type="monotone" dataKey="profit" name="Profit ($)" stroke="#10b981" fillOpacity={1} fill="url(#colorProfit)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Revenue by Category Chart */}
        <div className="glass-panel space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Revenue by Category</h2>
            <span className="text-[10px] text-brand-400">Category Margins</span>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.category_distribution || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis type="number" stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `$${v}`} />
                <YAxis type="category" dataKey="category" stroke="#94a3b8" fontSize={11} tickLine={false} width={90} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                <Bar dataKey="sales" name="Sales ($)" radius={[0, 8, 8, 0]}>
                  {(data?.category_distribution || []).map((_entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
