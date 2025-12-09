import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Interview from './pages/Interview';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-purple-500/30">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/10 p-6 flex flex-col glass-dark h-screen fixed top-0 left-0 z-10">
        <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-8">
          AI Recruiter
        </h1>

        <nav className="flex-1 space-y-2">
          <button
            onClick={() => setCurrentPage('dashboard')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentPage === 'dashboard'
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/20'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
          >
            <span>📊</span>
            <span className="font-medium">Dashboard</span>
          </button>
          <button
            onClick={() => setCurrentPage('interview')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentPage === 'interview'
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/20'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
          >
            <span>⚡</span>
            <span className="font-medium">Interview</span>
          </button>
        </nav>

        <div className="pt-6 border-t border-white/10">
          <p className="text-xs text-slate-500">v2.0.0 • AI-Powered</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          {currentPage === 'dashboard' ? <Dashboard /> : <Interview />}
        </div>
      </main>
    </div>
  );
}

export default App;
