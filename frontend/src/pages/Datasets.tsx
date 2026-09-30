import React, { useState, useEffect } from 'react';
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle, Trash2, Database, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

const STANDARD_FIELDS = [
  { key: 'order_date', label: 'Order Date', required: true },
  { key: 'sales', label: 'Sales / Revenue ($)', required: true },
  { key: 'quantity', label: 'Quantity', required: true },
  { key: 'customer_id', label: 'Customer ID', required: true },
  { key: 'customer_name', label: 'Customer Name', required: false },
  { key: 'product_name', label: 'Product Name', required: true },
  { key: 'category', label: 'Category', required: false },
  { key: 'region', label: 'Region', required: false },
  { key: 'profit', label: 'Profit ($)', required: false }
];

const Datasets: React.FC = () => {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  // Mapping stage state
  const [activeUploadDataset, setActiveUploadDataset] = useState<any>(null);
  const [mappings, setMappings] = useState<Record<string, string>>({});
  const [qualityReport, setQualityReport] = useState<any>(null);
  const [error, setError] = useState('');

  const fetchDatasets = async () => {
    setLoading(true);
    try {
      const res = await api.get('/datasets');
      setDatasets(res.data);
    } catch (err: any) {
      setError('Failed to fetch dataset list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await api.post('/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setActiveUploadDataset(res.data);
      setMappings(res.data.column_mappings || {});
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload dataset file');
    } finally {
      setUploading(false);
    }
  };

  const handleConfirmMapping = async () => {
    if (!activeUploadDataset) return;
    setUploading(true);
    setError('');

    try {
      const res = await api.post(`/datasets/${activeUploadDataset.id}/map`, {
        mappings: mappings
      });

      setQualityReport(res.data);
      fetchDatasets();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to confirm mapping');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) return;
    try {
      await api.delete(`/datasets/${id}`);
      fetchDatasets();
      if (activeUploadDataset?.id === id) {
        setActiveUploadDataset(null);
        setQualityReport(null);
      }
    } catch (err: any) {
      alert('Failed to delete dataset');
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Dataset Management</h1>
        <p className="text-xs text-brand-400 mt-1">Upload CSV or XLSX sales spreadsheets, configure column mappings, and audit dataset quality.</p>
      </div>

      {error && (
        <div className="p-4 bg-red-950/30 border border-red-500/30 rounded-xl text-xs text-red-400 flex items-center gap-3">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Upload & Mapping Card */}
      {!activeUploadDataset ? (
        <div className="glass-panel space-y-4">
          <h2 className="text-sm font-semibold text-white">Upload New Sales Dataset</h2>
          <form onSubmit={handleFileUpload} className="space-y-4">
            <div className="border-2 border-dashed border-brand-800 rounded-2xl p-8 text-center bg-brand-950/40 hover:border-accent-500/50 transition-all">
              <FileSpreadsheet className="mx-auto text-accent-500 mb-3" size={36} />
              <p className="text-xs font-semibold text-white">Select a CSV or Excel (.xlsx) file</p>
              <p className="text-[11px] text-brand-400 mt-1">Maximum file size: 100MB</p>
              <input
                type="file"
                accept=".csv, .xlsx, .xls"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="hidden"
                id="file-upload-input"
              />
              <label
                htmlFor="file-upload-input"
                className="inline-block mt-4 px-4 py-2 bg-brand-850 hover:bg-brand-800 text-xs font-semibold text-white rounded-xl cursor-pointer transition-all border border-brand-700"
              >
                Browse Files
              </label>
              {selectedFile && (
                <div className="mt-3 text-xs text-accent-400 font-semibold">
                  Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="px-6 py-3 bg-accent-600 hover:bg-accent-700 active:bg-accent-800 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shadow-md shadow-accent-600/10"
            >
              {uploading ? <RefreshCw className="animate-spin" size={16} /> : <Upload size={16} />}
              <span>Upload & Analyze Columns</span>
            </button>
          </form>
        </div>
      ) : !qualityReport ? (
        /* Column Mapping Step */
        <div className="glass-panel space-y-6">
          <div className="flex justify-between items-center border-b border-brand-800 pb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">Step 2: Map Columns for "{activeUploadDataset.filename}"</h2>
              <p className="text-xs text-brand-400 mt-0.5">Match standard database attributes to your spreadsheet headers.</p>
            </div>
            <button
              onClick={() => setActiveUploadDataset(null)}
              className="text-xs text-brand-400 hover:text-white"
            >
              Cancel
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {STANDARD_FIELDS.map((field) => (
              <div key={field.key} className="p-3 bg-brand-950 border border-brand-800 rounded-xl space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-white">
                    {field.label} {field.required && <b className="text-red-400">*</b>}
                  </span>
                  <span className="text-[10px] text-brand-500 font-mono">{field.key}</span>
                </div>

                <input
                  type="text"
                  value={mappings[field.key] || ''}
                  onChange={(e) => setMappings({ ...mappings, [field.key]: e.target.value })}
                  placeholder="CSV Header Name..."
                  className="w-full bg-brand-900 border border-brand-800 rounded-lg px-3 py-1.5 text-xs text-white placeholder-brand-600 focus:outline-none focus:border-accent-500"
                />
              </div>
            ))}
          </div>

          <button
            onClick={handleConfirmMapping}
            disabled={uploading}
            className="px-6 py-3 bg-accent-600 hover:bg-accent-700 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shadow-md shadow-accent-600/10"
          >
            {uploading ? <RefreshCw className="animate-spin" size={16} /> : <CheckCircle2 size={16} />}
            <span>Validate & Run Data Cleaner</span>
          </button>
        </div>
      ) : (
        /* Quality Report Summary */
        <div className="glass-panel space-y-6 border-emerald-500/30">
          <div className="flex justify-between items-center border-b border-brand-800 pb-4">
            <div>
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <CheckCircle2 className="text-emerald-400" size={18} />
                <span>Dataset Prepared Successfully!</span>
              </h2>
              <p className="text-xs text-brand-400 mt-0.5">Data cleaning and validation complete.</p>
            </div>
            <button
              onClick={() => { setActiveUploadDataset(null); setQualityReport(null); }}
              className="px-4 py-2 bg-brand-800 hover:bg-brand-700 text-xs font-semibold text-white rounded-xl"
            >
              Done
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-brand-950 rounded-xl border border-brand-800">
              <p className="text-[10px] font-semibold text-brand-400 uppercase">Quality Score</p>
              <h3 className="text-2xl font-bold text-emerald-400 mt-1">{qualityReport.quality_score} / 100</h3>
            </div>
            <div className="p-4 bg-brand-950 rounded-xl border border-brand-800">
              <p className="text-[10px] font-semibold text-brand-400 uppercase">Cleaned Rows</p>
              <h3 className="text-2xl font-bold text-white mt-1">{qualityReport.rows?.toLocaleString()}</h3>
            </div>
            <div className="p-4 bg-brand-950 rounded-xl border border-brand-800">
              <p className="text-[10px] font-semibold text-brand-400 uppercase">Duplicates Removed</p>
              <h3 className="text-2xl font-bold text-white mt-1">{qualityReport.duplicate_rows}</h3>
            </div>
            <div className="p-4 bg-brand-950 rounded-xl border border-brand-800">
              <p className="text-[10px] font-semibold text-brand-400 uppercase">Date Range</p>
              <h3 className="text-xs font-bold text-white mt-2">
                {qualityReport.date_range ? `${qualityReport.date_range[0]} to ${qualityReport.date_range[1]}` : 'N/A'}
              </h3>
            </div>
          </div>
        </div>
      )}

      {/* Dataset History List */}
      <div className="glass-panel space-y-4">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          <Database size={16} className="text-accent-500" />
          <span>Uploaded Datasets</span>
        </h2>

        {loading ? (
          <p className="text-xs text-brand-400">Loading datasets...</p>
        ) : datasets.length === 0 ? (
          <p className="text-xs text-brand-400">No datasets uploaded yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-brand-800 text-brand-400 uppercase text-[10px] tracking-wider">
                  <th className="py-3 px-4">Filename</th>
                  <th className="py-3 px-4">Rows</th>
                  <th className="py-3 px-4">Quality Score</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Uploaded At</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-850">
                {datasets.map((ds: any) => (
                  <tr key={ds.id} className="hover:bg-brand-900/40 transition-colors">
                    <td className="py-3 px-4 font-semibold text-white">{ds.filename}</td>
                    <td className="py-3 px-4 text-brand-300">{ds.row_count?.toLocaleString()}</td>
                    <td className="py-3 px-4 font-bold text-emerald-400">{ds.data_quality_score} / 100</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        ds.status === 'mapped' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                      }`}>
                        {ds.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-brand-400 text-[11px]">
                      {new Date(ds.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDelete(ds.id)}
                        className="p-1.5 hover:bg-red-950/40 text-red-400 rounded-lg transition-all"
                        title="Delete dataset"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Datasets;
