import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Sun, Zap, Battery as BatteryIcon, RefreshCw, Activity, ArrowDownToLine, Plug } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend, ComposedChart } from 'recharts';
import { dashboardApi } from '../services/api';
import { DashboardData } from '../types';
import MetricCard from '../components/MetricCard';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';

const Dashboard = () => {
  const { t } = useTranslation();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await dashboardApi.getDashboard();
      setData(result);
      setError(null);
    } catch (err) {
      setError(String(err) || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) return <LoadingSpinner />;
  if (error) return <ErrorAlert message={error} />;
  if (!data) return null;

  const pieData = [
    { name: t('dashboard.selfConsumption'), value: data.renewable_self_consumption_pct, color: '#0ea5e9' },
    { name: t('dashboard.gridDependency'), value: data.grid_dependency_pct, color: '#ef4444' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">{t('dashboard.title')}</h1>
        <div className="flex items-center gap-4">
          <StatusBadge status={data.system_status} text={t(`dashboard.${data.system_status.toLowerCase()}`)} />
          <button onClick={fetchData} aria-label={t('dashboard.refreshData')} className="p-2 text-slate-400 hover:text-white rounded-full hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500">
            <RefreshCw size={20} className={loading ? 'animate-spin' : ''} aria-hidden="true" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard title={t('dashboard.currentSolar')} value={data.current_solar_kw.toFixed(1)} unit="kW" icon={<Sun size={24} />} color="solar" />
        <MetricCard title={t('dashboard.totalLoad')} value={data.total_load_kw.toFixed(1)} unit="kW" icon={<Zap size={24} />} color="grid" />
        <MetricCard title={t('dashboard.batterySoc')} value={data.battery_soc.toFixed(1)} unit="%" icon={<BatteryIcon size={24} />} color="battery" />
        <MetricCard title={t('dashboard.selfConsumption')} value={data.renewable_self_consumption_pct.toFixed(1)} unit="%" icon={<Activity size={24} />} color="primary" />
        <MetricCard title={t('dashboard.renewableExport')} value={data.renewable_export_kwh.toFixed(1)} unit="kWh" icon={<ArrowDownToLine size={24} />} color="solar" />
        <MetricCard title={t('dashboard.gridDependency')} value={data.grid_dependency_pct.toFixed(1)} unit="%" icon={<Plug size={24} />} color="grid" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <h2 className="text-lg font-semibold text-white mb-4">Solar & Load Profile</h2>
          <div className="h-72" aria-label="Line chart showing solar generation versus load over 24 hours" tabIndex={0}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={data.hourly_data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="hour" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                <Legend />
                <Area type="monotone" dataKey="solar_kw" name="Solar (kW)" fill="#eab308" stroke="#ca8a04" fillOpacity={0.3} />
                <Line type="monotone" dataKey="load_kw" name="Load (kW)" stroke="#ef4444" strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Energy Mix</h2>
          <div className="h-72 flex items-center justify-center" aria-label="Pie chart showing energy mix between self-consumption and grid dependency" tabIndex={0}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="card">
         <h2 className="text-lg font-semibold text-white mb-4">{t('dashboard.activeLoads')}</h2>
         <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
               <thead className="bg-slate-800/50 text-slate-400">
                  <tr>
                     <th className="px-4 py-3 rounded-tl-lg">Name</th>
                     <th className="px-4 py-3">Type</th>
                     <th className="px-4 py-3">Power</th>
                     <th className="px-4 py-3 rounded-tr-lg">Priority</th>
                  </tr>
               </thead>
               <tbody className="divide-y divide-slate-700/50">
                  {data.active_loads?.map((load) => (
                     <tr key={load.id} className="hover:bg-slate-800/30">
                        <td className="px-4 py-3 font-medium text-white">{load.name}</td>
                        <td className="px-4 py-3"><StatusBadge status={load.load_type === 'essential' ? 'GOOD' : 'SCHEDULED'} text={load.load_type} /></td>
                        <td className="px-4 py-3">{load.power_kw} kW</td>
                        <td className="px-4 py-3"><span className={`badge-${load.priority}`}>{load.priority}</span></td>
                     </tr>
                  ))}
               </tbody>
            </table>
         </div>
      </div>
    </div>
  );
};

export default Dashboard;
