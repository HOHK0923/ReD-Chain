import React from 'react';
import { Smartphone, Battery, Cpu, HardDrive, MapPin, Clock } from 'lucide-react';

export default function NodeCard({ node }) {
  const isOnline = node.status === 'online';

  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString('ko-KR');
  };

  return (
    <div className="card p-6 hover:border-primary/50 transition-all cursor-pointer">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-xl ${isOnline ? 'bg-primary/20' : 'bg-gray-500/20'}`}>
            <Smartphone className={isOnline ? 'text-primary' : 'text-gray-500'} size={24} />
          </div>
          <div>
            <h3 className="font-semibold text-lg">{node.device_name || 'Unknown Device'}</h3>
            <p className="text-sm text-gray-500">{node.model || 'N/A'}</p>
          </div>
        </div>
        <span className={`badge ${isOnline ? 'badge-online' : 'badge-offline'}`}>
          {isOnline ? 'Online' : 'Offline'}
        </span>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center gap-2">
          <Battery size={16} className="text-gray-500" />
          <span className="text-sm">
            <span className="text-gray-500">배터리:</span>{' '}
            <span className="font-medium">{node.battery_level || 0}%</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Cpu size={16} className="text-gray-500" />
          <span className="text-sm">
            <span className="text-gray-500">CPU:</span>{' '}
            <span className="font-medium">{node.cpu_usage ? node.cpu_usage.toFixed(1) : 0}%</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <HardDrive size={16} className="text-gray-500" />
          <span className="text-sm">
            <span className="text-gray-500">Memory:</span>{' '}
            <span className="font-medium">{node.memory_usage || 0} MB</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Clock size={16} className="text-gray-500" />
          <span className="text-sm">
            <span className="text-gray-500">마지막 접속</span>
          </span>
        </div>
      </div>

      {/* Footer */}
      <div className="pt-4 border-t border-dark-lighter">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{node.os_version || 'Unknown OS'}</span>
          <span className="font-mono">{node.node_id?.slice(0, 8)}...</span>
        </div>
      </div>
    </div>
  );
}
