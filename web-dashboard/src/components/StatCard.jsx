import React from 'react';

export default function StatCard({ title, value, icon: Icon, change, trend = 'up' }) {
  return (
    <div className="card p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-2">{title}</p>
          <h3 className="text-3xl font-bold text-white">{value}</h3>
          {change && (
            <p className={`text-sm mt-2 ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
              {trend === 'up' ? '↑' : '↓'} {change}
            </p>
          )}
        </div>
        <div className="p-3 bg-primary/20 rounded-xl">
          <Icon className="text-primary" size={24} />
        </div>
      </div>
    </div>
  );
}
