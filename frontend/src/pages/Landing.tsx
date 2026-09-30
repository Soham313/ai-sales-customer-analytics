import React from 'react';
import { Link } from 'react-router-dom';
import { BrainCircuit, ArrowRight, BarChart3, ShieldAlert, Sparkles, ShieldCheck } from 'lucide-react';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-brand-950 font-sans text-brand-100 flex flex-col justify-between overflow-x-hidden selection:bg-accent-500">
      {/* Header */}
      <header className="max-w-7xl mx-auto w-full px-6 py-6 flex justify-between items-center border-b border-brand-900">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-accent-600 rounded-xl text-white">
            <BrainCircuit size={22} />
          </div>
          <div>
            <h1 className="font-bold text-base leading-none text-white">SalesAI</h1>
            <span className="text-[10px] text-brand-400 font-medium">Enterprise Analytics</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-xs font-medium text-brand-300 hover:text-white transition-all">
            Sign In
          </Link>
          <Link to="/register" className="px-4 py-2 bg-accent-600 hover:bg-accent-700 active:bg-accent-800 rounded-xl text-xs font-semibold text-white shadow-md shadow-accent-600/10 transition-all">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto w-full px-6 py-20 flex-1 flex flex-col items-center justify-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-brand-900 border border-brand-800 rounded-full text-xs text-accent-500 font-semibold mb-6 animate-pulse">
          <Sparkles size={14} />
          <span>Powered by Groq & Scikit-learn</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-white max-w-4xl leading-tight">
          Turn Spreadsheet Transactions into <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-500 to-blue-400">Actionable Intelligence</span>
        </h1>
        
        <p className="text-sm md:text-base text-brand-400 max-w-2xl mt-6 leading-relaxed">
          Upload your sales records to compute customer segments, model future sales, detect data anomalies, and interrogate your data using our AI assistant.
        </p>

        <div className="flex gap-4 mt-10">
          <Link to="/register" className="flex items-center gap-2 px-6 py-3 bg-accent-600 hover:bg-accent-700 active:bg-accent-800 rounded-xl text-xs font-semibold text-white shadow-lg shadow-accent-600/20 hover:scale-[1.02] transition-all">
            <span>Launch Platform</span>
            <ArrowRight size={16} />
          </Link>
          <a href="#features" className="px-6 py-3 bg-brand-900 border border-brand-800 hover:border-brand-700 rounded-xl text-xs font-semibold text-brand-300 hover:text-white transition-all">
            Learn More
          </a>
        </div>

        {/* Feature Highlights */}
        <section id="features" className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full mt-24 pt-12 border-t border-brand-900">
          {[
            {
              icon: BarChart3,
              title: "Executive Analytics",
              desc: "Fast, accurate Python calculations for RFM scores, growth margins, and category-level product breakdowns."
            },
            {
              icon: ShieldAlert,
              title: "Anomaly Isolation",
              desc: "Locate error entries, suspicious discounts, and unexpected transaction spikes using Isolation Forest."
            },
            {
              icon: ShieldCheck,
              title: "Privacy First design",
              desc: "Data resides in isolated storage. Groq LLM receives only aggregated statistical profiles, never raw spreadsheets."
            }
          ].map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div key={idx} className="glass-panel text-left flex flex-col gap-4">
                <div className="p-3 bg-brand-850 rounded-xl text-accent-500 w-fit">
                  <Icon size={20} />
                </div>
                <h3 className="font-semibold text-sm text-white">{feat.title}</h3>
                <p className="text-xs text-brand-400 leading-relaxed">{feat.desc}</p>
              </div>
            );
          })}
        </section>
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto w-full px-6 py-8 border-t border-brand-900 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-brand-500">
        <p>© 2026 SalesAI Platform. Synthetic sandbox workspace.</p>
        <div className="flex gap-6">
          <a href="#" className="hover:text-brand-300">Privacy Policy</a>
          <a href="#" className="hover:text-brand-300">Terms of Use</a>
          <a href="#" className="hover:text-brand-300">GitHub Codebase</a>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
