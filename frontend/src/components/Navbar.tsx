import { Home, BarChart2, Table } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 bg-white shadow-md z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex-shrink-0">
            <span className="text-xl font-bold text-indigo-600">DataQuest.ai</span>
          </div>
          <div className="flex space-x-8">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center space-x-2 text-gray-600 hover:text-indigo-600 transition-colors ${
                  isActive ? 'text-indigo-600' : ''
                }`
              }
            >
              <Home size={20} />
              <span>Home</span>
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `flex items-center space-x-2 text-gray-600 hover:text-indigo-600 transition-colors ${
                  isActive ? 'text-indigo-600' : ''
                }`
              }
            >
              <BarChart2 size={20} />
              <span>Dashboard</span>
            </NavLink>
            <NavLink
              to="/table"
              className={({ isActive }) =>
                `flex items-center space-x-2 text-gray-600 hover:text-indigo-600 transition-colors ${
                  isActive ? 'text-indigo-600' : ''
                }`
              }
            >
              <Table size={20} />
              <span>Table Visualizer</span>
            </NavLink>
          </div>
        </div>
      </div>
    </nav>
  );
}