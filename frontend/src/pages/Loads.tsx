import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Plus, Edit2, Trash2, X } from 'lucide-react';
import { loadsApi } from '../services/api';
import { Load } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import ConfirmDialog from '../components/ConfirmDialog';
import StatusBadge from '../components/StatusBadge';

const Loads = () => {
  const { t } = useTranslation();
  const [loads, setLoads] = useState<Load[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingLoad, setEditingLoad] = useState<Load | null>(null);
  const [formData, setFormData] = useState<any>({});
  
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [loadToDelete, setLoadToDelete] = useState<number | null>(null);

  const fetchLoads = async () => {
    try {
      setLoading(true);
      const data = await loadsApi.getLoads();
      setLoads(data);
    } catch (err) {
      setError(String(err) || 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLoads(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingLoad) {
        await loadsApi.updateLoad(editingLoad.id, formData);
      } else {
        await loadsApi.createLoad(formData);
      }
      setIsModalOpen(false);
      fetchLoads();
    } catch (err) {
      setError(String(err));
    }
  };

  const handleDelete = async () => {
    if (!loadToDelete) return;
    try {
      await loadsApi.deleteLoad(loadToDelete);
      setDeleteConfirmOpen(false);
      fetchLoads();
    } catch (err) {
      setError(String(err));
    }
  };

  const openModal = (load?: Load) => {
    if (load) {
      setEditingLoad(load);
      setFormData(load);
    } else {
      setEditingLoad(null);
      setFormData({ load_type: 'flexible', priority: 'medium', power_kw: 1, duration_hours: 1 });
    }
    setIsModalOpen(true);
  };

  if (loading && !loads.length) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">{t('loads.title')}</h1>
        <button onClick={() => openModal()} className="btn-primary">
          <Plus size={18} /> {t('loads.addLoad')}
        </button>
      </div>

      {error && <ErrorAlert message={error} />}

      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/50 text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">{t('loads.name')}</th>
                <th className="px-4 py-3">{t('loads.type')}</th>
                <th className="px-4 py-3">{t('loads.power')}</th>
                <th className="px-4 py-3">{t('loads.duration')}</th>
                <th className="px-4 py-3">{t('loads.priority')}</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {loads.map((load) => (
                <tr key={load.id} className="hover:bg-slate-800/30">
                  <td className="px-4 py-3 font-medium text-white">{load.name}</td>
                  <td className="px-4 py-3">
                    <span className={`badge-${load.load_type}`}>{t(`loads.${load.load_type}`)}</span>
                  </td>
                  <td className="px-4 py-3">{load.power_kw} kW</td>
                  <td className="px-4 py-3">{load.duration_hours} h</td>
                  <td className="px-4 py-3">
                    <span className={`badge-${load.priority}`}>{t(`loads.${load.priority}`)}</span>
                  </td>
                  <td className="px-4 py-3 flex justify-end gap-2">
                    <button onClick={() => openModal(load)} className="p-1.5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg">
                      <Edit2 size={16} />
                    </button>
                    <button onClick={() => { setLoadToDelete(load.id); setDeleteConfirmOpen(true); }} className="p-1.5 text-red-400 hover:text-white bg-red-900/20 hover:bg-red-900/50 rounded-lg">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]">
            <div className="flex justify-between items-center p-6 border-b border-slate-800">
              <h3 className="text-xl font-semibold text-white">{editingLoad ? t('loads.editLoad') : t('loads.addLoad')}</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">{t('loads.name')}</label>
                <input type="text" className="input-field" required value={formData.name || ''} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">{t('loads.type')}</label>
                  <select className="select-field" value={formData.load_type || 'flexible'} onChange={e => setFormData({...formData, load_type: e.target.value})}>
                    <option value="essential">{t('loads.essential')}</option>
                    <option value="flexible">{t('loads.flexible')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">{t('loads.priority')}</label>
                  <select className="select-field" value={formData.priority || 'medium'} onChange={e => setFormData({...formData, priority: e.target.value})}>
                    <option value="high">{t('loads.high')}</option>
                    <option value="medium">{t('loads.medium')}</option>
                    <option value="low">{t('loads.low')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">{t('loads.power')}</label>
                  <input type="number" step="0.1" className="input-field" required value={formData.power_kw || ''} onChange={e => setFormData({...formData, power_kw: parseFloat(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">{t('loads.duration')}</label>
                  <input type="number" step="0.5" className="input-field" required value={formData.duration_hours || ''} onChange={e => setFormData({...formData, duration_hours: parseFloat(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">{t('loads.earliestStart')}</label>
                  <input type="time" className="input-field" value={formData.earliest_start || ''} onChange={e => setFormData({...formData, earliest_start: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">{t('loads.latestFinish')}</label>
                  <input type="time" className="input-field" value={formData.latest_finish || ''} onChange={e => setFormData({...formData, latest_finish: e.target.value})} />
                </div>
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary">{t('common.cancel')}</button>
                <button type="submit" className="btn-primary">{t('common.save')}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ConfirmDialog
        isOpen={deleteConfirmOpen}
        title={t('loads.deleteLoad')}
        message={t('loads.confirmDelete')}
        onConfirm={handleDelete}
        onCancel={() => setDeleteConfirmOpen(false)}
      />
    </div>
  );
};

export default Loads;
