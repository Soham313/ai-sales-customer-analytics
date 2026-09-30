import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, User, Bot, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

const SAMPLE_PROMPTS = [
  "Which region performed best in revenue?",
  "What is our overall profit margin?",
  "Which customer group is currently at risk?",
  "What is the sales forecast for the next 30 days?",
  "Were any anomalies detected in our sales?"
];

const AiAnalyst: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'ai',
      text: "Hello! I am your AI Business Analyst. I explain the exact pre-calculated metrics computed by our Python analytics engine. What business question can I answer for you today?"
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeDatasetId, setActiveDatasetId] = useState<number | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load dataset id
    api.get('/datasets').then((res) => {
      const active = res.data.find((d: any) => d.status === 'mapped') || res.data[0];
      if (active) setActiveDatasetId(active.id);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || !activeDatasetId) return;

    // Add user message
    setMessages((prev) => [...prev, { sender: 'user', text: textToSend }]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const res = await api.post('/ai/chat', {
        dataset_id: activeDatasetId,
        query: textToSend
      });

      setMessages((prev) => [...prev, { sender: 'ai', text: res.data.response }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { sender: 'ai', text: `Error: ${err.response?.data?.detail || 'Failed to communicate with AI analyst.'}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-8rem)]">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">AI Business Analyst</h1>
        <p className="text-xs text-brand-400 mt-1">Interrogate pre-calculated metrics using natural language questions.</p>
      </div>

      {/* Suggested Prompts Pill Container */}
      <div className="flex flex-wrap gap-2">
        {SAMPLE_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="px-3 py-1.5 bg-brand-900 border border-brand-800 hover:border-accent-500/50 text-[11px] text-brand-300 hover:text-white rounded-full transition-all flex items-center gap-1.5"
          >
            <Sparkles size={12} className="text-accent-500" />
            <span>{prompt}</span>
          </button>
        ))}
      </div>

      {/* Main Chat Box */}
      <div className="flex-1 glass-panel flex flex-col justify-between overflow-hidden p-0">
        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 max-w-3xl ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-white shrink-0 ${
                  msg.sender === 'user' ? 'bg-accent-600' : 'bg-brand-800 text-accent-400'
                }`}
              >
                {msg.sender === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>

              <div
                className={`rounded-2xl p-4 text-xs leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-accent-600 text-white font-medium'
                    : 'bg-brand-950 border border-brand-800 text-brand-200 whitespace-pre-wrap'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 max-w-3xl">
              <div className="w-8 h-8 rounded-full bg-brand-800 text-accent-400 flex items-center justify-center shrink-0">
                <Bot size={16} />
              </div>
              <div className="bg-brand-950 border border-brand-800 rounded-2xl p-4 text-xs text-brand-400 flex items-center gap-2">
                <RefreshCw size={14} className="animate-spin text-accent-500" />
                <span>Running Python analytics & consulting AI reasoning layer...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-brand-800 bg-brand-950/60">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-3"
          >
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask any question about your sales, regions, or customers..."
              className="flex-1 bg-brand-900 border border-brand-800 rounded-xl px-4 py-3 text-xs text-white placeholder-brand-500 focus:outline-none focus:border-accent-500 transition-all"
            />
            <button
              type="submit"
              disabled={loading || !inputQuery.trim()}
              className="px-5 py-3 bg-accent-600 hover:bg-accent-700 active:bg-accent-800 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shadow-md shadow-accent-600/10"
            >
              <span>Ask AI</span>
              <Send size={14} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AiAnalyst;
