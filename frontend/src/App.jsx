import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Interview from './pages/Interview';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="glass-dark border-b border-white/10 px-8 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            AI Recruitment System
          </h1>
          <div className="flex gap-4">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded-lg transition-all ${currentPage === 'dashboard'
                  ? 'bg-purple-600 text-white'
                  : 'text-slate-300 hover:text-white'
                }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentPage('interview')}
              className={`px-4 py-2 rounded-lg transition-all ${currentPage === 'interview'
                  ? 'bg-purple-600 text-white'
                  : 'text-slate-300 hover:text-white'
                }`}
            >
              Interview
            </button>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <main className="max-w-7xl mx-auto px-8 py-8">
        {currentPage === 'dashboard' ? <Dashboard /> : <Interview />}
      </main>
    </div>
  );
}

export default App;
