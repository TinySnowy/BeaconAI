'use client';

import { useState } from 'react';
import Sidebar from './Sidebar';
import ChatInterface from './ChatInterface';
import ContextPanel from './ContextPanel';

// Function types that serve as "chats" for each client
export type FunctionType = 'policy-explainer' | 'needs-assessment' | 'product-recommendation' | 'compliance-check';

// Function configuration
const FUNCTION_TYPES: Record<FunctionType, { name: string, description: string, icon: string }> = {
  'policy-explainer': {
    name: 'Policy Explainer',
    description: 'Understand details and coverage of insurance policies',
    icon: '📄'
  },
  'needs-assessment': {
    name: 'Needs Assessment',
    description: 'Analyze client financial needs and gaps',
    icon: '📊'
  },
  'product-recommendation': {
    name: 'Product Recommendation',
    description: 'Get suitable product suggestions for your client',
    icon: '🛒'
  },
  'compliance-check': {
    name: 'Compliance Check',
    description: 'Ensure regulatory compliance in recommendations',
    icon: '⚖️'
  }
};

export default function Dashboard() {
  const [selectedClientId, setSelectedClientId] = useState<string | null>(null);
  const [selectedFunction, setSelectedFunction] = useState<FunctionType | null>(null);
  const [expandedDocumentId, setExpandedDocumentId] = useState<string | null>(null);
  const [rightPanelVisible, setRightPanelVisible] = useState(false);
  
  // Handle document preview in the dynamic right panel
  const handleDocumentExpand = (documentId: string | null) => {
    setExpandedDocumentId(documentId);
    setRightPanelVisible(!!documentId);
  };
  
  return (
    <div className="flex h-screen">
      {/* Left sidebar for client list (functions like Projects in Claude) */}
      <Sidebar 
        selectedClientId={selectedClientId} 
        onSelectClient={(id) => {
          setSelectedClientId(id);
          setSelectedFunction(null); // Reset function when switching clients
          setExpandedDocumentId(null);
          setRightPanelVisible(false);
        }}
      />
      
      {/* Main content area - Flexible width based on right panel visibility */}
      <div className={`flex flex-col ${rightPanelVisible ? 'w-1/2' : 'flex-1'}`}>
        {selectedClientId ? (
          selectedFunction ? (
            <ChatInterface 
              clientId={selectedClientId}
              functionType={selectedFunction}
              onDocumentExpand={handleDocumentExpand}
              onGoBack={() => setSelectedFunction(null)}
            />
          ) : (
            <div className="flex flex-col h-full p-6">
              <h2 className="text-2xl font-semibold mb-6">How can I help you today?</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(Object.keys(FUNCTION_TYPES) as FunctionType[]).map(funcType => (
                  <div 
                    key={funcType}
                    className="border rounded-lg p-4 hover:border-singlife-red hover:shadow-md cursor-pointer transition-all"
                    onClick={() => setSelectedFunction(funcType)}
                  >
                    <div className="flex items-center mb-2">
                      <span className="text-2xl mr-3">{FUNCTION_TYPES[funcType].icon}</span>
                      <h3 className="text-lg font-medium">{FUNCTION_TYPES[funcType].name}</h3>
                    </div>
                    <p className="text-sm text-singlife-dark/70">{FUNCTION_TYPES[funcType].description}</p>
                  </div>
                ))}
              </div>
            </div>
          )
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md p-8">
              <h2 className="text-2xl font-semibold mb-4">Welcome to Beacon AI</h2>
              <p className="text-singlife-dark/70 mb-6">
                Your AI-powered assistant for insurance advisory. Select a client from the sidebar 
                or create a new client to get started.
              </p>
              <button 
                className="btn-primary"
                onClick={() => {
                  // Implementation for creating a new client
                  // will be added later
                }}
              >
                Start with a New Client
              </button>
            </div>
          </div>
        )}
      </div>
      
      {/* Right context panel - Only visible when a document is expanded or when toggled */}
      {rightPanelVisible && (
        <ContextPanel 
          clientId={selectedClientId}
          documentId={expandedDocumentId}
          onClose={() => {
            setRightPanelVisible(false);
            setExpandedDocumentId(null);
          }}
        />
      )}
    </div>
  );
} 