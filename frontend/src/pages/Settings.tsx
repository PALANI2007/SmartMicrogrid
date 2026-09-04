import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CheckCircle2, Globe, Palette } from 'lucide-react';
import { validationApi } from '../services/api';

const Settings = () => {
  const { t, i18n } = useTranslation();
  const [formData, setFormData] = useState({
    respondent_name: '', q1_understandable: 5, q2_explanation_clear: 5, q3_disruption: 5, q4_easy_to_read: 5, q5_language_useful: 5, q6_confidence_clear: 5, notes: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await validationApi.submit(formData);
      setSubmitted(true);
    } catch (err) {
      console.error(err);
    }
  };

  const changeLanguage = (e: React.ChangeEvent<HTMLSelectElement>) => {
    i18n.changeLanguage(e.target.value);
    localStorage.setItem('language', e.target.value);
  };

  const StarRating = ({ value, onChange, label }: { value: number, onChange: (v: number) => void, label: string }) => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-slate-300 mb-2">{label}</label>
      <div className="flex gap-2">
        {[1,2,3,4,5].map(star => (
          <button key={star} type="button" onClick={() => onChange(star)} className={`text-2xl focus:outline-none ${star <= value ? 'text-yellow-400' : 'text-slate-700'}`}>★</button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-white">{t('settings.title')}</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Globe size={20} className="text-primary-400"/> Preferences</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">{t('settings.language')}</label>
              <select className="select-field" value={i18n.language} onChange={changeLanguage}>
                <option value="en">English</option>
                <option value="ta">தமிழ் (Tamil)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">{t('settings.theme')}</label>
              <select className="select-field" disabled>
                <option>Dark (Default)</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card md:col-span-2">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><CheckCircle2 size={20} className="text-green-400"/> {t('settings.validation')}</h2>
          <p className="text-slate-400 text-sm mb-6">Please help us validate this system by answering a few quick questions about your experience.</p>
          
          {submitted ? (
            <div className="bg-green-900/30 border border-green-500/50 rounded-xl p-6 text-center">
              <CheckCircle2 size={48} className="text-green-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white">Thank You!</h3>
              <p className="text-slate-300 mt-2">Your feedback has been recorded successfully.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <StarRating label="1. Are the schedules understandable?" value={formData.q1_understandable} onChange={v => setFormData({...formData, q1_understandable: v})} />
                <StarRating label="2. Are the schedule explanations clear?" value={formData.q2_explanation_clear} onChange={v => setFormData({...formData, q2_explanation_clear: v})} />
                <StarRating label="3. Is the schedule acceptable/non-disruptive?" value={formData.q3_disruption} onChange={v => setFormData({...formData, q3_disruption: v})} />
                <StarRating label="4. Is the dashboard easy to read?" value={formData.q4_easy_to_read} onChange={v => setFormData({...formData, q4_easy_to_read: v})} />
                <StarRating label="5. Is the Tamil language option useful?" value={formData.q5_language_useful} onChange={v => setFormData({...formData, q5_language_useful: v})} />
                <StarRating label="6. Is the forecast uncertainty clear?" value={formData.q6_confidence_clear} onChange={v => setFormData({...formData, q6_confidence_clear: v})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Additional Feedback</label>
                <textarea className="input-field min-h-[100px]" value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})}></textarea>
              </div>
              <button type="submit" className="btn-primary">Submit Validation</button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
