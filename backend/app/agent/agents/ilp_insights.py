# backend/app/agent/agents/ilp_insights.py
from typing import Dict, List, Any, Literal, TypedDict, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import tools
from agent.tools import market_data_tool, client_db_tool, document_retrieval_tool

# Define fund performance schema
class FundPerformance(BaseModel):
    """Performance data for an investment fund"""
    fund_name: str = Field(description="Name of the investment fund")
    risk_rating: str = Field(description="Risk rating of the fund")
    returns: Dict[str, float] = Field(description="Returns for different time periods (1y, 3y, 5y, etc.)")
    benchmark_comparison: Dict[str, float] = Field(description="Comparison to benchmark for different periods")
    asset_allocation: Dict[str, float] = Field(description="Current asset allocation percentages")
    top_holdings: List[Dict[str, Any]] = Field(description="Top holdings in the fund")

class MarketOutlook(BaseModel):
    """Market outlook and investment perspectives"""
    economic_environment: str = Field(description="Current economic environment assessment")
    market_trends: List[str] = Field(description="Key market trends")
    risk_factors: List[str] = Field(description="Key risk factors to monitor")
    opportunities: List[str] = Field(description="Potential investment opportunities")
    recommendation: str = Field(description="Overall recommendation for this type of fund")

class ILPInsightsOutput(BaseModel):
    """Output from the ILP Insights Agent"""
    response: str = Field(description="Natural language response analyzing fund performance")
    fund_performance: FundPerformance = Field(description="Structured fund performance data")
    market_outlook: MarketOutlook = Field(description="Market outlook assessment")
    document_references: List[Dict[str, str]] = Field(description="References to relevant documents")
    suggested_next_agent: Optional[str] = Field(description="Suggested next agent to handle the query")

# Create the ILP insights prompt
ilp_insights_system_prompt = """You are the ILP Insights Agent, an expert in investment-linked policies and fund analysis.

Your role is to:

1. Analyze investment fund performance data
2. Provide context for past performance and market trends
3. Explain asset allocation and portfolio composition
4. Assess risk-return characteristics of investments
5. Offer perspective on market outlook and investment strategy

When analyzing investment funds:
- Present performance in context of relevant benchmarks
- Explain the significance of asset allocation decisions
- Highlight key risk factors and potential opportunities
- Consider the client's risk profile and investment horizon
- Be balanced and objective in your assessment

Focus on helping financial advisors explain fund performance to their clients accurately.
Avoid making specific predictions about future returns.
Emphasize long-term performance over short-term fluctuations.

Your insights will help financial advisors have informed discussions about investment-linked policies with their clients.
"""

ilp_insights_prompt = ChatPromptTemplate.from_messages([
    ("system", ilp_insights_system_prompt),
    ("human", """
Query: {query}

Client Profile:
{client_profile}

Fund Data:
{fund_data}

Related Documents:
{related_documents}

Please analyze this fund performance data and provide insights that would help explain it to the client.
""")
])

# Initialize the model
ilp_insights_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

def ilp_insights_agent(state):
    """
    ILP Insights agent that analyzes investment fund performance
    """
    # Check if this agent has already processed this query
    if "ilp_insights" in state["agent_outputs"]:
        # Agent has already run, don't run again
        return state
    
    # Extract the relevant information from the state
    messages = state["messages"]
    client_id = state["client_id"]
    human_messages = [m for m in messages if isinstance(m, HumanMessage)]
    current_query = human_messages[-1].content if human_messages else ""
    
    # Get client information
    client_info = client_db_tool(client_id=client_id)
    
    # Format client profile
    client_profile = f"""
Name: {client_info.get('name', 'Unknown')}
Age: {client_info.get('age', 'Unknown')}
Risk Profile: {client_info.get('risk_profile', 'Unknown')}
"""
    
    # Determine which fund to analyze
    fund_name = None
    if "global growth" in current_query.lower():
        fund_name = "Global Growth Fund"
    elif "income" in current_query.lower():
        fund_name = "Income Plus Fund"
    
    # Get fund data
    fund_data_result = market_data_tool(fund_name=fund_name)
    
    # Format fund data
    fund_data = ""
    if "error" not in fund_data_result:
        fund_name = fund_data_result.get('fund_name', 'Unknown Fund')
        fund_data += f"""
Fund Name: {fund_name}
Risk Rating: {fund_data_result.get('risk_rating', 'Unknown')}
Fund Manager: {fund_data_result.get('fund_manager', 'Unknown')}

Performance:
"""
        for period, value in fund_data_result.get('performance', {}).items():
            fund_data += f"- {period}: {value}%\n"
        
        fund_data += "\nAsset Allocation:\n"
        for asset, percentage in fund_data_result.get('allocation', {}).items():
            fund_data += f"- {asset}: {percentage}%\n"
        
        fund_data += "\nTop Holdings:\n"
        for i, holding in enumerate(fund_data_result.get('top_holdings', [])[:5]):
            fund_data += f"- {holding.get('name', 'Unknown')}: {holding.get('percentage', 0)}%\n"
    else:
        fund_data = "No specific fund data available. Please provide the fund name for detailed analysis."
    
    # Retrieve related documents
    documents = document_retrieval_tool(
        query=f"investment fund {fund_name}" if fund_name else current_query,
        client_id=client_id,
        document_type="financial"
    )
    
    # Format related documents
    related_documents = ""
    document_references = []
    
    for doc in documents:
        related_documents += f"\nDocument: {doc.get('title', 'Unknown')}\n"
        related_documents += f"Type: {doc.get('type', 'Unknown')}\n"
        related_documents += f"Excerpt: {doc.get('content', '')[:200]}...\n"
        
        document_references.append({
            "id": doc.get("id", "doc-id"),
            "title": doc.get("title", "Financial Document"),
            "type": doc.get("type", "financial"),
            "snippet": doc.get("content", "")[:150] + "..."
        })
    
    if not related_documents:
        related_documents = "No specific fund documents found."
    
    # Prepare the input for the LLM
    input_values = {
        "query": current_query,
        "client_profile": client_profile,
        "fund_data": fund_data,
        "related_documents": related_documents
    }
    
    # Generate the fund analysis
    try:
        llm_response = ilp_insights_model.invoke(ilp_insights_prompt.format(**input_values))
        response_text = llm_response.content
        
        # In a real implementation, you would parse the LLM output to extract structured data
        # For this mock implementation, we'll create plausible structured data
        
        # Create structured fund performance data
        if "error" not in fund_data_result:
            fund_performance = FundPerformance(
                fund_name=fund_data_result.get('fund_name', 'Unknown Fund'),
                risk_rating=fund_data_result.get('risk_rating', 'Moderate'),
                returns={
                    k: v for k, v in fund_data_result.get('performance', {}).items()
                },
                benchmark_comparison={
                    "1y": 1.3,  # Outperformance by 1.3%
                    "3y": 1.9,
                    "5y": 3.6
                },
                asset_allocation=fund_data_result.get('allocation', {}),
                top_holdings=[
                    {"name": h.get("name"), "percentage": h.get("percentage")}
                    for h in fund_data_result.get('top_holdings', [])[:5]
                ]
            )
        else:
            # Default fund performance if no specific fund data
            fund_performance = FundPerformance(
                fund_name="Generic Balanced Fund",
                risk_rating="Moderate",
                returns={"1y": 7.0, "3y": 18.5, "5y": 32.0},
                benchmark_comparison={"1y": 0.5, "3y": 1.0, "5y": 2.0},
                asset_allocation={"Equities": 60, "Bonds": 30, "Cash": 10},
                top_holdings=[
                    {"name": "Diversified Holdings", "percentage": 100}
                ]
            )
        
        # Create market outlook
        market_outlook = MarketOutlook(
            economic_environment="Moderate growth with controlled inflation",
            market_trends=[
                "Central banks maintaining cautious monetary policy",
                "Ongoing digital transformation across sectors",
                "Increasing focus on sustainable investments"
            ],
            risk_factors=[
                "Geopolitical tensions affecting global trade",
                "Potential inflation pressures in certain economies",
                "Valuation concerns in some market segments"
            ],
            opportunities=[
                "Quality companies with strong cash flows",
                "Selective opportunities in emerging markets",
                "Companies benefiting from sustainability trends"
            ],
            recommendation="Maintain a diversified portfolio aligned with long-term financial goals and risk tolerance."
        )
        
        # Determine if we should suggest another agent
        suggested_next = None
        
        if "compliance" in current_query.lower() or "regulations" in current_query.lower():
            suggested_next = "compliance_check"
        elif "recommend" in current_query.lower() or "suitable" in current_query.lower():
            suggested_next = "product_suitability"
        
        # Create structured output
        output = {
            "response": response_text,
            "fund_performance": fund_performance.dict() if isinstance(fund_performance, BaseModel) else fund_performance,
            "market_outlook": market_outlook.dict() if isinstance(market_outlook, BaseModel) else market_outlook,
            "document_references": document_references,
            "suggested_next_agent": suggested_next
        }
        
    except Exception as e:
        # Fallback response if LLM call fails
        print(f"Error in ILP insights agent: {str(e)}")
        
        response_text = "## Fund Performance Analysis\n\n"
        
        if "error" not in fund_data_result:
            fund_name = fund_data_result.get('fund_name', 'Unknown Fund')
            response_text += f"Risk Rating: {fund_data_result.get('risk_rating', 'Moderate')}\n"
            response_text += f"Fund Manager: {fund_data_result.get('fund_manager', 'Unknown')}\n\n"
            
            response_text += "### Performance\n"
            for period, value in fund_data_result.get('performance', {}).items():
                response_text += f"{period.upper()} Return: {value}%\n"
            
            response_text += "\n### Asset Allocation\n"
            for asset, percentage in fund_data_result.get('allocation', {}).items():
                response_text += f"- {asset}: {percentage}%\n"
            
            response_text += "\n### Market Outlook\n"
            response_text += "The fund continues to perform well against its benchmark. "
            response_text += "Current market conditions suggest moderate growth potential with some volatility. "
            response_text += "The fund's diversified allocation provides good risk mitigation."
        else:
            response_text += "I don't have specific data for this fund. Please provide the fund name for a detailed analysis."
        
        # Create fallback structured data
        fund_performance = FundPerformance(
            fund_name=fund_data_result.get('fund_name', 'Unknown Fund') if "error" not in fund_data_result else "Unknown Fund",
            risk_rating=fund_data_result.get('risk_rating', 'Moderate') if "error" not in fund_data_result else "Moderate",
            returns=fund_data_result.get('performance', {}) if "error" not in fund_data_result else {"1y": 0, "3y": 0, "5y": 0},
            benchmark_comparison={"1y": 0, "3y": 0, "5y": 0},
            asset_allocation=fund_data_result.get('allocation', {}) if "error" not in fund_data_result else {"Equities": 0, "Bonds": 0, "Cash": 0},
            top_holdings=[
                {"name": h.get("name"), "percentage": h.get("percentage")}
                for h in fund_data_result.get('top_holdings', [])[:3]
            ] if "error" not in fund_data_result else []
        )
        
        market_outlook = MarketOutlook(
            economic_environment="Mixed economic indicators",
            market_trends=["Ongoing market volatility", "Sector rotation"],
            risk_factors=["Interest rate uncertainty", "Geopolitical tensions"],
            opportunities=["Selective quality companies", "Diversification"],
            recommendation="Maintain diversified portfolio aligned with risk tolerance"
        )
        
        # Create fallback output
        output = {
            "response": response_text,
            "fund_performance": fund_performance,
            "market_outlook": market_outlook,
            "document_references": document_references,
            "suggested_next_agent": None
        }
    
    # Add the response to messages
    messages.append(AIMessage(content=output["response"]))
    
    # Update the state
    state["messages"] = messages
    state["agent_path"].append("ilp_insights")
    state["agent_outputs"]["ilp_insights"] = output
    state["current_agent"] = "ilp_insights"
    
    # Save relevant information to shared memory
    if "shared_memory" not in state:
        state["shared_memory"] = {}
    
    # Handle both Pydantic model and dictionary formats
    fund_perf = output["fund_performance"]
    
    # Check if we're dealing with a Pydantic model or a dictionary
    if hasattr(fund_perf, 'dict'):
        # It's a Pydantic model, use attributes
        state["shared_memory"]["fund_performance"] = {
            "fund_name": fund_perf.fund_name,
            "returns": fund_perf.returns,
            "risk_rating": fund_perf.risk_rating
        }
    else:
        # It's already a dictionary, use dictionary access
        state["shared_memory"]["fund_performance"] = {
            "fund_name": fund_perf.get("fund_name", "Unknown Fund"),
            "returns": fund_perf.get("returns", {}),
            "risk_rating": fund_perf.get("risk_rating", "Unknown")
        }
    
    return state