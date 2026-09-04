import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Battery as BatteryIcon, BatteryCharging, Zap, Settings2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { batteryApi } from '../services/api';
import { BatteryConfig } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';

const Battery = () => {
  const { t } = useTranslation();
  const [config, setConfig] = useState<BatteryConfig | null>(null);
  const [simulation, setSimulation] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<any>({});

  const loadData = async () => {
    try {
      setLoading(true);
      const [batteryData, simData] = await Promise.all([
        batteryApi.getBattery(),
        batteryApi.getSimulation()
      ]);
      setConfig(batteryData);
      setFormData(batteryData);
      setSimulation(simData);
    } catch (err) {
      setError(String(err) || 'Failed to load battery data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      const updated = await batteryApi.updateBattery(formData);
      setConfig(updated);
      setFormData(updated);
      const simData = await batteryApi.getSimulation();
      setSimulation(simData);
    } catch (err) {
      setError(String(err) || 'Failed to update battery config');
    } finally {
      setSaving(false);
    }
  };

  if (loading && !config) return <LoadingSpinner />;

  const getBatteryColor = (soc: number) => {
    if (soc > 60) return 'text-green-500';
    if (soc > 30) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">{t('battery.title')}</h1>
      </div>

      {error && <ErrorAlert message={error} />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-1 flex flex-col items-center justify-center py-8">
          <div className="relative w-48 h-48 flex items-center justify-center mb-4">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="10" />
              <circle 
                cx="50" cy="50" r="45" fill="none" 
                stroke={config?.current_soc && config.current_soc > 30 ? (config.current_soc > 60 ? '#22c55e' : '#eab308') : '#ef4444'} 
                strokeWidth="10" 
                strokeDasharray={`${(config?.current_soc || 0) * 2.83} 283`}
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <BatteryCharging className={getBatteryColor(config?.current_soc || 0)} size={32} />
              <span className="text-3xl font-bold text-white mt-2">{config?.current_soc.toFixed(1)}%</span>
            </div>
          </div>
          <h3 className="text-xl font-semibold text-slate-300">{t('battery.currentSoc')}</h3>
          <p className="text-slate-500 mt-2">{config?.capacity_kwh} {t('common.kwh')} {t('battery.capacity')}</p>
        </div>

        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Settings2 size={20} className="text-primary-400" />
            {t('battery.update')}
          </h3>
          <form onSubmit={handleUpdate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">{t('battery.capacity')}</label>
              <input type="number" step="0.1" className="input-field" value={formData.capacity_kwh || ''} onChange={e => setFormData({...formData, capacity_kwh: parseFloat(e.target.value)})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">{t('battery.minSoc')}</label>
              <input type="number" step="1" className="input-field" value={formData.minimum_soc || ''} onChange={e => setFormData({...formData, minimum_soc: parseFloat(e.target.value)})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">{t('battery.maxSoc')}</label>
              <input type="number" step="1" className="input-field" value={formData.maximum_soc || ''} onChange={e => setFormData({...formData, maximum_soc: parseFloat(e.target.value)})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">{t('battery.maxCharge')}</label>
              <input type="number" step="0.1" className="input-field" value={formData.max_charge_kw || ''} onChange={e => setFormData({...formData, max_charge_kw: parseFloat(e.target.value)})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">{t('battery.maxDischarge')}</label>
              <input type="number" step="0.1" className="input-field" value={formData.max_discharge_kw || ''} onChange={e => setFormData({...formData, max_discharge_kw: parseFloat(e.target.value)})} />
            </div>
            <div className="md:col-span-2 flex justify-end mt-4">
              <button type="submit" className="btn-primary" disabled={saving}>
                {saving ? t('common.loading') : t('common.save')}
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">SOC Simulation</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={simulation}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="hour" stroke="#94a3b8" />
              <YAxis domain={[0, 100]} stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
              <ReferenceLine y={config?.minimum_soc} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Min SOC', fill: '#ef4444' }} />
              <ReferenceLine y={config?.maximum_soc} stroke="#22c55e" strokeDasharray="3 3" label={{ position: 'insideBottomLeft', value: 'Max SOC', fill: '#22c55e' }} />
              <Line type="monotone" dataKey="soc" stroke="#3b82f6" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Battery;
