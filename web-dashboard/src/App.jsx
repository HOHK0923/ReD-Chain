import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import NodesPage from './pages/NodesPage';
import TasksPage from './pages/TasksPage';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'nodes':
        return <NodesPage />;
      case 'tasks':
        return <TasksPage />;
      case 'monitoring':
        return (
          <div className="card p-12 text-center text-gray-500">
            <h3 className="text-xl font-semibold mb-2">실시간 모니터링</h3>
            <p>개발 중입니다</p>
          </div>
        );
      case 'settings':
        return (
          <div className="card p-12 text-center text-gray-500">
            <h3 className="text-xl font-semibold mb-2">설정</h3>
            <p>개발 중입니다</p>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-dark">
      <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
      <main className="ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

export default App;
