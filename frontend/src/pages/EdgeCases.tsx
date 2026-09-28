import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TriangleAlert } from 'lucide-react';
import { edgeCasesApi } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';

interface SmartMetrics {
  renewable_self_consumption_pct?: number;
  grid_energy_kwh?: number;
  deadline_violations?: number;
  [key: string]: any;
}

interface EdgeCaseResult {
  id?: number;
  scenario_id: string;
  name?: string;
  scenario_name?: string;
  status: 'PASS' | 'FAIL';
  expected_behavior: string;
  actual_behavior?: string;
  smart_metrics?: SmartMetrics;
  violations?: string[];
  explanation?: string;
}

const StatusBadge = ({ status }: { status: 'PASS' | 'FAIL' }) => (
  <span
    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
      status === 'PASS'
        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
        : 'bg-red-500/20 text-red-400 border border-red-500/30'
    }`}
  >
    {status}
  </span>
);

const EdgeCases = () => {
  const { t } = useTranslation();
  const [results, setResults] = useState<EdgeCaseResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await edgeCasesApi.getResults();
      setResults(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(String(err) || 'Failed to load edge case results');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResults();
  }, []);

  const handleRunAll = async () => {
    try {
      setRunning(true);
      setError(null);
      await edgeCasesApi.runAll('all');
      await loadResults();
    } catch (err) {
      setError(String(err) || 'Failed to run edge cases');
    } finally {
      setRunning(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">{t('edgeCases.title')}</h1>
        <button
          onClick={handleRunAll}
          disabled={running}
          className="btn-primary flex items-center gap-2"
        >
          <TriangleAlert size={18} className={running ? 'animate-pulse' : ''} />
          {running ? t('edgeCases.running') : t('edgeCases.runAll')}
        </button>
      </div>

      {error && <ErrorAlert message={error} />}

      {results.length === 0 && !error && (
        <div className="card text-center py-12">
          <TriangleAlert size={48} className="mx-auto text-slate-500 mb-4" />
          <p className="text-slate-400">{t('edgeCases.noResults')}</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {results.map((result, idx) => (
            <div key={result.id ? `edge-case-${result.id}` : `edge-case-${result.scenario_id}-${idx}`} className="card space-y-4">
              <div className="flex items-start justify-between gap-3">
                <h2 className="text-lg font-semibold text-white leading-tight">
                  {result.name || result.scenario_name || result.scenario_id}
                </h2>
                <StatusBadge status={result.status} />
              </div>

              {result.expected_behavior && (
                <div>
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">
                    {t('edgeCases.expected')}
                  </p>
                  <p className="text-sm text-slate-300">{result.expected_behavior}</p>
                </div>
              )}

              {result.actual_behavior && (
                <div>
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">
                    {t('edgeCases.actual')}
                  </p>
                  <p className="text-sm text-slate-300">{result.actual_behavior}</p>
                </div>
              )}

              {result.smart_metrics && (
                <div>
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-2">
                    {t('edgeCases.metrics')}
                  </p>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                      <p className="text-xs text-slate-400 mb-0.5">Self-Consumption</p>
                      <p className="text-sm font-semibold text-white">
                        {result.smart_metrics.renewable_self_consumption_pct != null
                          ? `${result.smart_metrics.renewable_self_consumption_pct.toFixed(1)}%`
                          : 'N/A'}
                      </p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                      <p className="text-xs text-slate-400 mb-0.5">Grid Energy</p>
                      <p className="text-sm font-semibold text-white">
                        {result.smart_metrics.grid_energy_kwh != null
                          ? `${result.smart_metrics.grid_energy_kwh.toFixed(2)} kWh`
                          : 'N/A'}
                      </p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                      <p className="text-xs text-slate-400 mb-0.5">Deadline Violations</p>
                      <p className={`text-sm font-semibold ${
                        (result.smart_metrics.deadline_violations ?? 0) > 0
                          ? 'text-red-400'
                          : 'text-green-400'
                      }`}>
                        {result.smart_metrics.deadline_violations ?? 0}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {(() => {
                const viols: string[] = [];
                if (Array.isArray(result.violations)) {
                  viols.push(...result.violations);
                } else if (result.violations && typeof result.violations === 'object') {
                  const vDict = result.violations as Record<string, any>;
                  if (vDict.essential > 0) viols.push(`Essential Load Violations: ${vDict.essential}`);
                  if (vDict.deadline > 0) viols.push(`Deadline Violations: ${vDict.deadline}`);
                  if (vDict.battery) viols.push(`Battery Minimum Reserve Violated`);
                }
                if (viols.length === 0) return null;
                return (
                  <div>
                    <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">
                      {t('edgeCases.violations')}
                    </p>
                    <ul className="space-y-1">
                      {viols.map((v, idx) => (
                        <li key={idx} className="text-sm text-red-300 flex items-start gap-1.5">
                          <span className="mt-1 shrink-0 w-1.5 h-1.5 rounded-full bg-red-400 inline-block" />
                          {v}
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })()}

              {result.explanation && (
                <div className="border-t border-slate-700 pt-3">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">
                    {t('edgeCases.explanation')}
                  </p>
                  <p className="text-sm text-slate-300 italic">{result.explanation}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EdgeCases;