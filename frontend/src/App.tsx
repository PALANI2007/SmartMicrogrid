import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Forecast from './pages/Forecast';
import Loads from './pages/Loads';
import Battery from './pages/Battery';
import Scheduler from './pages/Scheduler';
import Comparison from './pages/Comparison';
import Experiments from './pages/Experiments';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';
import Help from './pages/Help';
import EdgeCases from './pages/EdgeCases';
import './i18n';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="forecast" element={<Forecast />} />
          <Route path="loads" element={<Loads />} />
          <Route path="battery" element={<Battery />} />
          <Route path="scheduler" element={<Scheduler />} />
          <Route path="comparison" element={<Comparison />} />
          <Route path="experiments" element={<Experiments />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="settings" element={<Settings />} />
          <Route path="help" element={<Help />} />
          <Route path="edge-cases" element={<EdgeCases />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
