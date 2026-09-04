import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ArrowRightLeft, TrendingUp, TrendingDown } from 'lucide-react';
import { baselineApi, schedulerApi } from '../services/api';
import { ScheduleMetrics } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';

const Comparison = () => {
  const { t } = useTranslation();
  const [baseline, setBaseline] = useState<ScheduleMetrics | null>(null);
  const [smart, setSmart] = useState<ScheduleMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const runComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const [baseResult, smartResult] = await Promise.all([
        baselineApi.runBaseline(date),
        schedulerApi.runSchedule(date)
      ]);
      setBaseline(baseResult.metrics);
      setSmart(smartResult.metrics);
    } catch (err) {
      setError(String(err) || 'Failed to run comparison');
    } finally {
      setLoading(false);
    }
  };

  const calculateImprovement = (baseVal: number | undefined, smartVal: number | undefined, higherIsBetter: boolean) => {
    if (baseVal === undefined || smartVal === undefined) return { value: 0, text: 'N/A', isPositive: true };
    if (baseVal === 0) return { value: 0, text: 'N/A', isPositive: true };
    const diff = higherIsBetter ? smartVal - baseVal : baseVal - smartVal;
    const pct = (diff / baseVal) * 100;
    return {
      value: pct,
      text: `${pct > 0 ? '+' : ''}${pct.toFixed(1)}%`,
      isPositive: pct > 0
    };
  };

  const chartData = baseline && smart ? [
    { name: 'Self-Consumption %', Baseline: baseline.renewable_self_consumption_pct || 0, Smart: smart.renewable_self_consumption_pct || 0 },
    { name: 'Grid Energy (kWh)', Baseline: baseline.grid_energy_kwh || 0, Smart: smart.grid_energy_kwh || 0 },
    { name: 'Renewable Export', Baseline: baseline.renewable_export_kwh || 0, Smart: smart.renewable_export_kwh || 0 }
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-white">{t('comparison.title')}</h1>
        <div className="flex items-center gap-3">
          <input type="date" className="input-field max-w-[200px]" value={date} onChange={(e) => setDate(e.target.value)} />
          <button onClick={runComparison} disabled={loading} className="btn-primary">
            <ArrowRightLeft size={18} className={loading ? 'animate-spin' : ''} /> {t('comparison.runComparison')}
          </button>
        </div>
      </div>

      {error && <ErrorAlert message={error} />}
      {loading && <LoadingSpinner />}

      {!loading && baseline && smart && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: t('comparison.selfConsumption'), base: baseline.renewable_self_consumption_pct || 0, smart: smart.renewable_self_consumption_pct || 0, unit: '%', higherBetter: true },
              { label: t('comparison.gridEnergy'), base: baseline.grid_energy_kwh || 0, smart: smart.grid_energy_kwh || 0, unit: 'kWh', higherBetter: false },
              { label: t('comparison.deadlineViolations'), base: baseline.deadline_violations || 0, smart: smart.deadline_violations || 0, unit: '', higherBetter: false },
              { label: t('comparison.userDisruption'), base: (baseline as any).user_disruption_score || 0, smart: (smart as any).user_disruption_score || 0, unit: '', higherBetter: false },
            ].map((m, i) => {
              const imp = calculateImprovement(m.base, m.smart, m.higherBetter);
              return (
                <div key={i} className="card p-5">
                  <h3 className="text-slate-400 text-sm font-medium mb-3">{m.label}</h3>
                  <div className="flex justify-between items-end">
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Baseline</div>
                      <div className="text-lg font-semibold text-slate-300">{m.base?.toFixed(1) ?? 'N/A'} {m.unit}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Smart</div>
                      <div className="text-xl font-bold text-white">{m.smart?.toFixed(1) ?? 'N/A'} {m.unit}</div>
                    </div>
                  </div>
                  <div className={`mt-3 pt-3 border-t border-slate-800 flex items-center justify-between ${imp.isPositive ? 'text-green-400' : (imp.value === 0 ? 'text-slate-400' : 'text-red-400')}`}>
                    <span className="text-xs font-medium uppercase tracking-wider">{t('comparison.improvement')}</span>
                    <div className="flex items-center gap-1 font-bold">
                      {imp.isPositive ? <TrendingUp size={16} /> : (imp.value !== 0 ? <TrendingDown size={16} /> : null)}
                      {imp.text}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-white mb-6">Metrics Comparison</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                  <Legend />
                  <Bar dataKey="Baseline" fill="#64748b" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Smart" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Comparison;
