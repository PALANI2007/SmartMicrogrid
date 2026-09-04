import React from 'react';

interface Props {
  title: string;
  value: string | number;
  unit?: string;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'primary' | 'solar' | 'grid' | 'battery';
}

const MetricCard: React.FC<Props> = ({ title, value, unit, icon, trend, color = 'primary' }) => {
  const colorMap = {
    primary: 'text-primary-400 bg-primary-400/10',
    solar: 'text-solar-400 bg-solar-400/10',
    grid: 'text-grid-400 bg-grid-400/10',
    battery: 'text-battery-400 bg-battery-400/10',
  };

  return (
    <div className="stat-card">
      <div className="flex items-start justify-between">
        <h3 className="text-slate-400 text-sm font-medium">{title}</h3>
        <div className={`p-2 rounded-xl ${colorMap[color]}`}>
          {icon}
        </div>
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-slate-100">{value}</span>
        {unit && <span className="text-slate-400 text-sm font-medium">{unit}</span>}
      </div>
      {trend && (
        <div className="mt-2 text-xs font-medium flex items-center gap-1">
          <span className={trend.isPositive ? 'text-green-400' : 'text-red-400'}>
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
          <span className="text-slate-500">vs yesterday</span>
        </div>
      )}
    </div>
  );
};

export default MetricCard;
