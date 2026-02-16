import React from 'react';
import { useQuery } from 'react-query';
import { companies, changes } from '../services/api';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  BuildingOfficeIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { data: companiesData } = useQuery('companies', () => companies.list());
  const { data: changesData } = useQuery('recent-changes', () => 
    changes.list({ limit: 10 })
  );

  const stats = [
    {
      name: 'Tracked Companies',
      value: companiesData?.length || 0,
      icon: BuildingOfficeIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Recent Changes',
      value: changesData?.length || 0,
      icon: ArrowPathIcon,
      color: 'bg-green-500',
    },
    {
      name: 'High Significance',
      value: changesData?.filter((c: any) => c.significance_score >= 70).length || 0,
      icon: ExclamationTriangleIcon,
      color: 'bg-yellow-500',
    },
    {
      name: 'Categories',
      value: new Set(changesData?.map((c: any) => c.category)).size || 0,
      icon: ChartBarIcon,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-lg shadow p-6"
          >
            <div className="flex items-center">
              <div className={`${stat.color} rounded-lg p-3`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Recent Changes</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {changesData?.map((change: any) => (
              <div key={change.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {change.company_name}
                    </p>
                    <p className="text-sm text-gray-600">{change.summary}</p>
                  </div>
                  <div className="flex items-center">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      change.significance_score >= 70
                        ? 'bg-red-100 text-red-800'
                        : change.significance_score >= 40
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {change.significance_score}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
              Add New Company
            </button>
            <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              View All Changes
            </button>
            <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              Configure Alerts
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;