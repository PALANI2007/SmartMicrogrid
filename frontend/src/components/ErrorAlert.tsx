import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface Props {
  message: string;
}

const ErrorAlert: React.FC<Props> = ({ message }) => {
  const { t } = useTranslation();
  return (
    <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-4 flex items-start gap-3">
      <AlertTriangle className="text-red-400 shrink-0 mt-0.5" size={20} />
      <div>
        <h4 className="text-red-400 font-semibold">{t('common.error')}</h4>
        <p className="text-slate-300 text-sm mt-1">{message}</p>
      </div>
    </div>
  );
};

export default ErrorAlert;
