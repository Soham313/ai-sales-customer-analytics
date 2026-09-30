import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BrainCircuit, Lock, Mail, User } from 'lucide-react';

const Register: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate registration
    localStorage.setItem('token', 'skeleton-token-jwt');
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-brand-950 flex flex-col justify-center items-center px-4 font-sans text-brand-100">
      <div className="w-full max-w-md bg-brand-900 border border-brand-800 rounded-3xl p-8 shadow-2xl shadow-brand-950/80 glow-purple">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-accent-600 rounded-2xl text-white mb-3">
            <BrainCircuit size={28} />
          </div>
          <h2 className="text-xl font-bold text-white">Create Account</h2>
          <p className="text-xs text-brand-400 mt-1">Get started with SalesAI analytics platform</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-brand-300 mb-1.5">Full Name</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3.5 text-brand-500" size={16} />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                className="w-full pl-11 pr-4 py-3 bg-brand-950 border border-brand-800 rounded-xl text-xs text-white placeholder-brand-600 focus:outline-none focus:border-accent-500 transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-brand-300 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3.5 text-brand-500" size={16} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full pl-11 pr-4 py-3 bg-brand-950 border border-brand-800 rounded-xl text-xs text-white placeholder-brand-600 focus:outline-none focus:border-accent-500 transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-brand-300 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3.5 text-brand-500" size={16} />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-11 pr-4 py-3 bg-brand-950 border border-brand-800 rounded-xl text-xs text-white placeholder-brand-600 focus:outline-none focus:border-accent-500 transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-accent-600 hover:bg-accent-700 active:bg-accent-800 rounded-xl text-xs font-semibold text-white transition-all shadow-md shadow-accent-600/10 mt-2"
          >
            Create Account
          </button>
        </form>

        <p className="text-center text-xs text-brand-400 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-accent-500 hover:text-accent-400 font-semibold">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
