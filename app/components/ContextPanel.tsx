'use client';

import { useState, useEffect } from 'react';

// Mock client documents
const MOCK_CLIENT_DOCUMENTS: Record<string, any[]> = {
  '1': [
    { 
      id: 'doc1', 
      title: 'Term Life Insurance Policy', 
      type: 'policy', 
      content: 'This Term Life Insurance policy provides coverage for a specified term of 20 years. Sum assured: $500,000. Premium: $1,200/year...',
      highlights: ['Coverage Term: 20 years', 'Sum Assured: $500,000', 'Premium: $1,200/year']
    },
    { 
      id: 'doc2', 
      title: 'Health Insurance Policy', 
      type: 'policy',
      content: 'This Health Insurance policy provides coverage for hospitalization, surgery, and outpatient treatments...',
      highlights: ['Coverage: Hospitalization', 'Annual Limit: $100,000', 'Deductible: $1,000']
    }
  ],
  '2': [
    { 
      id: 'doc3', 
      title: 'Whole Life Insurance Policy', 
      type: 'policy',
      content: 'This Whole Life Insurance policy provides lifelong coverage with a savings component...',
      highlights: ['Lifelong Coverage', 'Sum Assured: $200,000', 'Cash Value: Accumulates over time']
    }
  ]
};

// Mock client financial data for ILP performance
const MOCK_FINANCIAL_DATA: Record<string, any> = {
  '4': {
    ilpPerformance: {
      fundName: 'Global Growth Fund',
      returns: {
        '1yr': 8.5,
        '3yr': 23.4,
        '5yr': 42.1,
        'ytd': 3.2
      },
      allocation: [
        { category: 'Equities', percentage: 65 },
        { category: 'Bonds', percentage: 20 },
        { category: 'Cash', percentage: 10 },
        { category: 'Others', percentage: 5 }
      ]
    }
  }
};

// Mock compliance regulations
const MOCK_REGULATIONS = [
  {
    id: 'reg1',
    title: 'MAS Notice FAA-N16',
    description: 'Guidelines on Recommendations: Financial advisers should recommend suitable products to clients based on their needs, objectives, and financial situation.',
    link: '#'
  },
  {
    id: 'reg2',
    title: 'FAIR Principles',
    description: 'Financial advisers should act in the best interest of the client, adhere to clear and transparent disclosure, and ensure recommendations are suitable.',
    link: '#'
  }
];

// Mock document data
const MOCK_DOCUMENTS: Record<string, any> = {
  'doc1': {
    id: 'doc1',
    title: 'Term Life Insurance Policy',
    type: 'policy', 
    client: '1',
    issueDate: '2021-03-15',
    content: `
# Term Life Insurance Policy

**Policy Number:** TL-12345678
**Insured:** John Smith
**Coverage Amount:** $500,000
**Term:** 20 years
**Premium:** $1,200/year (paid annually)
**Issue Date:** March 15, 2021
**Expiry Date:** March 15, 2041

## Key Policy Provisions:

### 1. Death Benefit
The Company will pay the designated beneficiary the Coverage Amount upon receipt of proof that the insured died while this policy was in force.

### 2. Premium Payments
Premiums are payable annually on the policy anniversary date. A 30-day grace period is provided.

### 3. Beneficiary
Primary: Sarah Smith (Wife) - 100%
Contingent: Michael Smith (Son) - 50%, Emily Smith (Daughter) - 50%

### 4. Exclusions
- Suicide within first 2 years
- Material misrepresentation in application
- War or act of war

### 5. Conversion Option
This policy may be converted to a permanent life insurance policy without evidence of insurability before age 65 or the end of the term period, whichever comes first.

### 6. Renewability
This policy is renewable to age 80 at increased premiums without evidence of insurability.
    `
  },
  'doc4': {
    id: 'doc4',
    title: 'Estate Planning Checklist',
    type: 'financial',
    client: '4',
    issueDate: '2023-01-10',
    content: `
# Estate Planning Checklist

## Essential Documents

1. **Will**
   - Designates executor
   - Names guardians for minor children
   - Specifies distribution of assets
   - Should be reviewed every 3-5 years

2. **Trust**
   - Revocable living trust to avoid probate
   - Special needs trust if applicable
   - Consider tax implications

3. **Power of Attorney**
   - Financial POA
   - Durable POA (remains in effect if incapacitated)
   - Limited vs. general POA

4. **Healthcare Directive**
   - Living will
   - Healthcare proxy designation
   - HIPAA authorization

5. **Beneficiary Designations**
   - Life insurance policies
   - Retirement accounts
   - Transfer-on-death accounts
   - Should be reviewed annually

## For High Net Worth Individuals

- Estate tax planning strategies
- Gifting strategies
- Charitable remainder trusts
- Life insurance trust
- Family limited partnerships

## Digital Assets

- Inventory of online accounts
- Password manager information
- Digital executor designation
- Social media account instructions

## Special Considerations for Physicians

- Medical practice succession planning
- Malpractice insurance tail coverage
- Student loan death provisions
- Professional corporation handling
    `
  },
  'doc5': {
    id: 'doc5',
    title: 'Global Growth Fund Performance Report',
    type: 'financial',
    client: '4',
    issueDate: '2023-04-01',
    content: `
# Global Growth Fund Performance Report

## Fund Overview
**Fund Name:** Global Growth Fund
**Inception Date:** January 15, 2010
**Fund Manager:** Jane Williams
**Risk Rating:** Moderate
**Investment Objective:** Long-term capital growth

## Performance Summary

| Period | Return | Benchmark | +/- Benchmark |
|--------|--------|-----------|---------------|
| 1 Year | 8.5%   | 7.2%      | +1.3%         |
| 3 Year | 23.4%  | 21.5%     | +1.9%         |
| 5 Year | 42.1%  | 38.5%     | +3.6%         |
| YTD    | 3.2%   | 2.9%      | +0.3%         |

## Asset Allocation

- Equities: 65%
  - US: 30%
  - Europe: 15%
  - Asia Pacific: 12%
  - Emerging Markets: 8%
- Bonds: 20% 
  - Government: 10%
  - Corporate: 10%
- Cash: 10%
- Others: 5%

## Top 10 Holdings

1. Apple Inc. (3.5%)
2. Microsoft Corp. (3.2%)
3. Amazon.com Inc. (2.8%)
4. Alphabet Inc. (2.5%)
5. Taiwan Semiconductor (2.0%)
6. Nestlé S.A. (1.8%)
7. Samsung Electronics (1.5%)
8. ASML Holding (1.4%)
9. Tesla Inc. (1.3%)
10. Johnson & Johnson (1.2%)

## Market Commentary

The fund has performed well against a backdrop of market volatility, delivering above-benchmark returns across all time periods. The overweight position in technology and healthcare sectors has contributed positively to performance.

Economic indicators suggest continued but moderate growth globally, with inflation pressures beginning to ease in major economies. Central banks are expected to maintain a cautious approach to monetary policy.

## Outlook

We maintain a positive outlook for global equities, although expect returns to moderate from the exceptional performance seen in recent years. The fund continues to focus on companies with strong cash flow generation, robust balance sheets, and sustainable competitive advantages.

We have slightly reduced exposure to higher-valuation growth stocks while incrementally increasing allocation to select value opportunities and quality defensive names as a hedge against potential volatility.
    `
  }
};

interface ContextPanelProps {
  clientId: string | null;
  documentId: string | null;
  onClose: () => void;
}

export default function ContextPanel({ clientId, documentId, onClose }: ContextPanelProps) {
  const [document, setDocument] = useState<any>(null);
  
  useEffect(() => {
    if (documentId && MOCK_DOCUMENTS[documentId]) {
      setDocument(MOCK_DOCUMENTS[documentId]);
    } else {
      setDocument(null);
    }
  }, [documentId]);
  
  // Function to convert markdown-like content to basic HTML
  const formatContent = (content: string) => {
    if (!content) return '';
    
    // Handle headers
    content = content.replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold my-3">$1</h1>');
    content = content.replace(/^## (.+)$/gm, '<h2 class="text-lg font-semibold my-2">$1</h2>');
    content = content.replace(/^### (.+)$/gm, '<h3 class="text-md font-medium my-2">$1</h3>');
    
    // Handle bold text
    content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Handle lists
    content = content.replace(/^\- (.+)$/gm, '<li class="ml-4 mb-1">$1</li>');
    content = content.replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 mb-1"><span class="font-medium">$1.</span> $2</li>');
    
    // Handle paragraphs
    content = content.replace(/\n\n/g, '<br><br>');
    
    return content;
  };
  
  const getDocumentTypeLabel = (type: string) => {
    switch (type) {
      case 'policy':
        return { text: 'Insurance Policy', icon: '📄', bgColor: 'bg-blue-100', textColor: 'text-blue-800' };
      case 'financial':
        return { text: 'Financial Document', icon: '📊', bgColor: 'bg-green-100', textColor: 'text-green-800' };
      case 'regulatory':
        return { text: 'Regulatory Document', icon: '⚖️', bgColor: 'bg-amber-100', textColor: 'text-amber-800' };
      default:
        return { text: 'Document', icon: '📎', bgColor: 'bg-gray-100', textColor: 'text-gray-800' };
    }
  };
  
  return (
    <div className="w-1/2 border-l border-gray-200 h-full bg-white flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-medium">Document Viewer</h2>
          {document && (
            <div className="flex items-center mt-1">
              <span className={`text-xs px-2 py-0.5 rounded-full inline-block ${
                getDocumentTypeLabel(document.type).bgColor
              } ${
                getDocumentTypeLabel(document.type).textColor
              }`}>
                {getDocumentTypeLabel(document.type).icon} {getDocumentTypeLabel(document.type).text}
              </span>
              <span className="text-xs text-gray-500 ml-2">Issue Date: {document.issueDate}</span>
            </div>
          )}
        </div>
        <button 
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
      
      {/* Document content */}
      <div className="flex-1 overflow-y-auto p-4">
        {document ? (
          <div>
            <h1 className="text-2xl font-bold mb-4">{document.title}</h1>
            <div 
              className="prose prose-sm max-w-none" 
              dangerouslySetInnerHTML={{ __html: formatContent(document.content) }}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            {documentId ? (
              <p>Document not found</p>
            ) : (
              <p>Select a document to view details</p>
            )}
          </div>
        )}
      </div>
      
      {/* Actions */}
      {document && (
        <div className="border-t border-gray-200 p-3 bg-gray-50 flex justify-end">
          <button className="text-sm text-gray-600 border border-gray-300 rounded px-3 py-1 mr-2 hover:bg-gray-200">
            Download
          </button>
          <button className="text-sm text-white bg-indigo-600 rounded px-3 py-1 hover:bg-indigo-700">
            Share with Client
          </button>
        </div>
      )}
    </div>
  );
} 