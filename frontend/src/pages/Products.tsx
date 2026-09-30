import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { RefreshCw, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

const Products: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchProducts = async () => {
    setLoading(true);
    setError('');
    try {
      const dsRes = await api.get('/datasets');
      const activeDataset = dsRes.data.find((d: any) => d.status === 'mapped') || dsRes.data[0];
      if (!activeDataset) {
        setError('No dataset available.');
        setLoading(false);
        return;
      }

      const res = await api.get(`/dashboard/${activeDataset.id}`);
      setDashboardData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load product analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <RefreshCw className="animate-spin text-accent-500" size={32} />
        <p className="text-xs text-brand-400 font-medium">Aggregating category and product margin data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel border-red-500/30 bg-red-950/20 p-8 text-center space-y-4">
        <AlertCircle className="mx-auto text-red-400" size={40} />
        <p className="text-xs text-brand-300">{error}</p>
      </div>
    );
  }

  const categoryDist = dashboardData?.category_distribution || [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Product Performance</h1>
        <p className="text-xs text-brand-400 mt-1">Category volume distributions, margin profiles, and top items.</p>
      </div>

      {/* Category Distribution Chart */}
      <div className="glass-panel space-y-4">
        <h2 className="text-sm font-semibold text-white">Revenue & Profit Margins by Category</h2>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryDist}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="category" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `$${v}`} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
              <Bar dataKey="sales" name="Sales ($)" radius={[8, 8, 0, 0]}>
                {categoryDist.map((_entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
              <Bar dataKey="profit" name="Profit ($)" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Breakdown Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {categoryDist.map((cat: any, idx: number) => (
          <div key={idx} className="glass-panel space-y-2">
            <p className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider">{cat.category}</p>
            <h3 className="text-xl font-bold text-white">${cat.sales?.toLocaleString()}</h3>
            <div className="flex justify-between text-xs pt-2 border-t border-brand-800">
              <span className="text-brand-400">Margin:</span>
              <span className="font-bold text-emerald-400">{cat.margin}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Products;
