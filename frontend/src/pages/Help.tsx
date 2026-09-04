import React from 'react';
import { useTranslation } from 'react-i18next';
import { Book, HelpCircle, Lightbulb, ShieldAlert } from 'lucide-react';

const Help = () => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-white">{t('help.title')}</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Book size={20} className="text-primary-400" /> Getting Started</h2>
          <ul className="space-y-3 text-slate-300 text-sm">
            <li className="flex items-start gap-2">
              <span className="bg-primary-600 text-white rounded-full w-5 h-5 flex items-center justify-center shrink-0 mt-0.5">1</span>
              <p>Navigate to <strong>Load Management</strong> to add your household appliances.</p>
            </li>
            <li className="flex items-start gap-2">
              <span className="bg-primary-600 text-white rounded-full w-5 h-5 flex items-center justify-center shrink-0 mt-0.5">2</span>
              <p>Configure your battery specs in the <strong>Battery</strong> tab.</p>
            </li>
            <li className="flex items-start gap-2">
              <span className="bg-primary-600 text-white rounded-full w-5 h-5 flex items-center justify-center shrink-0 mt-0.5">3</span>
              <p>Go to <strong>Smart Scheduler</strong> and click generate to create an optimized daily plan.</p>
            </li>
          </ul>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Lightbulb size={20} className="text-yellow-400" /> Key Concepts</h2>
          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-semibold text-slate-200">Essential vs Flexible Loads</h4>
              <p className="text-slate-400 mt-1">Essential loads cannot be interrupted (e.g. Fridge). Flexible loads can be shifted to match solar peaks (e.g. Water Pump).</p>
            </div>
            <div>
              <h4 className="font-semibold text-slate-200">Self-Consumption</h4>
              <p className="text-slate-400 mt-1">The percentage of generated solar energy used locally rather than exported to the grid.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><HelpCircle size={20} className="text-blue-400" /> Frequently Asked Questions</h2>
        <div className="space-y-4 text-sm divide-y divide-slate-800">
          <div className="py-2">
            <h4 className="font-semibold text-slate-200">What does a 'Conflict' status mean?</h4>
            <p className="text-slate-400 mt-1">A conflict occurs when a load must run (due to deadlines) but there isn't enough solar or battery power available, forcing grid usage or skipping.</p>
          </div>
          <div className="py-2">
            <h4 className="font-semibold text-slate-200">How is the forecast calculated?</h4>
            <p className="text-slate-400 mt-1">The system uses a machine learning model trained on historical weather and solar output data to predict generation with confidence intervals.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Help;
