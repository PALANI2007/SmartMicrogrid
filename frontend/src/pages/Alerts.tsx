import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertTriangle, BatteryWarning, Clock, Zap, Play } from 'lucide-react';
import { AlertItem } from '../types';

const Alerts = () => {
  const { t } = useTranslation();
  
  const demoAlerts: AlertItem[] = [
    {
      id: '1', type: 'forecast_error', severity: 'critical',
      title: 'Forecast Error Detected',
      message: 'Actual generation is 40% lower than predicted.',
      details: 'Predicted: 15.2 kW | Actual: 9.1 kW. Caused by unexpected heavy cloud cover.',
      recommendation: 'Scheduler will automatically defer flexible loads to afternoon peak.',
      timestamp: new Date().toISOString(), is_active: true
    },
    {
      id: '2', type: 'low_battery', severity: 'warning',
      title: 'Low Battery Alert',
      message: 'Battery SOC dropping faster than expected.',
      details: 'Current SOC: 22%. Minimum threshold is 20%.',
      recommendation: 'Consider reducing essential load consumption if possible.',
      timestamp: new Date(Date.now() - 3600000).toISOString(), is_active: true
    },
    {
      id: '3', type: 'deadline_conflict', severity: 'critical',
      title: 'Deadline Conflict',
      message: 'Water Pump cannot complete before 16:00 deadline.',
      details: 'Insufficient renewable energy and battery reserved for evening essential loads.',
      recommendation: 'Grid power will be required to meet this deadline. Allow grid usage?',
      timestamp: new Date(Date.now() - 7200000).toISOString(), is_active: true
    }
  ];

  const [activeAlert, setActiveAlert] = useState<AlertItem | null>(null);

  const getIcon = (type: string) => {
    switch(type) {
      case 'forecast_error': return <AlertTriangle size={24} className="text-orange-500" />;
      case 'low_battery': return <BatteryWarning size={24} className="text-red-500" />;
      case 'deadline_conflict': return <Clock size={24} className="text-red-500" />;
      default: return <Zap size={24} className="text-yellow-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">{t('alerts.title')}</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-300 mb-4">Edge Case Simulations</h2>
          
          {demoAlerts.map(alert => (
            <div key={alert.id} className={`card cursor-pointer transition-all border-2 ${activeAlert?.id === alert.id ? 'border-primary-500 bg-slate-800' : 'border-transparent hover:border-slate-600'}`} onClick={() => setActiveAlert(alert)}>
              <div className="flex items-start gap-4">
                <div className="p-2 bg-slate-950 rounded-xl">{getIcon(alert.type)}</div>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <h3 className="font-semibold text-white">{alert.title}</h3>
                    <span className={`text-xs font-bold px-2 py-1 rounded-md ${alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-slate-400 mt-1">{alert.message}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="card bg-slate-900 border-slate-700 h-fit sticky top-24">
          {activeAlert ? (
            <div className="space-y-6">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
                {getIcon(activeAlert.type)}
                <h2 className="text-xl font-bold text-white">{activeAlert.title}</h2>
              </div>
              
              <div>
                <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Details</h4>
                <p className="text-slate-300">{activeAlert.details}</p>
              </div>

              <div className="bg-primary-900/20 border border-primary-500/30 rounded-xl p-4">
                <h4 className="text-sm font-semibold text-primary-400 uppercase tracking-wider mb-2">System Recommendation</h4>
                <p className="text-slate-300">{activeAlert.recommendation}</p>
              </div>

              <button className="btn-primary w-full justify-center mt-4">
                <Play size={18} /> Simulate Resolution
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-slate-500 text-center">
              <Zap size={48} className="mb-4 opacity-50" />
              <p>Select a scenario to view details and simulate resolution.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Alerts;
