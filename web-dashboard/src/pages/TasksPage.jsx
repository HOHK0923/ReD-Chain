import React, { useEffect, useState } from 'react';
import { Plus, Filter } from 'lucide-react';
import TaskCard from '../components/TaskCard';
import { c2Api } from '../api/c2Api';

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTasks();
    const interval = setInterval(loadTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadTasks = async () => {
    try {
      const data = await c2Api.getTasks(statusFilter === 'all' ? null : statusFilter);
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = statusFilter === 'all'
    ? tasks
    : tasks.filter(task => task.status === statusFilter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold mb-2">작업 관리</h2>
          <p className="text-gray-500">좀비폰에 할당된 작업을 관리하고 모니터링하세요</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          새 작업 생성
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          <Filter size={20} className="text-gray-500" />
          <div className="flex gap-2">
            {['all', 'pending', 'running', 'completed', 'failed'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-4 py-2 rounded-lg transition-all ${
                  statusFilter === status
                    ? 'bg-primary text-white'
                    : 'bg-dark-lighter text-gray-400 hover:bg-dark-lighter/80'
                }`}
              >
                {status === 'all' ? '전체' : status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="card p-4">
          <div className="text-sm text-gray-500 mb-1">전체</div>
          <div className="text-2xl font-bold">{tasks.length}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500 mb-1">대기중</div>
          <div className="text-2xl font-bold text-yellow-400">
            {tasks.filter(t => t.status === 'pending').length}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500 mb-1">실행중</div>
          <div className="text-2xl font-bold text-blue-400">
            {tasks.filter(t => t.status === 'running').length}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500 mb-1">완료</div>
          <div className="text-2xl font-bold text-green-400">
            {tasks.filter(t => t.status === 'completed').length}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500 mb-1">실패</div>
          <div className="text-2xl font-bold text-red-400">
            {tasks.filter(t => t.status === 'failed').length}
          </div>
        </div>
      </div>

      {/* Tasks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTasks.map((task) => (
          <TaskCard key={task.task_id} task={task} />
        ))}
      </div>

      {filteredTasks.length === 0 && (
        <div className="card p-12 text-center text-gray-500">
          <p>{statusFilter === 'all' ? '생성된 작업이 없습니다' : `${statusFilter} 상태의 작업이 없습니다`}</p>
        </div>
      )}

      {/* Create Task Modal - Simplified for now */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">새 작업 생성</h3>
            <p className="text-gray-500 mb-4">
              작업 생성은 Commander CLI를 통해 더 쉽게 할 수 있습니다.
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary flex-1"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
