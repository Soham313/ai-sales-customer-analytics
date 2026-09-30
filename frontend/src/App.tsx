import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Sales from './pages/Sales';
import Customers from './pages/Customers';
import Products from './pages/Products';
import Forecast from './pages/Forecast';
import Anomalies from './pages/Anomalies';
import AiAnalyst from './pages/AiAnalyst';
import Datasets from './pages/Datasets';
import Settings from './pages/Settings';
import { SidebarLayout } from './components/common/SidebarLayout';

// Simple Route Protection wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <SidebarLayout>{children}</SidebarLayout>;
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Dashboard Routes */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/sales" element={<ProtectedRoute><Sales /></ProtectedRoute>} />
        <Route path="/customers" element={<ProtectedRoute><Customers /></ProtectedRoute>} />
        <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
        <Route path="/forecast" element={<ProtectedRoute><Forecast /></ProtectedRoute>} />
        <Route path="/anomalies" element={<ProtectedRoute><Anomalies /></ProtectedRoute>} />
        <Route path="/ai-analyst" element={<ProtectedRoute><AiAnalyst /></ProtectedRoute>} />
        <Route path="/datasets" element={<ProtectedRoute><Datasets /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
