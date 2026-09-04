import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from 'recharts';
import { Brain, Activity, Target } from 'lucide-react';
import { forecastApi } from '../services/api';
import MetricCard from '../components/MetricCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';

const Forecast = () => {
  const { t } = useTranslation();
  const [data, setData] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [forecastData, metricsData] = await Promise.all([
        forecastApi.getForecast(),
        forecastApi.getMetrics()
      ]);
      setData(forecastData);
      setMetrics(metricsData);
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
    </div>
  );
};

export default Forecast;
