import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from 'recharts';
import { Brain, Activity, Target } from 'lucide-react';
import { forecastApi, forecastErrorsApi } from '../services/api';
import MetricCard from '../components/MetricCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';

const Forecast = () => {
  const { t } = useTranslation();
  const [data, setData] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [errorData, setErrorData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [forecastData, metricsData, errDist] = await Promise.all([
        forecastApi.getForecast(),
        forecastApi.getMetrics(),
        // Non-critical: gracefully degrades to null if /api/forecast/errors is not yet available
        // (e.g. model not yet trained or endpoint not deployed). Does not block the rest of the data load.
        forecastErrorsApi.getErrorDistribution().catch(() => null),
      ]);
      setData(forecastData);
      setMetrics(metricsData);
      setErrorData(errDist);
    } catch (err) {
      setError(String(err) || 'Failed to load forecast data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTrain = async () => {
    try {
      setTraining(true);
      await forecastApi.trainModel();
      await loadData();
    } catch (err) {
      setError(String(err) || 'Failed to train model');
    } finally {
      setTraining(false);
    }
  };

  if (loading && !data.length) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">{t('forecast.title')}</h1>
        <button onClick={handleTrain} disabled={training} className="btn-primary">
          <Brain size={18} className={training ? 'animate-pulse' : ''} />
          {training ? 'Training...' : t('forecast.trainModel')}
        </button>
      </div>

      {error && <ErrorAlert message={error} />}

      {metrics && metrics.model && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard title={t('forecast.mae') + ' (ML)'} value={metrics.model.mae.toFixed(2)} unit="kW" icon={<Activity size={24} />} />
          <MetricCard title={t('forecast.rmse') + ' (ML)'} value={metrics.model.rmse.toFixed(2)} unit="kW" icon={<Target size={24} />} />
          <MetricCard title={t('forecast.r2') + ' (ML)'} value={metrics.model.r2.toFixed(2)} icon={<Brain size={24} />} />
        </div>
      )}

      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Generation Forecast</h2>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="hour" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
              <Legend />
              <Area type="monotone" dataKey="upper_bound_kw" fill="#ca8a04" stroke="none" fillOpacity={0.1} name="Upper Bound" />
              <Area type="monotone" dataKey="lower_bound_kw" fill="#0f172a" stroke="none" fillOpacity={1} name="Lower Bound" />
              <Line type="monotone" dataKey="predicted_generation_kw" stroke="#eab308" strokeWidth={2} strokeDasharray="5 5" name="Predicted" />
              <Line type="monotone" dataKey="actual_generation_kw" stroke="#3b82f6" strokeWidth={2} name="Actual" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card bg-slate-900/50">
          <h3 className="font-medium text-white mb-2">{t('forecast.forecastUncertainty')}</h3>
          <p className="text-sm text-slate-400">
            The shaded area represents the 95% confidence interval for the predicted solar generation. Wider intervals indicate higher uncertainty in the prediction, usually occurring during periods of highly variable weather. The scheduler takes this uncertainty into account when making robust decisions.
          </p>
        </div>
      </div>

      {/* Empirical Forecast Error Distribution */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-white">Empirical Forecast Error Distribution (test period)</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-xs text-slate-400 mb-1">Mean Error</p>
            <p className="text-sm font-semibold text-white">{errorData?.mean_error?.toFixed(4) ?? 'N/A'} kW</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-xs text-slate-400 mb-1">Std</p>
            <p className="text-sm font-semibold text-white">{errorData?.std_error?.toFixed(4) ?? 'N/A'} kW</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-xs text-slate-400 mb-1">MAE</p>
            <p className="text-sm font-semibold text-white">{errorData?.mae?.toFixed(4) ?? 'N/A'} kW</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-xs text-slate-400 mb-1">P90 Abs Error</p>
            <p className="text-sm font-semibold text-white">{errorData?.percentiles?.p90?.toFixed(4) ?? 'N/A'} kW</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-xs text-slate-400 mb-1">Test Samples</p>
            <p className="text-sm font-semibold text-white">{errorData?.n_test_samples ?? 'N/A'}</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-xs text-slate-400 mb-1">Test Period</p>
            <p className="text-sm font-semibold text-white">
              {errorData?.test_period_start?.substring(0, 10) ?? 'N/A'} to {errorData?.test_period_end?.substring(0, 10) ?? 'N/A'}
            </p>
          </div>
        </div>
        <p className="text-xs text-slate-500 italic">
          Uncertainty bounds use ±1.645 × tree-prediction std (empirical interval, not a guaranteed CI).
        </p>
      </div>

      {/* Model vs Baseline Comparison Table:
          Compares the trained Random Forest (RF) model against a naive "last-value" baseline.
          Lower MAE/RMSE and higher R² in the RF column confirms the ML model outperforms the baseline. */}
      {metrics && metrics.model && metrics.baseline && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Model vs Naive Baseline</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-2 px-3 text-slate-400 font-medium">Metric</th>
                  <th className="text-right py-2 px-3 text-slate-400 font-medium">Random Forest</th>
                  <th className="text-right py-2 px-3 text-slate-400 font-medium">Naive Baseline</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                <tr>
                  <td className="py-2 px-3 text-slate-300">MAE</td>
                  <td className="py-2 px-3 text-right text-white font-mono">{metrics?.model?.mae?.toFixed(4)}</td>
                  <td className="py-2 px-3 text-right text-slate-400 font-mono">{metrics?.baseline?.mae?.toFixed(4)}</td>
                </tr>
                <tr>
                  <td className="py-2 px-3 text-slate-300">RMSE</td>
                  <td className="py-2 px-3 text-right text-white font-mono">{metrics?.model?.rmse?.toFixed(4)}</td>
                  <td className="py-2 px-3 text-right text-slate-400 font-mono">{metrics?.baseline?.rmse?.toFixed(4)}</td>
                </tr>
                <tr>
                  <td className="py-2 px-3 text-slate-300">R²</td>
                  <td className="py-2 px-3 text-right text-white font-mono">{metrics?.model?.r2?.toFixed(4)}</td>
                  <td className="py-2 px-3 text-right text-slate-400 font-mono">{metrics?.baseline?.r2?.toFixed(4)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Forecast;
