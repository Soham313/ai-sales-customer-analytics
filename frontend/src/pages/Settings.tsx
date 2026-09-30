import React from 'react';
import { Key, Server } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Settings</h1>
        <p className="text-xs text-brand-400 mt-1">Configure workspace parameters, security tokens, and backend services.</p>
      </div>

      <div className="glass-panel space-y-6">
        <div className="flex items-center gap-3 border-b border-brand-800 pb-4">
          <div className="p-2.5 bg-accent-600/20 text-accent-400 rounded-xl">
            <Key size={20} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Groq AI Analyst API Configuration</h2>
            <p className="text-xs text-brand-400">Generative business explanations are routed through Groq LLaMA 3.3.</p>
          </div>
        </div>

        <div className="space-y-3">
          <label className="block text-xs font-semibold text-brand-300">Active GROQ API Key Status</label>
          <div className="p-3 bg-brand-950 border border-brand-800 rounded-xl text-xs flex justify-between items-center">
            <span className="font-mono text-brand-400">GROQ_API_KEY (Environment Variable)</span>
            <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-400 font-semibold rounded-full text-[10px]">
              Configured
            </span>
          </div>
          <p className="text-[11px] text-brand-400">
            Secrets are loaded safely from the backend <code className="text-accent-400">.env</code> file and are never exposed to client browsers.
          </p>
        </div>
      </div>

      <div className="glass-panel space-y-6">
        <div className="flex items-center gap-3 border-b border-brand-800 pb-4">
          <div className="p-2.5 bg-blue-500/20 text-blue-400 rounded-xl">
            <Server size={20} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Database Engine & Storage</h2>
            <p className="text-xs text-brand-400">Relational SQLite ORM with PostgreSQL migration support.</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-brand-950 border border-brand-800 rounded-xl space-y-1">
            <span className="text-[10px] text-brand-400 uppercase font-semibold">ORM Layer</span>
            <p className="font-bold text-white">SQLAlchemy 2.0</p>
          </div>
          <div className="p-3 bg-brand-950 border border-brand-800 rounded-xl space-y-1">
            <span className="text-[10px] text-brand-400 uppercase font-semibold">Isolation Strategy</span>
            <p className="font-bold text-white">User-Scoped Disk Storage</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
