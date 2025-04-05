'use client';

import { FC, useState } from 'react';

interface DocumentReference {
  id: string;
  title: string;
  type: 'policy' | 'financial' | 'regulatory';
  snippet: string;
}

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  agentType?: 'policy-explainer' | 'needs-assessment' | 'product-recommendation' | 'compliance-check';
  chainOfThought?: string;
  documentReferences?: DocumentReference[];
}

interface MessageProps {
  message: ChatMessage;
  onDocumentClick?: (documentId: string) => void;
}

const Message: FC<MessageProps> = ({ message, onDocumentClick }) => {
  const [showChainOfThought, setShowChainOfThought] = useState(false);
  const isAI = message.sender === 'ai';
  const formattedTime = new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: 'numeric',
    hour12: true
  }).format(new Date(message.timestamp));

  // Get agent type label and color
  const getAgentLabel = () => {
    if (!message.agentType) return null;
    
    switch (message.agentType) {
      case 'policy-explainer':
        return { label: 'Policy Explainer', bgColor: 'bg-singlife-light', textColor: 'text-singlife-dark' };
      case 'needs-assessment':
        return { label: 'Needs Assessment', bgColor: 'bg-singlife-light', textColor: 'text-singlife-dark' };
      case 'product-recommendation':
        return { label: 'Product Recommendation', bgColor: 'bg-singlife-light', textColor: 'text-singlife-dark' };
      case 'compliance-check':
        return { label: 'Compliance Check', bgColor: 'bg-singlife-light', textColor: 'text-singlife-dark' };
      default:
        return null;
    }
  };
  
  // Get document type styles
  const getDocumentStyles = (type: DocumentReference['type']) => {
    switch (type) {
      case 'policy':
        return { bgColor: 'bg-singlife-light', borderColor: 'border-singlife-red/20', icon: '📄' };
      case 'financial':
        return { bgColor: 'bg-singlife-light', borderColor: 'border-singlife-red/20', icon: '📊' };
      case 'regulatory':
        return { bgColor: 'bg-singlife-light', borderColor: 'border-singlife-red/20', icon: '⚖️' };
      default:
        return { bgColor: 'bg-singlife-light', borderColor: 'border-singlife-dark/20', icon: '📎' };
    }
  };
  
  const agentInfo = isAI ? getAgentLabel() : null;

  return (
    <div className={`flex mb-4 ${isAI ? 'justify-start' : 'justify-end'}`}>
      <div 
        className={`max-w-[75%] rounded-lg px-4 py-2 ${
          isAI 
            ? 'bg-singlife-white border border-singlife-light text-singlife-dark' 
            : 'bg-singlife-red text-singlife-white'
        }`}
      >
        {/* Agent type label - only for AI messages */}
        {agentInfo && (
          <div className={`text-xs px-2 py-0.5 rounded-full inline-block mb-1 ${agentInfo.bgColor} ${agentInfo.textColor}`}>
            {agentInfo.label}
          </div>
        )}
        
        {/* Message text */}
        <div className="text-sm">{message.text}</div>
        
        {/* Document references */}
        {isAI && message.documentReferences && message.documentReferences.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.documentReferences.map(doc => {
              const docStyles = getDocumentStyles(doc.type);
              return (
                <div 
                  key={doc.id} 
                  className={`text-xs rounded border p-2 ${docStyles.bgColor} ${docStyles.borderColor} cursor-pointer hover:shadow-sm transition-shadow`}
                  onClick={() => onDocumentClick && onDocumentClick(doc.id)}
                >
                  <div className="flex items-center mb-1">
                    <span className="mr-1">{docStyles.icon}</span>
                    <span className="font-medium">{doc.title}</span>
                  </div>
                  <p className="text-singlife-dark">{doc.snippet}</p>
                  <div className="text-singlife-red text-right mt-1">View Document →</div>
                </div>
              );
            })}
          </div>
        )}
        
        {/* Timestamp */}
        <div className="flex justify-between items-center mt-1">
          <div className={`text-xs ${isAI ? 'text-singlife-dark/50' : 'text-singlife-white/70'}`}>
            {formattedTime}
          </div>
          
          {/* Chain of thought toggle - only for AI messages with CoT */}
          {isAI && message.chainOfThought && (
            <button 
              onClick={() => setShowChainOfThought(!showChainOfThought)}
              className="text-xs text-singlife-red hover:text-singlife-dark"
            >
              {showChainOfThought ? 'Hide reasoning' : 'Show reasoning'}
            </button>
          )}
        </div>
        
        {/* Chain of thought reasoning - collapsed by default */}
        {isAI && message.chainOfThought && showChainOfThought && (
          <div className="mt-2 text-xs bg-singlife-light p-2 border border-singlife-light rounded text-singlife-dark whitespace-pre-line">
            <div className="font-medium mb-1">Reasoning Process:</div>
            {message.chainOfThought}
          </div>
        )}
      </div>
    </div>
  );
};

export default Message; 