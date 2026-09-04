import React from 'react';
import { useTranslation } from 'react-i18next';
import { FileQuestion } from 'lucide-react';

interface Props {
  message?: string;
}

const EmptyState: React.FC<Props> = ({ message }) => {
  const { t } = useTranslation();
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center border-2 border-dashed border-slate-700 rounded-2xl">
      <FileQuestion size={48} className="text-slate-600 mb-4" />
      <p className="text-slate-400 font-medium">{message || t('common.noData')}</p>
    </div>
  );
};

export default EmptyState;
