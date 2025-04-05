'use client';

import { useState } from 'react';

// Enhanced mock client data with category and next review date
const MOCK_CLIENTS = [
  { 
    id: '1', 
    name: 'John Smith', 
    lastUpdated: '2023-04-21',
    category: 'active',
    nextReview: '2023-05-15',
    policies: ['Term Life', 'Health']
  },
  { 
    id: '2', 
    name: 'Sarah Johnson', 
    lastUpdated: '2023-04-19',
    category: 'active',
    nextReview: '2023-06-02',
    policies: ['Whole Life']
  },
  { 
    id: '3', 
    name: 'Michael Brown', 
    lastUpdated: '2023-04-18',
    category: 'pending',
    nextReview: null,
    policies: ['Health']
  },
  { 
    id: '4', 
    name: 'Emily Davis', 
    lastUpdated: '2023-04-15',
    category: 'review',
    nextReview: '2023-04-30',
    policies: ['Term Life', 'ILP', 'Critical Illness']
  },
  { 
    id: '5', 
    name: 'Robert Wilson', 
    lastUpdated: '2023-04-10',
    category: 'prospect',
    nextReview: null,
    policies: []
  }
];

interface SidebarProps {
  selectedClientId: string | null;
  onSelectClient: (id: string) => void;
}

export default function Sidebar({ selectedClientId, onSelectClient }: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'active' | 'review' | 'pending' | 'prospect'>('all');
  
  // Filter clients by search and category
  const filteredClients = MOCK_CLIENTS.filter(client => 
    client.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
    (selectedCategory === 'all' || client.category === selectedCategory)
  );
  
  // Get category badge color
  const getCategoryBadge = (category: string) => {
    switch (category) {
      case 'active':
        return 'bg-singlife-light text-singlife-dark';
      case 'review':
        return 'bg-singlife-light/80 text-singlife-dark';
      case 'pending':
        return 'bg-singlife-light/60 text-singlife-dark';
      case 'prospect':
        return 'bg-singlife-light/40 text-singlife-dark';
      default:
        return 'bg-singlife-light text-singlife-dark';
    }
  };
  
  // Get category label
  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'active':
        return 'Active';
      case 'review':
        return 'Due for Review';
      case 'pending':
        return 'Pending Decision';
      case 'prospect':
        return 'Prospect';
      default:
        return category;
    }
  };
  
  return (
    <div className="w-64 bg-singlife-light border-r border-singlife-light h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-singlife-light bg-white">
        <h1 className="text-xl font-semibold text-singlife-red">Beacon AI</h1>
        <p className="text-sm text-singlife-dark/70">Financial Advisor Assistant</p>
      </div>
      
      {/* Search */}
      <div className="p-3 border-b border-singlife-light">
        <input
          type="text"
          placeholder="Search clients..."
          className="w-full p-2 border border-singlife-light rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-singlife-red"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      
      {/* Category filter */}
      <div className="p-3 border-b border-singlife-light">
        <div className="grid grid-cols-2 gap-1">
          <button 
            className={`text-xs px-2 py-1 rounded ${selectedCategory === 'all' ? 'bg-singlife-red text-white' : 'bg-singlife-light text-singlife-dark hover:bg-singlife-light/80'}`}
            onClick={() => setSelectedCategory('all')}
          >
            All Clients
          </button>
          <button 
            className={`text-xs px-2 py-1 rounded ${selectedCategory === 'active' ? 'bg-singlife-red text-white' : 'bg-singlife-light text-singlife-dark hover:bg-singlife-light/80'}`}
            onClick={() => setSelectedCategory('active')}
          >
            Active
          </button>
          <button 
            className={`text-xs px-2 py-1 rounded ${selectedCategory === 'review' ? 'bg-singlife-red text-white' : 'bg-singlife-light text-singlife-dark hover:bg-singlife-light/80'}`}
            onClick={() => setSelectedCategory('review')}
          >
            Due for Review
          </button>
          <button 
            className={`text-xs px-2 py-1 rounded ${selectedCategory === 'prospect' ? 'bg-singlife-red text-white' : 'bg-singlife-light text-singlife-dark hover:bg-singlife-light/80'}`}
            onClick={() => setSelectedCategory('prospect')}
          >
            Prospects
          </button>
        </div>
      </div>
      
      {/* Client list */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-3 border-b border-singlife-light">
          <h2 className="text-sm font-medium text-singlife-dark/70">CLIENTS ({filteredClients.length})</h2>
        </div>
        <ul>
          {filteredClients.map(client => (
            <li 
              key={client.id}
              className={`p-3 hover:bg-singlife-light/80 cursor-pointer ${
                selectedClientId === client.id ? 'bg-singlife-light border-l-4 border-singlife-red' : ''
              }`}
              onClick={() => onSelectClient(client.id)}
            >
              <div className="flex justify-between items-center mb-1">
                <div className="font-medium">{client.name}</div>
                <div className={`text-xs px-2 py-0.5 rounded-full ${getCategoryBadge(client.category)}`}>
                  {getCategoryLabel(client.category)}
                </div>
              </div>
              
              {client.nextReview && (
                <div className="text-xs text-singlife-dark/50 mb-1">
                  Next review: {client.nextReview}
                </div>
              )}
              
              {client.policies.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {client.policies.map((policy, index) => (
                    <span key={index} className="text-[10px] px-1.5 py-0.5 bg-singlife-white text-singlife-dark/70 rounded">
                      {policy}
                    </span>
                  ))}
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
      
      {/* New client button */}
      <div className="p-3 border-t border-singlife-light bg-white">
        <button className="w-full btn-primary">
          + New Client
        </button>
      </div>
    </div>
  );
} 