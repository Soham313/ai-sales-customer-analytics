import React, { useState, useEffect } from 'react';
import { 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  Cell 
} from 'recharts';
import { RefreshCw, AlertCircle, Layers } from 'lucide-react';
import { api } from '../services/api';

const CLUSTER_COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1', '#14b8a6'];

const Customers: React.FC = () => {
  const [rfmData, setRfmData] = useState<any>(null);
  const [segmentationData, setSegmentationData] = useState<any>(null);
  const [numClusters, setNumClusters] = useState<number>(4);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const dsRes = await api.get('/datasets');
      const activeDataset = dsRes.data.find((d: any) => d.status === 'mapped') || dsRes.data[0];
      if (!activeDataset) {
        setError('No mapped dataset available. Please upload a dataset first.');
        setLoading(false);
        return;
      }

      const [rfmRes, segRes] = await Promise.all([
        api.get(`/customers/${activeDataset.id}/rfm`),
        api.post(`/customers/${activeDataset.id}/segmentation?n_clusters=${numClusters}`)
      ]);

      setRfmData(rfmRes.data);
      setSegmentationData(segRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load customer analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [numClusters]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <RefreshCw className="animate-spin text-accent-500" size={32} />
        <p className="text-xs text-brand-400 font-medium">Running RFM analysis & K-Means clustering...</p>
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

  const profiles = rfmData?.summary?.profiles || [];
  const clusterProfiles = segmentationData?.segmentation?.profiles || [];
  const pcaCustomers = segmentationData?.segmentation?.customers || [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Customer Analytics & Segmentation</h1>
        <p className="text-xs text-brand-400 mt-1">RFM Quintile scoring, K-Means ML clustering, and PCA 2D projection.</p>
      </div>

      {/* RFM Segment Cards Grid */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-white">Rule-Based RFM Business Segments</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {profiles.map((prof: any, idx: number) => (
            <div key={idx} className="glass-panel space-y-3 relative overflow-hidden">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-white">{prof.segment}</h3>
                <span className="text-xs font-bold px-2 py-0.5 bg-accent-600/20 text-accent-400 rounded-full">
                  {prof.customer_count} Customers
                </span>
              </div>
              <p className="text-[11px] text-brand-400 leading-relaxed">{prof.description}</p>
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-brand-800 text-[10px] text-brand-300">
                <div>Recency: <b className="text-white">{prof.recency}d</b></div>
                <div>Freq: <b className="text-white">{prof.frequency}x</b></div>
                <div>Monetary: <b className="text-white">${prof.monetary}</b></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ML K-Means Clustering Section */}
      <div className="glass-panel space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Layers className="text-accent-500" size={18} />
              <h2 className="text-sm font-semibold text-white">Unsupervised K-Means Customer Clustering</h2>
            </div>
            <p className="text-xs text-brand-400 mt-0.5">Feature standardization and PCA dimensionality reduction.</p>
          </div>

          <div className="flex items-center gap-3">
            <label className="text-xs text-brand-300 font-semibold">Clusters (K):</label>
            <select
              value={numClusters}
              onChange={(e) => setNumClusters(Number(e.target.value))}
              className="bg-brand-950 border border-brand-800 rounded-xl px-3 py-1.5 text-xs text-white"
            >
              {[2, 3, 4, 5, 6, 7, 8].map((k) => (
                <option key={k} value={k}>K = {k}</option>
              ))}
            </select>
          </div>
        </div>

        {/* PCA Scatter Plot & Profiles */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-2">
            <h3 className="text-xs font-semibold text-brand-300">PCA 2D Cluster Projection</h3>
            <div className="h-[320px] w-full bg-brand-950/50 rounded-xl p-2 border border-brand-800">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                  <XAxis type="number" dataKey="pca_x" name="PCA Component 1" stroke="#94a3b8" fontSize={10} />
                  <YAxis type="number" dataKey="pca_y" name="PCA Component 2" stroke="#94a3b8" fontSize={10} />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '11px' }} 
                    formatter={(_value: any, _name: any, item: any) => [
                      `Cluster: ${item.payload.business_label} | Spent: $${item.payload.monetary}`,
                      item.payload.customer_name
                    ]}
                  />
                  <Scatter data={pcaCustomers} fill="#8b5cf6">
                    {pcaCustomers.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={CLUSTER_COLORS[entry.cluster % CLUSTER_COLORS.length]} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-xs font-semibold text-brand-300">Discovered Cluster Profiles</h3>
            <div className="space-y-3">
              {clusterProfiles.map((c: any, idx: number) => (
                <div key={idx} className="p-3 bg-brand-950 border border-brand-800 rounded-xl space-y-1 text-xs">
                  <div className="flex justify-between items-center font-bold">
                    <span style={{ color: CLUSTER_COLORS[c.cluster_id % CLUSTER_COLORS.length] }}>
                      {c.label}
                    </span>
                    <span className="text-[10px] text-brand-400">{c.size} Accounts</span>
                  </div>
                  <div className="text-[10px] text-brand-300 flex justify-between pt-1">
                    <span>Avg Recency: <b>{c.average_recency}d</b></span>
                    <span>Avg Spend: <b>${c.average_monetary}</b></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Customers;
