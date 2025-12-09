import React from 'react';
import { Smartphone, Activity, Target, BarChart3, Settings } from 'lucide-react';

const menuItems = [
  { id: 'dashboard', label: '대시보드', icon: BarChart3 },
  { id: 'nodes', label: '좀비폰 관리', icon: Smartphone },
  { id: 'tasks', label: '작업 관리', icon: Target },
  { id: 'monitoring', label: '실시간 모니터링', icon: Activity },
  { id: 'settings', label: '설정', icon: Settings },
];

export default function Sidebar({ currentPage, onPageChange }) {
  return (
    <div className="w-64 bg-dark-light border-r border-dark-lighter h-screen fixed left-0 top-0 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-dark-lighter">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          ReD-Chain C2
        </h1>
        <p className="text-xs text-gray-500 mt-1">Command & Control Center</p>
      </div>

      {/* Menu */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all
                ${isActive
                  ? 'bg-primary text-white shadow-lg shadow-primary/20'
                  : 'text-gray-400 hover:bg-dark-lighter hover:text-gray-200'
                }
              `}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-dark-lighter">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>C2 Server Online</span>
        </div>
      </div>
    </div>
  );
}
