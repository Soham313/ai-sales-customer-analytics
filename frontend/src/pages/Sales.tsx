import React, { useState, useEffect } from 'react';
import { ArrowUpRight, ArrowDownRight, RefreshCw, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

const Sales: React.FC = () => {
  const [startDate, setStartDate] = useState('2025-01-01');
  const [endDate, setEndDate] = useState('2026-08-01');
  const [salesData, setSalesData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchSalesData = async () => {
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

      const res = await api.get(`/sales/${activeDataset.id}?start_date=${startDate}&end_date=${endDate}`);
      setSalesData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load sales comparison metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSalesData();
  }, [startDate, endDate]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <RefreshCw className="animate-spin text-accent-500" size={32} />
        <p className="text-xs text-brand-400 font-medium">Computing comparative growth rates...</p>
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

  const current = salesData?.current_period || {};
  const previous = salesData?.previous_period || {};
  const growth = salesData?.growth || {};

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Sales Performance Analytics</h1>
          <p className="text-xs text-brand-400 mt-1">Period-over-Period growth comparisons and performance margins.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-brand-900 border border-brand-800 rounded-xl px-3 py-1.5 text-xs text-white">
            <span className="text-brand-400">From:</span>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="bg-transparent border-none focus:outline-none text-xs text-white"
            />
            <span className="text-brand-400">To:</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="bg-transparent border-none focus:outline-none text-xs text-white"
            />
          </div>
        </div>
      </div>

      {/* Growth Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Revenue Growth', current: current.total_revenue, prev: previous.total_revenue, growth: growth.total_revenue },
          { label: 'Profit Growth', current: current.total_profit, prev: previous.total_profit, growth: growth.total_profit },
          { label: 'Order Volume Growth', current: current.total_orders, prev: previous.total_orders, growth: growth.total_orders },
        ].map((card, idx) => {
          const isUp = card.growth >= 0;
          return (
            <div key={idx} className="glass-panel space-y-3">
              <div className="flex justify-between items-center">
                <p className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider">{card.label}</p>
                <div className={`flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full ${
                  isUp ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                }`}>
                  {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                  <span>{card.growth}%</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white">${card.current?.toLocaleString()}</h3>
              <p className="text-[11px] text-brand-400">Previous Period: <b>${card.prev?.toLocaleString()}</b></p>
            </div>
          );
        })}
      </div>

      {/* Margins and Selling Price Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel space-y-2">
          <h3 className="text-sm font-semibold text-white">Average Order Value (AOV)</h3>
          <p className="text-2xl font-bold text-accent-400">${current.average_order_value}</p>
          <p className="text-xs text-brand-400">Previous period AOV was ${previous.average_order_value}</p>
        </div>

        <div className="glass-panel space-y-2">
          <h3 className="text-sm font-semibold text-white">Average Selling Price (ASP)</h3>
          <p className="text-2xl font-bold text-blue-400">${current.average_selling_price}</p>
          <p className="text-xs text-brand-400">Previous period ASP was ${previous.average_selling_price}</p>
        </div>
      </div>
    </div>
  );
};

export default Sales;
