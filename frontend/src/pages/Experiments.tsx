import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Play, Download, FileText } from 'lucide-react';
import { experimentsApi } from '../services/api';
import { ExperimentResult } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';

const Experiments = () => {
  const { t } = useTranslation();
  const [results, setResults] = useState<ExperimentResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({ name: '', date: new Date().toISOString().split('T')[0] });

  const fetchResults = async () => {
    try {
      setLoading(true);
      const data = await experimentsApi.getResults();
      setResults(data);
    } catch (err) {
      setError(String(err) || 'Failed to fetch experiment results');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchResults(); }, []);

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setRunning(true);
      setError(null);
      await experimentsApi.runExperiment(formData);
      await fetchResults();
      setFormData({ ...formData, name: '' });
    } catch (err) {
      setError(String(err) || 'Failed to run experiment');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">{t('experiments.title')}</h1>
      </div>

      {error && <ErrorAlert message={error} />}

      <div className="card max-w-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">New Experiment</h2>
        <form onSubmit={handleRun} className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="flex-1 w-full">
            <label className="block text-sm font-medium text-slate-300 mb-1">{t('experiments.experimentName')}</label>
            <input type="text" required className="input-field" placeholder="e.g., Summer Peak Test" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
          </div>
          <div className="w-full sm:w-auto">
            <label className="block text-sm font-medium text-slate-300 mb-1">Date</label>
            <input type="date" required className="input-field" value={formData.date} onChange={e => setFormData({...formData, date: e.target.value})} />
          </div>
          <button type="submit" disabled={running} className="btn-primary w-full sm:w-auto">
            <Play size={18} className={running ? 'animate-pulse' : ''} /> {running ? 'Running...' : t('experiments.runExperiment')}
          </button>
        </form>
      </div>

      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-white">{t('experiments.results')}</h2>
          <button className="btn-secondary text-sm py-1.5"><Download size={16} /> {t('experiments.downloadCSV')}</button>
        </div>

        {loading ? <LoadingSpinner /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/50 text-slate-400 border-b border-slate-700">
                <tr>
                  <th className="px-4 py-3">Experiment</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Self-Consumption</th>
                  <th className="px-4 py-3">Grid Energy</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {results.length === 0 ? (
                  <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">No experiments run yet.</td></tr>
                ) : results.map((res, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="px-4 py-3 font-medium text-white">{res.experiment_name}</td>
                    <td className="px-4 py-3 text-slate-400">{new Date(res.created_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-green-400">{(res as any).renewable_self_consumption_pct?.toFixed(1) ?? '0.0'}%</td>
                    <td className="px-4 py-3 text-green-400">{(res as any).grid_energy_kwh?.toFixed(1) ?? '0.0'} kWh</td>
                    <td className="px-4 py-3 flex justify-end gap-2">
                      <button className="p-1.5 text-primary-400 hover:text-primary-300 hover:bg-primary-900/20 rounded-lg">
                        <FileText size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Experiments;
