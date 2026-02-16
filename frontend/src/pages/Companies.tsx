import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { companies } from '../services/api';
import { motion } from 'framer-motion';
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import AddCompanyModal from '../components/companies/AddCompanyModal';

const Companies: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [search, setSearch] = useState('');
  const queryClient = useQueryClient();

  const { data: companiesList, isLoading } = useQuery('companies', () => 
    companies.list()
  );

  const deleteMutation = useMutation(companies.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('companies');
    },
  });

  const filteredCompanies = companiesList?.filter((company: any) =>
    company.name.toLowerCase().includes(search.toLowerCase()) ||
    company.url.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Companies</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Company
        </button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search companies..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Companies Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCompanies?.map((company: any, index: number) => (
            <motion.div
              key={company.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-1">
                  {company.name}
                </h3>
                <p className="text-sm text-gray-500 mb-4">{company.url}</p>
                
                <div className="flex items-center justify-between">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    company.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {company.status}
                  </span>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => window.location.href = `/companies/${company.id}`}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      View
                    </button>
                    <button
                      onClick={() => {
                        if (window.confirm('Delete this company?')) {
                          deleteMutation.mutate(company.id);
                        }
                      }}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      <AddCompanyModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
};

export default Companies;