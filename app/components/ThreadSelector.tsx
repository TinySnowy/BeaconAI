'use client';

import { useState } from 'react';

interface ConversationThread {
  id: string;
  title: string;
  type: 'policy-explanation' | 'needs-assessment' | 'product-recommendation' | 'compliance-check' | 'general';
  lastUpdated: Date;
}

interface ThreadSelectorProps {
  threads: ConversationThread[];
  selectedThreadId: string | null;
  onSelectThread: (id: string) => void;
  onCreateThread: (type: ConversationThread['type'], title: string) => void;
}

export default function ThreadSelector({ 
  threads, 
  selectedThreadId, 
  onSelectThread, 
  onCreateThread 
}: ThreadSelectorProps) {
  const [isCreateMenuOpen, setIsCreateMenuOpen] = useState(false);
  
  const getTypeIcon = (type: ConversationThread['type']) => {
    switch (type) {
      case 'policy-explanation':
        return '📄'; // Document
      case 'needs-assessment':
        return '📊'; // Chart
      case 'product-recommendation':
        return '🛒'; // Shopping cart
      case 'compliance-check':
        return '⚖️'; // Balance scale
      default:
        return '💬'; // Chat
    }
  };
  
  const getTypeLabel = (type: ConversationThread['type']) => {
    switch (type) {
      case 'policy-explanation':
        return 'Policy Explanation';
      case 'needs-assessment':
        return 'Needs Assessment';
      case 'product-recommendation':
        return 'Product Recommendation';
      case 'compliance-check':
        return 'Compliance Check';
      default:
        return 'General';
    }
  };
  
  const formatDate = (date: Date) => {
    // Format as relative time if today, otherwise show actual date
    const now = new Date();
    const isToday = now.toDateString() === date.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
    } else {
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    }
  };
  
  return (
    <div className="border-b border-gray-200 bg-white">
      <div className="px-4 py-2 flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">Conversation Threads</h3>
        
        <div className="relative">
          <button 
            className="text-xs bg-indigo-600 text-white px-3 py-1 rounded-md hover:bg-indigo-700 flex items-center"
            onClick={() => setIsCreateMenuOpen(!isCreateMenuOpen)}
          >
            <span className="mr-1">+</span> New Thread
          </button>
          
          {isCreateMenuOpen && (
            <div className="absolute right-0 mt-1 w-64 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
              <div className="py-1">
                <h4 className="px-4 py-2 text-xs font-semibold text-gray-500">CREATE NEW THREAD</h4>
                
                {/* Thread type options */}
                <button 
                  className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 flex items-center"
                  onClick={() => {
                    onCreateThread('policy-explanation', 'New Policy Explanation');
                    setIsCreateMenuOpen(false);
                  }}
                >
                  <span className="mr-2">{getTypeIcon('policy-explanation')}</span>
                  Policy Explanation
                </button>
                
                <button 
                  className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 flex items-center"
                  onClick={() => {
                    onCreateThread('needs-assessment', 'New Needs Assessment');
                    setIsCreateMenuOpen(false);
                  }}
                >
                  <span className="mr-2">{getTypeIcon('needs-assessment')}</span>
                  Needs Assessment
                </button>
                
                <button 
                  className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 flex items-center"
                  onClick={() => {
                    onCreateThread('product-recommendation', 'New Product Recommendation');
                    setIsCreateMenuOpen(false);
                  }}
                >
                  <span className="mr-2">{getTypeIcon('product-recommendation')}</span>
                  Product Recommendation
                </button>
                
                <button 
                  className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 flex items-center"
                  onClick={() => {
                    onCreateThread('compliance-check', 'New Compliance Check');
                    setIsCreateMenuOpen(false);
                  }}
                >
                  <span className="mr-2">{getTypeIcon('compliance-check')}</span>
                  Compliance Check
                </button>
                
                <button 
                  className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 flex items-center"
                  onClick={() => {
                    onCreateThread('general', 'New General Conversation');
                    setIsCreateMenuOpen(false);
                  }}
                >
                  <span className="mr-2">{getTypeIcon('general')}</span>
                  General Conversation
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Thread list */}
      <div className="overflow-x-auto">
        <div className="flex px-2 py-1 space-x-2 min-w-full">
          {threads.map(thread => (
            <button
              key={thread.id}
              className={`shrink-0 px-3 py-2 rounded-md flex flex-col min-w-32 ${
                selectedThreadId === thread.id
                  ? 'bg-indigo-100 border-2 border-indigo-500'
                  : 'bg-gray-100 hover:bg-gray-200 border border-gray-200'
              }`}
              onClick={() => onSelectThread(thread.id)}
            >
              <div className="flex items-center mb-1">
                <span className="mr-1">{getTypeIcon(thread.type)}</span>
                <span className="text-xs font-medium truncate max-w-[6rem]">{thread.title}</span>
              </div>
              <div className="text-[10px] text-gray-500">
                {formatDate(thread.lastUpdated)}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
} 