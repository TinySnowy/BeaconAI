# test_agent.py
import os
import sys
import time
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the agent system
from agent.main import test_agent

# Define test cases
test_cases = [
    {
        "name": "Policy Explainer",
        "query": "Tell me about John Smith's life insurance policy",
        "client_id": "client-1",
        "function_type": "policy-explainer",
        "expected_agents": ["policy_explainer"]
    },
    {
        "name": "Needs Assessment",
        "query": "What are Sarah's financial needs?",
        "client_id": "client-2",
        "function_type": "needs-assessment",
        "expected_agents": ["client_profiler"]
    },
    {
        "name": "Product Recommendation",
        "query": "What insurance products would you recommend for Emily?",
        "client_id": "client-4",
        "function_type": "product-recommendation",
        "expected_agents": ["product_suitability"]
    },
    {
        "name": "Compliance Check",
        "query": "What compliance issues should I be aware of when recommending investment products?",
        "client_id": "client-3",
        "function_type": "compliance-check",
        "expected_agents": ["compliance_check"]
    },
    {
        "name": "Investment Fund Analysis",
        "query": "How has the Global Growth Fund been performing?",
        "client_id": "client-4",
        "function_type": "policy-explainer",
        "expected_agents": ["policy_explainer", "ilp_insights"]
    },
    {
        "name": "Upsell Opportunities",
        "query": "Are there any upsell opportunities for Michael?",
        "client_id": "client-3",
        "function_type": "needs-assessment",
        "expected_agents": ["client_profiler", "review_upsell"]
    },
    {
        "name": "Multi-Step Query",
        "query": "Analyze Emily's investment policy and check compliance requirements",
        "client_id": "client-4",
        "function_type": "needs-assessment",
        "expected_agents": ["client_profiler", "policy_explainer", "compliance_check"]
    }
]

def print_json_output(data, title=None):
    """Pretty print JSON data"""
    if title:
        print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2))

def print_separator(character="=", length=80):
    """Print a separator line"""
    print(f"\n{character * length}")

def display_structured_data(result, agent_name):
    """Display structured data from an agent output"""
    if agent_name not in result["agent_outputs"]:
        return
    
    agent_output = result["agent_outputs"][agent_name]
    
    # Check for specific agent types and their structured outputs
    if agent_name == "client_profiler" and "needs_assessment" in agent_output:
        print_json_output(agent_output["needs_assessment"], "NEEDS ASSESSMENT")
    
    elif agent_name == "product_suitability" and "recommended_products" in agent_output:
        print_json_output(agent_output["recommended_products"], "RECOMMENDED PRODUCTS")
    
    elif agent_name == "policy_explainer" and "policy_details" in agent_output:
        print_json_output(agent_output["policy_details"], "POLICY DETAILS")
    
    elif agent_name == "compliance_check" and "compliance_requirements" in agent_output:
        print_json_output(agent_output["compliance_requirements"], "COMPLIANCE REQUIREMENTS")
    
    elif agent_name == "ilp_insights" and "fund_performance" in agent_output:
        print_json_output({
            "fund_name": agent_output["fund_performance"].get("fund_name", ""),
            "risk_rating": agent_output["fund_performance"].get("risk_rating", ""),
            "returns": agent_output["fund_performance"].get("returns", {})
        }, "FUND PERFORMANCE")
    
    elif agent_name == "review_upsell":
        if "upsell_opportunities" in agent_output:
            print_json_output(agent_output["upsell_opportunities"], "UPSELL OPPORTUNITIES")
        if "next_steps" in agent_output:
            print("\n=== RECOMMENDED NEXT STEPS ===")
            for i, step in enumerate(agent_output["next_steps"], 1):
                print(f"{i}. {step}")

def run_tests(selected_tests=None):
    """Run all the test cases or specified tests"""
    results = []
    
    test_index = 1
    selected_test_cases = test_cases
    if selected_tests:
        selected_test_cases = [test_cases[i-1] for i in selected_tests if 0 < i <= len(test_cases)]
    
    print(f"\n{'=' * 30} TEST EXECUTION PLAN {'=' * 30}")
    for i, test in enumerate(selected_test_cases, 1):
        print(f"{i}. {test['name']}: '{test['query']}'")
    print('=' * 80)
    
    for test in selected_test_cases:
        print_separator("=")
        print(f"TEST CASE {test_index}: {test['name']}")
        print(f"QUERY: {test['query']}")
        print_separator("=")
        
        start_time = time.time()
        
        # Run the test
        result = test_agent(
            query=test["query"],
            client_id=test["client_id"],
            function_type=test["function_type"]
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Get list of non-coordinator agents
        actual_agents = [a for a in result["agent_path"] if a != "coordinator"]
        unique_agents = []
        for agent in actual_agents:
            if agent not in unique_agents:
                unique_agents.append(agent)
        
        # Check if expected agents were used
        expected_agents = test.get("expected_agents", [])
        missing_agents = [a for a in expected_agents if a not in unique_agents]
        unexpected_agents = [a for a in unique_agents if a not in expected_agents]
        
        # Print agent outputs
        print_separator("-")
        print(f"AGENT PATH: {' -> '.join(unique_agents)}")
        print(f"EXECUTION TIME: {duration:.2f} seconds")
        
        if missing_agents:
            print(f"\nMISSING EXPECTED AGENTS: {', '.join(missing_agents)}")
        
        if unexpected_agents:
            print(f"\nUNEXPECTED AGENTS: {', '.join(unexpected_agents)}")
        
        print_separator("-")
        
        # Display structured data from each agent
        for agent in unique_agents:
            display_structured_data(result, agent)
        
        # Print final response
        print_separator("-")
        print("FINAL RESPONSE:")
        print(result.get("final_response", "No final response generated"))
        
        # Save results for summary
        results.append({
            "test_case": test,
            "pass": not missing_agents,
            "agent_path": unique_agents,
            "duration": duration,
            "missing_agents": missing_agents,
            "unexpected_agents": unexpected_agents
        })
        
        test_index += 1
    
    return results

def print_test_summary(results):
    """Print a summary of the test results"""
    print_separator("=")
    print("TEST SUMMARY")
    print_separator("=")
    
    pass_count = sum(1 for r in results if r["pass"])
    
    print(f"Tests: {len(results)} | Passed: {pass_count} | Failed: {len(results) - pass_count}")
    print()
    
    for i, result in enumerate(results, 1):
        status = "✓ PASS" if result["pass"] else "✗ FAIL"
        print(f"{i}. {result['test_case']['name']}: {status}")
        print(f"   Query: {result['test_case']['query']}")
        print(f"   Agent Path: {' -> '.join(result['agent_path'])}")
        print(f"   Duration: {result['duration']:.2f} seconds")
        
        if result["missing_agents"]:
            print(f"   Missing Agents: {', '.join(result['missing_agents'])}")
        
        if result["unexpected_agents"]:
            print(f"   Unexpected Agents: {', '.join(result['unexpected_agents'])}")
        
        print()

if __name__ == "__main__":
    # Check for test selection in command line arguments
    selected_tests = None
    if len(sys.argv) > 1:
        try:
            selected_tests = [int(arg) for arg in sys.argv[1:]]
            print(f"Running selected tests: {selected_tests}")
        except ValueError:
            print("Invalid test numbers. Please provide test numbers as integers.")
            sys.exit(1)
    
    # Check if OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable is not set.")
        print("The test will run with mock responses only.")
        print("To use real LLM responses, set your API key:")
        print("export OPENAI_API_KEY=your_api_key_here")
        print()
    
    # Run the tests
    start_time = time.time()
    print(f"Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results = run_tests(selected_tests)
    
    # Print summary
    end_time = time.time()
    total_duration = end_time - start_time
    print(f"Total test duration: {total_duration:.2f} seconds")
    print_test_summary(results)