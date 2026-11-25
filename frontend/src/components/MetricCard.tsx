import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: string;
  trendColor?: string;
  color?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendColor = 'text-cyan-400',
  color = 'from-cyan-500/10 to-blue-500/5'
}) => {
  return (
    <div className={`relative overflow-hidden rounded-xl border border-slate-800 bg-gradient-to-br ${color} p-5 backdrop-blur shadow-sm hover:border-slate-700 transition`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <p className="mt-2 text-3xl font-extrabold text-white tracking-tight">{value}</p>
        </div>
        <div className="rounded-xl bg-slate-900/80 p-3 text-cyan-400 border border-slate-700/50 shadow-inner">
          {icon}
        </div>
      </div>
      {(subtitle || trend) && (
        <div className="mt-3 flex items-center gap-2 text-xs">
          {trend && <span className={`font-semibold ${trendColor}`}>{trend}</span>}
          {subtitle && <span className="text-slate-400">{subtitle}</span>}
        </div>
      )}
    </div>
  );
};

