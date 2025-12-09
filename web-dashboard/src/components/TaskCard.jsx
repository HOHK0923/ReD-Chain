import React from 'react';
import { Target, CheckCircle, XCircle, Clock, Play } from 'lucide-react';

const taskTypeNames = {
  port_scan: '포트 스캔',
  traffic_gen: '트래픽 생성',
  http_flood: 'HTTP Flood',
  slowloris: 'Slowloris',
  udp_flood: 'UDP Flood',
  custom: '커스텀 작업',
};

const statusIcons = {
  pending: Clock,
  running: Play,
  completed: CheckCircle,
  failed: XCircle,
};

export default function TaskCard({ task }) {
  const StatusIcon = statusIcons[task.status] || Clock;
  const taskName = taskTypeNames[task.task_type] || task.task_type;

  return (
    <div className="card p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/20 rounded-lg">
            <Target className="text-primary" size={20} />
          </div>
          <div>
            <h4 className="font-semibold">{taskName}</h4>
            <p className="text-xs text-gray-500 mt-0.5">
              {task.assigned_node_id ? `Node: ${task.assigned_node_id.slice(0, 8)}...` : 'Broadcast'}
            </p>
          </div>
        </div>
        <span className={`badge badge-${task.status}`}>
          <StatusIcon size={12} className="mr-1" />
          {task.status}
        </span>
      </div>

      {/* Parameters */}
      {task.parameters && (
        <div className="bg-dark rounded-lg p-3 mb-3">
          <div className="text-xs space-y-1">
            {Object.entries(task.parameters).slice(0, 3).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-gray-500">{key}:</span>
                <span className="text-gray-300 font-mono text-xs">
                  {typeof value === 'object' ? JSON.stringify(value) : String(value).slice(0, 30)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>작업 ID: {task.task_id?.slice(0, 12)}...</span>
        {task.created_at && (
          <span>{new Date(task.created_at).toLocaleTimeString('ko-KR')}</span>
        )}
      </div>
    </div>
  );
}
