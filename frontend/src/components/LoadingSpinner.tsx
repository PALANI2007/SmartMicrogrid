import React from 'react';
import { Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const LoadingSpinner = ({ size = 24 }: { size?: number }) => {
  const { t } = useTranslation();
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <Loader2 size={size} className="animate-spin text-primary-500" />
      <span className="text-slate-400">{t('common.loading')}</span>
    </div>
  );
};

export default LoadingSpinner;
