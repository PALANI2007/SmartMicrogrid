import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Play, Calendar as CalendarIcon, Info } from 'lucide-react';
import { schedulerApi } from '../services/api';
import { ScheduleResult } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import StatusBadge from '../components/StatusBadge';
import EmptyState from '../components/EmptyState';

const Scheduler = () => {
  const { t } = useTranslation();
  const [result, setResult] = useState<ScheduleResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchLatest = async () => {
    try {
      setLoading(true);
      const data = await schedulerApi.getLatest();
      setResult(data);
    } catch (err) {
      if (err !== 'No smart schedule results found.') {
        setError(String(err) || 'Failed to fetch latest schedule');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLatest(); }, []);

  const handleRun = async () => {
    try {
      setRunning(true);
      setError(null);
      const data = await schedulerApi.runSchedule(date);
      setResult(data);
    } catch (err) {
      setError(String(err) || 'Failed to run scheduler');
    } finally {
      setRunning(false);
    }
  };

  // Helper to calculate timeline bar styles
  const getTimelineStyle = (start: string, duration: number) => {
    const [h, m] = start.split(':').map(Number);
    const startOffset = (h + m / 60) / 24 * 100;
    const width = (duration / 24) * 100;
    return { left: `${startOffset}%`, width: `${width}%` };
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-white">{t('scheduler.title')}</h1>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <input 
            type="date" 
            className="input-field max-w-[200px]" 
            value={date} 
            onChange={(e) => setDate(e.target.value)} 
          />
          <button onClick={handleRun} disabled={running} className="btn-primary w-full sm:w-auto">
            {running ? <><div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" /> {t('scheduler.running')}</> : <><Play size={18} /> {t('scheduler.runSchedule')}</>}
          </button>
        </div>
      </div>

      {error && <ErrorAlert message={error} />}
      {loading && !result && <LoadingSpinner />}
      
      {!loading && !result && !error && (
        <EmptyState message="No schedule generated yet. Click 'Generate Smart Schedule' to create one." />
      )}

      {result && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="stat-card">
              <h3 className="text-slate-400 text-sm font-medium">{t('comparison.selfConsumption')}</h3>
              <span className="text-2xl font-bold text-white">{result.metrics?.renewable_self_consumption_pct?.toFixed(1) ?? 'N/A'}%</span>
            </div>
            <div className="stat-card">
              <h3 className="text-slate-400 text-sm font-medium">{t('comparison.export')}</h3>
              <span className="text-2xl font-bold text-white">{result.metrics?.renewable_export_kwh?.toFixed(1) ?? 'N/A'} kWh</span>
            </div>
            <div className="stat-card">
              <h3 className="text-slate-400 text-sm font-medium">{t('comparison.gridEnergy')}</h3>
              <span className="text-2xl font-bold text-white">{result.metrics?.grid_energy_kwh?.toFixed(1) ?? 'N/A'} kWh</span>
            </div>
            <div className="stat-card">
              <h3 className="text-slate-400 text-sm font-medium">{t('comparison.deadlineViolations')}</h3>
              <span className="text-2xl font-bold text-white">{result.metrics?.deadline_violations ?? 'N/A'}</span>
            </div>
          </div>

          <div className="card overflow-hidden">
            <h2 className="text-lg font-semibold text-white mb-6">Schedule Timeline</h2>
            <div className="relative pt-6 pb-2">
              <div className="absolute top-0 left-0 w-full flex justify-between text-xs text-slate-500 px-2">
                {[0,4,8,12,16,20,24].map(h => (
                  <span key={h} className="w-8 text-center" style={{ position: 'absolute', left: `calc(${(h/24)*100}% - 16px)` }}>
                    {h.toString().padStart(2, '0')}:00
                  </span>
                ))}
              </div>
              
              <div className="mt-4 space-y-3">
                {result.schedule.map((entry, idx) => {
                  if (entry.status !== 'SCHEDULED') return null;
                  const isEssential = entry.load_type === 'essential';
                  return (
                    <div key={idx} className="relative h-10 bg-slate-800/50 rounded-lg group">
                      <div className="absolute inset-0 flex items-center px-3 z-10 w-48 truncate">
                        <span className="text-sm font-medium text-slate-300">{entry.load_name}</span>
                      </div>
                      <div 
                        className={`absolute h-full rounded-lg transition-all duration-300 cursor-pointer flex items-center justify-center overflow-hidden whitespace-nowrap px-2 text-xs font-semibold
                          ${isEssential ? 'bg-red-500/80 hover:bg-red-400 border border-red-400' : 'bg-blue-500/80 hover:bg-blue-400 border border-blue-400'}`}
                        style={getTimelineStyle(entry.scheduled_start, entry.duration_hours)}
                        title={`${entry.load_name}: ${entry.scheduled_start} - ${entry.scheduled_end}`}
                      >
                        {entry.power_kw}kW
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-white mb-4">Detailed Results</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/50 text-slate-400 border-b border-slate-700">
                  <tr>
                    <th className="px-4 py-3">{t('scheduler.load')}</th>
                    <th className="px-4 py-3">{t('scheduler.start')} - {t('scheduler.end')}</th>
                    <th className="px-4 py-3">{t('scheduler.status')}</th>
                    <th className="px-4 py-3">{t('scheduler.explanation')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {result.schedule.map((entry, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30">
                      <td className="px-4 py-3">
                        <div className="font-medium text-white">{entry.load_name}</div>
                        <div className="text-xs text-slate-500">{entry.load_type} • {entry.power_kw}kW</div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        {entry.scheduled_start} - {entry.scheduled_end}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={entry.status} text={t(`scheduler.${entry.status.toLowerCase()}`)} />
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-400 max-w-xs">
                        <div className="flex items-start gap-2">
                          <Info size={14} className="mt-0.5 shrink-0" />
                          <span>{entry.explanation}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Scheduler;
