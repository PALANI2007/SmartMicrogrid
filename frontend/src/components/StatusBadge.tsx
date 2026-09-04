import React from 'react';

type Status = 'GOOD' | 'WARNING' | 'CONFLICT' | 'SCHEDULED' | 'SKIPPED';

interface Props {
  status: Status;
  text?: string;
}

const StatusBadge: React.FC<Props> = ({ status, text }) => {
  const getBadgeClass = () => {
    switch (status) {
      case 'GOOD':
      case 'SCHEDULED':
        return 'bg-green-900/50 text-green-300 border-green-700/50';
      case 'WARNING':
        return 'bg-yellow-900/50 text-yellow-300 border-yellow-700/50';
      case 'CONFLICT':
      case 'SKIPPED':
        return 'bg-red-900/50 text-red-300 border-red-700/50';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeClass()}`}>
      {text || status}
    </span>
  );
};

export default StatusBadge;
