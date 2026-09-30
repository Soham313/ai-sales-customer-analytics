import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldAlert, RefreshCw, AlertCircle, Calendar } from 'lucide-react';
import { api } from '../services/api';

const Anomalies: React.FC = () => {
  const [anomalyData, setAnomalyData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchAnomalies = async () => {
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

      const res = await api.get(`/anomalies/${activeDataset.id}`);
      setAnomalyData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to detect anomalies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomalies();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <RefreshCw className="animate-spin text-accent-500" size={32} />
        <p className="text-xs text-brand-400 font-medium">Running Isolation Forest anomaly detection...</p>
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

  const transactions = anomalyData?.anomalous_transactions || [];
  const dates = anomalyData?.anomalous_dates || [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Anomaly Detection</h1>
        <p className="text-xs text-brand-400 mt-1">Isolation Forest unsupervised outlier isolation on transaction features.</p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel border-amber-500/30 bg-amber-950/10">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider">Detected Outlier Transactions</p>
              <h3 className="text-3xl font-bold text-white mt-1">{anomalyData?.anomaly_count}</h3>
            </div>
            <div className="p-3 bg-amber-500/20 rounded-2xl text-amber-400">
              <ShieldAlert size={28} />
            </div>
          </div>
        </div>

        <div className="glass-panel">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider">Dataset Anomaly Percentage</p>
              <h3 className="text-3xl font-bold text-white mt-1">{anomalyData?.anomaly_percentage}%</h3>
            </div>
            <div className="p-3 bg-brand-850 rounded-2xl text-accent-400">
              <AlertTriangle size={28} />
            </div>
          </div>
        </div>
      </div>

      {/* Anomalous Dates Summary */}
      {dates.length > 0 && (
        <div className="glass-panel space-y-4">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2">
            <Calendar size={16} className="text-accent-500" />
            <span>Dates with Abnormal Sales Volume</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {dates.map((d: any, idx: number) => (
              <div key={idx} className="p-3 bg-brand-950 border border-brand-800 rounded-xl space-y-1 text-xs">
                <div className="font-bold text-white">{d.date}</div>
                <div className="text-[11px] text-brand-400">Sales: <b>${d.sales}</b></div>
                <div className={`text-[10px] font-semibold ${d.deviation_percentage < 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {d.deviation_percentage > 0 ? `+${d.deviation_percentage}%` : `${d.deviation_percentage}%`} vs Median
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Anomalous Transactions Table */}
      <div className="glass-panel space-y-4 overflow-hidden">
        <h2 className="text-sm font-semibold text-white">Top Outlier Transactions</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-brand-800 text-brand-400 uppercase text-[10px] tracking-wider">
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Product</th>
                <th className="py-3 px-4">Qty</th>
                <th className="py-3 px-4">Sales ($)</th>
                <th className="py-3 px-4">Profit ($)</th>
                <th className="py-3 px-4">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-850">
              {transactions.map((tx: any, idx: number) => (
                <tr key={idx} className="hover:bg-brand-900/40 transition-colors">
                  <td className="py-3 px-4 font-semibold text-white">{tx.order_id}</td>
                  <td className="py-3 px-4 text-brand-300">{tx.order_date}</td>
                  <td className="py-3 px-4 text-brand-300">{tx.customer_name}</td>
                  <td className="py-3 px-4 text-brand-300">{tx.product_name}</td>
                  <td className="py-3 px-4 text-brand-300">{tx.quantity}</td>
                  <td className="py-3 px-4 font-bold text-white">${tx.sales}</td>
                  <td className={`py-3 px-4 font-bold ${tx.profit < 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                    ${tx.profit}
                  </td>
                  <td className="py-3 px-4 text-red-400 font-mono text-[10px]">{tx.anomaly_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Anomalies;
