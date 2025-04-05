# AdvisorAI - Financial Advisor Assistant

AdvisorAI is an AI-powered assistant for insurance financial advisors, inspired by the architecture and concepts of FinRobot but tailored specifically for the insurance advisory sector.

## Project Overview

This project implements a Claude-like interface specifically designed for financial advisors to interact with clients. Each "project" in our interface corresponds to an individual client, with the ability to maintain separate conversation threads for different topics and needs.

### Core Features

- **Client-Centric Interface**: Manage multiple clients with separate conversation histories
- **Multi-thread Conversations**: Create purpose-specific conversation threads for each client
- **Specialized AI Agents**: Different AI agents for policy explanation, needs assessment, etc.
- **Context Panel**: View relevant policy documents, financial data, and compliance guides
- **Chain-of-Thought Reasoning**: Transparent AI reasoning process for advisor review
- **Client Categorization**: Organize clients by status and priority

## Interface Structure

1. **Left Sidebar: Client Management**
   - List of clients with search functionality and categorization
   - Clients categorized as active, pending review, prospects, etc.
   - "Add Client" button for creating new client profiles

2. **Main Content Area: AI Assistant Interaction**
   - Conversation interface with specialized AI agents
   - Multiple conversation threads per client for different purposes
   - Messages tagged by agent type with distinct colors/icons
   - Chain-of-thought reasoning in collapsible sections

3. **Right Panel: Context Display**
   - Shows relevant policy documents with key points
   - Displays client financial data and visualizations
   - Provides regulatory information when needed

## Architecture

AdvisorAI is built on a multi-layered architecture:

1. **Insurance AI Agents Layer**: Specialized agents for client profiling, product suitability, policy explanation, etc.
2. **Insurance LLM Algorithms Layer**: Fine-tuned models specific to insurance terminology and concepts
3. **LLMOps & DataOps Layer**: Manages data flow and model selection
4. **Foundation Models Layer**: Leverages powerful base LLMs for general capabilities

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AdvisorAI.git
cd AdvisorAI
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
AdvisorAI/
├── app/                  # Next.js app directory
│   ├── components/       # React components
│   ├── context/          # React context providers
│   ├── styles/           # CSS and styling files
│   ├── lib/              # Utility functions and shared code
│   ├── api/              # API routes
│   └── types/            # TypeScript type definitions
├── public/               # Static assets
└── ...config files
```

## Key UI Components

- **Dashboard**: Main interface with three-panel layout
- **Sidebar**: Client navigation with categorization
- **ChatInterface**: Main conversation area with thread support
- **ThreadSelector**: Horizontal navigation for client conversation threads
- **Message**: Individual message display with agent indicators and reasoning
- **ContextPanel**: Right panel with contextual information
- **ChatInput**: User input with suggested queries

## Deployment

The application can be deployed to Vercel, Netlify, or any other Next.js-compatible hosting service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.