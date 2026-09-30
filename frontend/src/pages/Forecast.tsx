import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { RefreshCw, AlertCircle, Calendar } from 'lucide-react';
import { api } from '../services/api';

const Forecast: React.FC = () => {
  const [horizon, setHorizon] = useState<number>(30);
  const [forecastData, setForecastData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchForecast = async () => {
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

      const res = await api.post(`/forecast/${activeDataset.id}?horizon_days=${horizon}`);
      setForecastData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to compute forecast');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [horizon]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <RefreshCw className="animate-spin text-accent-500" size={32} />
        <p className="text-xs text-brand-400 font-medium">Training Random Forest model & computing prediction intervals...</p>
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

  const historical = forecastData?.historical || [];
  const forecast = forecastData?.forecast || [];
  const metrics = forecastData?.metrics || {};

  // Combine historical and forecast into single timeline array
  const combinedTimeline = [
    ...historical.map((h: any) => ({ ...h, historical_sales: h.sales })),
    ...forecast.map((f: any) => ({ ...f, forecast_sales: f.sales }))
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Sales Forecasting</h1>
          <p className="text-xs text-brand-400 mt-1">Random Forest time-series model with 95% confidence interval estimation.</p>
        </div>

        <div className="flex items-center gap-3">
          <label className="text-xs text-brand-300 font-semibold flex items-center gap-1.5">
            <Calendar size={14} />
            <span>Horizon:</span>
          </label>
          <div className="flex bg-brand-900 border border-brand-800 rounded-xl p-1">
            {[30, 60, 90].map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                  horizon === h ? 'bg-accent-600 text-white' : 'text-brand-400 hover:text-white'
                }`}
              >
                {h} Days
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Model Performance Metrics Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel">
          <p className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider">Mean Absolute Error (MAE)</p>
          <h3 className="text-2xl font-bold text-white mt-1">${metrics.mae?.toLocaleString()}</h3>
        </div>
        <div className="glass-panel">
          <p className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider">Root Mean Squared Error (RMSE)</p>
          <h3 className="text-2xl font-bold text-white mt-1">${metrics.rmse?.toLocaleString()}</h3>
        </div>
        <div className="glass-panel">
          <p className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider">MAPE</p>
          <h3 className="text-2xl font-bold text-white mt-1">{metrics.mape}%</h3>
        </div>
      </div>

      {/* Main Forecast Chart */}
      <div className="glass-panel space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-sm font-semibold text-white">Historical Sales vs Projected Timeline</h2>
          <span className="text-[10px] text-brand-400">Shaded area = 95% Confidence Interval</span>
        </div>

        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={combinedTimeline}>
              <defs>
                <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} tickFormatter={(v) => `$${v}`} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
              <Legend />
              
              {/* Confidence interval bounds */}
              <Area type="monotone" dataKey="upper_bound" name="Upper Confidence" stroke="none" fill="#3b82f6" fillOpacity={0.1} />
              <Area type="monotone" dataKey="historical_sales" name="Historical Sales ($)" stroke="#8b5cf6" fill="none" strokeWidth={2} />
              <Area type="monotone" dataKey="forecast_sales" name="Predicted Sales ($)" stroke="#3b82f6" strokeDasharray="5 5" fill="url(#colorForecast)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Forecast;
