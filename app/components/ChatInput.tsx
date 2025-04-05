'use client';

import { useState, FC } from 'react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
}

const ChatInput: FC<ChatInputProps> = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="border-t border-singlife-light bg-singlife-white p-4">
      <form onSubmit={handleSubmit} className="flex items-center">
        {/* Input field */}
        <input
          type="text"
          placeholder="Type your message..."
          className="flex-1 p-3 border border-singlife-light rounded-l-md focus:outline-none focus:ring-2 focus:ring-singlife-red"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        
        {/* Send button */}
        <button
          type="submit"
          className="bg-singlife-red text-white p-3 rounded-r-md hover:bg-singlife-dark focus:outline-none"
          disabled={!message.trim()}
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-5 w-5" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </form>
      
      {/* Suggested queries */}
      <div className="mt-3 flex flex-wrap gap-2">
        <button 
          onClick={() => onSendMessage("What insurance products would be suitable for this client's profile?")}
          className="text-xs bg-singlife-light hover:bg-singlife-light/80 text-singlife-dark px-3 py-1 rounded-full"
        >
          What insurance products would be suitable for this client's profile?
        </button>
        <button 
          onClick={() => onSendMessage("How should I explain the difference between term and whole life insurance to this client?")}
          className="text-xs bg-singlife-light hover:bg-singlife-light/80 text-singlife-dark px-3 py-1 rounded-full"
        >
          How should I explain the difference between term and whole life insurance?
        </button>
        <button 
          onClick={() => onSendMessage("What are the key compliance considerations for recommending investment-linked policies?")}
          className="text-xs bg-singlife-light hover:bg-singlife-light/80 text-singlife-dark px-3 py-1 rounded-full"
        >
          Key compliance considerations for ILPs
        </button>
      </div>
    </div>
  );
};

export default ChatInput; 