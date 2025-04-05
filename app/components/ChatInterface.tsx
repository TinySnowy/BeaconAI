'use client';

import { useState, useRef, useEffect } from 'react';
import Message from './Message';
import ChatInput from './ChatInput';
import { FunctionType } from './Dashboard';

// Types
interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  agentType?: 'policy-explainer' | 'needs-assessment' | 'product-recommendation' | 'compliance-check';
  chainOfThought?: string;
  documentReferences?: DocumentReference[];
}

interface DocumentReference {
  id: string;
  title: string;
  type: 'policy' | 'financial' | 'regulatory';
  snippet: string;
}

interface ClientData {
  id: string;
  name: string;
  age: number;
  occupation: string;
  dependents: number;
  insurancePolicies: string[];
}

// Mock client data
const MOCK_CLIENT_DATA: Record<string, ClientData> = {
  '1': {
    id: '1',
    name: 'John Smith',
    age: 35,
    occupation: 'Software Engineer',
    dependents: 2,
    insurancePolicies: ['Term Life Insurance', 'Health Insurance']
  },
  '2': {
    id: '2',
    name: 'Sarah Johnson',
    age: 42,
    occupation: 'Marketing Manager',
    dependents: 1,
    insurancePolicies: ['Whole Life Insurance']
  },
  '3': {
    id: '3',
    name: 'Michael Brown',
    age: 29,
    occupation: 'Teacher',
    dependents: 0,
    insurancePolicies: ['Health Insurance']
  },
  '4': {
    id: '4',
    name: 'Emily Davis',
    age: 55,
    occupation: 'Doctor',
    dependents: 3,
    insurancePolicies: ['Term Life Insurance', 'Investment-Linked Policy', 'Critical Illness']
  },
};

// Mock chat history for each client + function combination
const MOCK_CHAT_HISTORY: Record<string, Record<FunctionType, ChatMessage[]>> = {
  '1': {
    'policy-explainer': [
      {
        id: '1',
        text: 'Hi, I need to review John Smith\'s life insurance policy. What can you tell me about his current coverage?',
        sender: 'user',
        timestamp: new Date('2023-04-21T10:30:00')
      },
      {
        id: '2',
        text: 'Based on John Smith\'s profile, he currently has a Term Life Insurance policy with the following details:\n\n- Coverage: $500,000\n- Term: 20 years\n- Premium: $1,200/year\n\nConsidering his family situation with 2 dependents, you should ensure his coverage is adequate. Would you like me to analyze if his current coverage amount is sufficient based on his financial needs?',
        sender: 'ai',
        agentType: 'policy-explainer',
        timestamp: new Date('2023-04-21T10:31:00'),
        documentReferences: [
          {
            id: 'doc1',
            title: 'Term Life Insurance Policy',
            type: 'policy',
            snippet: 'Coverage: $500,000 | Term: 20 years | Premium: $1,200/year'
          }
        ]
      }
    ],
    'needs-assessment': [],
    'product-recommendation': [],
    'compliance-check': []
  },
  '2': {
    'policy-explainer': [],
    'needs-assessment': [
      {
        id: '1',
        text: 'I\'m meeting with Sarah Johnson next week to discuss her retirement planning options. What should I recommend?',
        sender: 'user',
        timestamp: new Date('2023-04-19T14:20:00')
      },
      {
        id: '2',
        text: 'For your upcoming meeting with Sarah Johnson, her current age of 42 makes this an ideal time to review retirement planning options.',
        sender: 'ai',
        agentType: 'needs-assessment',
        timestamp: new Date('2023-04-19T14:21:00'),
        chainOfThought: '1. Client is 42 years old\n2. Retirement typically occurs between 60-65\n3. That gives approximately 18-23 years for retirement planning\n4. Client has one dependent, which affects financial planning\n5. Already has Whole Life Insurance with savings component\n6. Need to assess if additional retirement-specific products are needed'
      },
      {
        id: '3',
        text: 'Sarah\'s current Whole Life Insurance policy provides a savings component, but you might want to discuss additional options like retirement-focused investment-linked policies or dedicated retirement plans. I can prepare a comparison of the key differences between these options for your meeting, highlighting the advantages of each based on her profile.',
        sender: 'ai',
        agentType: 'product-recommendation',
        timestamp: new Date('2023-04-19T14:22:00')
      }
    ],
    'product-recommendation': [],
    'compliance-check': []
  },
  '4': {
    'policy-explainer': [],
    'needs-assessment': [
      {
        id: '1',
        text: 'I need to evaluate Emily Davis\'s estate planning needs. She has 3 dependents and substantial assets to protect.',
        sender: 'user',
        timestamp: new Date('2023-04-14T09:44:00')
      },
      {
        id: '2',
        text: 'Based on Emily\'s profile with 3 dependents and her career as a doctor, estate planning is indeed a priority. I recommend you focus on assessing her current net worth, outstanding debts, and future educational expenses for her dependents.',
        sender: 'ai',
        agentType: 'needs-assessment',
        timestamp: new Date('2023-04-14T09:45:00'),
        documentReferences: [
          {
            id: 'doc4',
            title: 'Estate Planning Checklist',
            type: 'financial',
            snippet: 'Key considerations: Will, Trust, Power of Attorney, Healthcare Directive, Beneficiary Designations'
          }
        ]
      }
    ],
    'product-recommendation': [
      {
        id: '1',
        text: 'Emily Davis contacted me about her investment-linked policy performance. She\'s concerned about market volatility. What should I tell her?',
        sender: 'user',
        timestamp: new Date('2023-04-15T11:09:00')
      },
      {
        id: '2',
        text: 'I\'ve analyzed Emily\'s Global Growth Fund within her ILP. You can inform her that the fund has shown a positive performance with 8.5% return over the past year and 42.1% over 5 years, which is above the benchmark.',
        sender: 'ai',
        agentType: 'policy-explainer',
        timestamp: new Date('2023-04-15T11:10:00'),
        chainOfThought: '1. Client has an ILP with Global Growth Fund\n2. Fund performance: 1yr: 8.5%, 3yr: 23.4%, 5yr: 42.1%\n3. Benchmark index for similar funds: 1yr: 7.2%, 5yr: 38.5%\n4. Fund allocation: 65% Equities, 20% Bonds, 10% Cash, 5% Others\n5. Current market conditions show volatility but long-term performance remains strong',
        documentReferences: [
          {
            id: 'doc5',
            title: 'Global Growth Fund Performance Report',
            type: 'financial',
            snippet: 'Returns: 1yr: 8.5%, 3yr: 23.4%, 5yr: 42.1% | Risk Rating: Moderate'
          }
        ]
      },
      {
        id: '3',
        text: 'Regarding Emily\'s concern about market volatility, you can reassure her that while short-term fluctuations are expected, her fund\'s allocation is well-diversified with 65% in equities, 20% in bonds, and 15% in other assets, providing a good balance between growth and stability. The 5-year performance suggests resilience during different market cycles. If she remains concerned, you could discuss potential adjustments to her investment strategy based on her current risk tolerance.',
        sender: 'ai',
        agentType: 'product-recommendation',
        timestamp: new Date('2023-04-15T11:11:00')
      }
    ],
    'compliance-check': []
  },
  '3': {
    'policy-explainer': [],
    'needs-assessment': [],
    'product-recommendation': [],
    'compliance-check': []
  }
};

interface ChatInterfaceProps {
  clientId: string;
  functionType: FunctionType;
  onGoBack: () => void;
  onDocumentExpand: (documentId: string | null) => void;
}

export default function ChatInterface({ 
  clientId, 
  functionType, 
  onGoBack,
  onDocumentExpand
}: ChatInterfaceProps) {
  const client = MOCK_CLIENT_DATA[clientId];
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load chat history when client or function changes
  useEffect(() => {
    if (clientId && functionType) {
      const history = MOCK_CHAT_HISTORY[clientId]?.[functionType] || [];
      setMessages(history);
    } else {
      setMessages([]);
    }
  }, [clientId, functionType]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message handler
  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;
    
    // Add user message
    const newUserMessage: ChatMessage = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setIsTyping(true);
    
    // Determine agent type based on function
    const agentType = functionType;
    
    // Simulate AI response after a delay
    setTimeout(() => {
      // Randomly decide if we should include a document reference (for demo purposes)
      const includeDoc = Math.random() > 0.6;
      const docRef: DocumentReference | undefined = includeDoc ? {
        id: `doc-${Date.now()}`,
        title: `Sample ${functionType.charAt(0).toUpperCase() + functionType.slice(1)} Document`,
        type: functionType === 'compliance-check' ? 'regulatory' : 'policy',
        snippet: 'This is a sample document snippet that would contain relevant information from a policy, financial report, or compliance regulation.'
      } : undefined;
      
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: `This is a simulated response from the ${agentType} agent: Based on the client's profile and your question "${text}", I would recommend focusing on relevant policy details and personalized advice you can provide during your next client interaction.`,
        sender: 'ai',
        timestamp: new Date(),
        agentType,
        chainOfThought: text.length > 50 ? 'This is a simulated chain-of-thought reasoning that would be provided by the specific agent:\n1. First, I analyzed the key aspects of the advisor\'s query\n2. Then I retrieved relevant client and policy information\n3. Next, I considered the client\'s profile data and financial situation\n4. Finally, I formulated advice for the advisor based on best practices' : undefined,
        documentReferences: docRef ? [docRef] : undefined
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Header with back button */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center mb-2">
          <button 
            onClick={onGoBack}
            className="mr-3 text-gray-500 hover:text-gray-700"
          >
            ← Back
          </button>
          <h2 className="text-xl font-semibold">
            {functionType.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
          </h2>
        </div>
        
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium">{client.name}</h3>
            <p className="text-sm text-gray-500">
              {client.age} years old • {client.occupation} • {client.dependents} dependents
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {client.insurancePolicies.map((policy, index) => (
              <span key={index} className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                {policy}
              </span>
            ))}
          </div>
        </div>
      </div>
      
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.map(message => (
          <Message 
            key={message.id}
            message={message}
            onDocumentClick={
              message.documentReferences?.length 
              ? (docId) => onDocumentExpand(docId) 
              : undefined
            }
          />
        ))}
        {isTyping && (
          <div className="flex items-center text-gray-500 text-sm ml-2 mt-2">
            <div className="dot-typing"></div>
            <span className="ml-2">AI is thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input area */}
      <ChatInput onSendMessage={handleSendMessage} />
    </div>
  );
} 