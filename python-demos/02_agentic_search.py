"""
Agentic Search Demo
Demonstrates AI-powered query understanding and automatic filtering with Azure AI Search

This script shows the agentic approach where the LLM:
1. Automatically analyzes complex queries and breaks them down
2. Intelligently determines appropriate categories without manual mapping
3. Executes parallel subqueries for better coverage
4. Provides unified, semantically ranked results

Based on Azure-Samples/azure-search-python-samples quickstart-agentic-retrieval
Reference: https://github.com/Azure-Samples/azure-search-python-samples/blob/main/Quickstart-Agentic-Retrieval/quickstart-agentic-retrieval.ipynb
"""

import os
import time
import json
import textwrap
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeAgent,
    KnowledgeAgentAzureOpenAIModel,
    KnowledgeAgentTargetIndex,
    AzureOpenAIVectorizerParameters
)
from azure.search.documents.agent import KnowledgeAgentRetrievalClient
from azure.search.documents.agent.models import (
    KnowledgeAgentRetrievalRequest,
    KnowledgeAgentMessage,
    KnowledgeAgentMessageTextContent,
    KnowledgeAgentIndexParams
)
from openai import AzureOpenAI

# Load environment variables
load_dotenv(override=True)

# Configuration - Use environment variables for security
# Based on Azure sample configuration
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")
AGENT_NAME = os.getenv("AZURE_SEARCH_AGENT_NAME")
AZURE_OPENAI_KNOWLEDGE_MODEL = os.getenv("AZURE_OPENAI_KNOWLEDGE_MODEL")
AZURE_OPENAI_KNOWLEDGE_DEPLOYMENT = os.getenv("AZURE_OPENAI_KNOWLEDGE_DEPLOYMENT")


# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")


# Hard-coded complex query for demo - multiple intents that agentic search should handle
USER_QUERY = """What are the networking requirements for AKS when an enterprise hub and spoke 
topology is being used and the Azure AI landing zone is in place? I need to understand 
the specific configuration, security considerations, and integration patterns."""

def create_knowledge_agent():
    """
    Create or update knowledge agent for agentic search using the Azure SDK
    The agent integrates with Azure OpenAI for query planning and understanding
    """
    print("\n1. Setting up knowledge agent...")
    
    try:
        # Create index client for agent management - using API key authentication
        index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_API_KEY))
        
        # Define the knowledge agent with Azure OpenAI integration
        agent = KnowledgeAgent(
            name=AGENT_NAME,
            models=[
                KnowledgeAgentAzureOpenAIModel(
                    azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                        resource_url=AZURE_OPENAI_ENDPOINT,
                        model_name=AZURE_OPENAI_KNOWLEDGE_MODEL,
                        deployment_name=AZURE_OPENAI_KNOWLEDGE_DEPLOYMENT,
                    )
                )
            ],
            target_indexes=[
                KnowledgeAgentTargetIndex(
                    index_name=INDEX_NAME,
                    default_reranker_threshold=2.5
                )
            ]
        )
        
        # Create or update the agent
        index_client.create_or_update_agent(agent)
        print(f"   ✅ Knowledge agent '{AGENT_NAME}' created or updated successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error setting up knowledge agent: {e}")
        return False

def agentic_retrieval_search(query):
    """
    Execute agentic retrieval with automatic query understanding using Azure SDK
    The LLM will handle all the complexity of query breakdown and category inference
    """
    print(f"\n=== Agentic Search Demo ===")
    print(f"Complex Query: {query}")
    
    start_time = time.time()
    
    try:
        # Step 1: Setup knowledge agent
        if not create_knowledge_agent():
            return None
        
        # Step 2: Create agent client for retrieval - using API key authentication
        print("\n2. Creating agent client for retrieval...")
        agent_client = KnowledgeAgentRetrievalClient(
            endpoint=SEARCH_ENDPOINT, 
            agent_name=AGENT_NAME, 
            credential=AzureKeyCredential(SEARCH_API_KEY)
        )
        
        # Step 3: Set up messages for conversation
        print("\n3. Preparing conversation messages...")
        instructions = """
        You are an intelligent search assistant specializing in Azure architecture and best practices.
        When processing queries, analyze the user's intent and provide comprehensive information
        covering security, architecture, networking, and operational considerations.
        """
        
        messages = [
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        # Step 4: Execute agentic retrieval using the SDK
        print("\n4. Executing agentic retrieval...")
        print("   🤖 LLM analyzing query and planning subqueries...")
        
        retrieval_result = agent_client.retrieve(
            retrieval_request=KnowledgeAgentRetrievalRequest(
                messages=[
                    KnowledgeAgentMessage(
                        role=msg["role"],
                        content=[KnowledgeAgentMessageTextContent(text=msg["content"])]
                    ) for msg in messages if msg["role"] != "system"
                ],
                target_index_params=[
                    KnowledgeAgentIndexParams(
                        index_name=INDEX_NAME, 
                        reranker_threshold=2.5
                    )
                ]
            )
        )
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Step 5: Process and display results
        print("\n5. Processing agentic results...")
        
        # Extract response content
        unified_result = retrieval_result.response[0].content[0].text if retrieval_result.response else ""
        references = retrieval_result.references or []
        activities = retrieval_result.activity or []
        
        # Display results
        print(f"\n=== Agentic Search Results ===")
        print(f"Execution time: {execution_time:.2f} ms")
        print(f"Total references found: {len(references)}")
        print(f"Number of activities executed: {len(activities)}")
        
        # Show LLM's query breakdown and execution plan
        if activities:
            print(f"\n🧠 LLM Query Breakdown & Execution Plan:")
            for i, activity in enumerate(activities, 1):
                activity_dict = activity.as_dict()
                activity_type = activity_dict.get("type", "Unknown")
                if activity_type == "AzureSearchQuery":
                    search_query = activity_dict.get("query", {}).get("search", "")
                    result_count = activity_dict.get("count", 0)
                    print(f"   {i}. Search Query: \"{search_query}\"")
                    print(f"      Type: {activity_type}")
                    print(f"      Results: {result_count}")
       
        
        # Show top references
        print(f"\nTop {min(3, len(references))} references:")
        for i, ref in enumerate(references[:3], 1):
            ref_dict = ref.as_dict()
            doc_key = ref_dict.get("doc_key", "Unknown")
            activity_source = ref_dict.get("activity_source", 0)
            
            print(f"\n{i}. Document: {doc_key}")
            print(f"   Activity Source: {activity_source}")
            print(f"   Reference ID: {ref_dict.get('id', 'N/A')}")
          # Generate natural language answer
        natural_answer = generate_natural_language_answer(query, retrieval_result, activities)
        
        # Highlight agentic advantages
        print(f"\n=== Agentic Search Advantages Demonstrated ===")
        print("✅ Automatic query decomposition (no manual breakdown needed)")
        print("✅ Intelligent LLM-powered query planning")
        print("✅ Parallel subquery execution (better coverage)")
        print("✅ Semantic understanding and ranking")
        print("✅ Unified result synthesis")
        print("✅ Context-aware conversation handling")
        print("✅ Natural language answer generation from search results")
        
        return {
            "execution_time_ms": execution_time,
            "result_count": len(references),
            "activities_executed": len(activities),
            "search_type": "agentic_retrieval",
            "activities": [activity.as_dict() for activity in activities],
            "unified_result": unified_result,
            "natural_answer": natural_answer
        }
        
    except Exception as e:
        print(f"Error in agentic search: {e}")
        return None

# Function replaced by generate_natural_language_answer for better comprehensive answers

def generate_natural_language_answer(query, retrieval_result, activities):
    """
    Generate a comprehensive natural language answer using Azure OpenAI
    based on the agentic search results and retrieved documents
    """
    print(f"\n6. Generating natural language answer...")
    
    try:
        # Create Azure OpenAI client with API key
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT
        )
        
        # Extract relevant content from retrieval results
        references_content = ""
        if retrieval_result.references:
            for i, ref in enumerate(retrieval_result.references[:5], 1):  # Top 5 references
                ref_dict = ref.as_dict()
                if 'content' in ref_dict:
                    references_content += f"\nReference {i}: {ref_dict['content'][:500]}...\n"
        
        # Create comprehensive prompt for natural language answer
        system_prompt = """You are an expert Azure architect and consultant. Based on the provided search results and references, 
        provide a comprehensive, well-structured answer to the user's question. Your response should:
        
        1. Directly address the specific question asked
        2. Be technically accurate and detailed
        3. Include practical implementation guidance
        4. Cover security, networking, and operational considerations
        5. Be organized with clear sections and bullet points
        6. Include specific Azure service recommendations where appropriate
        7. Cite which reference sections inform your answer via the reference_link urls

        Format your response in a clear, professional manner suitable for technical stakeholders."""
        
        user_prompt = f"""
        Original Question: {query}
        
        Search Results and References:
        {references_content}
        
        Please provide a comprehensive answer to the original question based on these search results.
        """
        
        # Generate comprehensive answer
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_MODEL,
            messages=messages,
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=3000
        )
        
        answer = response.choices[0].message.content
        
        print(f"\n🎯 Natural Language Answer:")
        print("=" * 80)
        
        # Format the answer with proper line breaks
        formatted_answer = textwrap.fill(answer, width=100, break_long_words=False, break_on_hyphens=False)
        print(formatted_answer)
        
        print("=" * 80)
        
        return answer
        
    except Exception as e:
        print(f"Error generating natural language answer: {e}")
        return None

def compare_with_traditional():
    """Show comparison with what traditional search would require"""
    print(f"\n=== Comparison: What Traditional Search Would Require ===")
    print("🔧 Manual Requirements:")
    print("   - Parse 'AKS networking requirements'")
    print("   - Map 'enterprise hub and spoke topology' → Architecture, Networking categories")
    print("   - Map 'Azure AI landing zone' → AI and Machine Learning, Infrastructure categories")
    print("   - Map 'security considerations' → Security category")
    print("   - Map 'integration patterns' → Integration category")
    print("   - Construct complex filter with multiple OR conditions")
    print("   - Execute single query (may miss nuanced enterprise requirements)")
    print("   - Manually merge and rank results")
    print("   - Parse raw search results to extract relevant information")
    print("   - Manually synthesize a coherent answer from fragmented results")
    print()
    print("🤖 Agentic Approach:")
    print("   - LLM automatically understands AKS networking context")
    print("   - Intelligently breaks down enterprise topology requirements")
    print("   - Automatically identifies AI landing zone implications")
    print("   - Executes parallel searches for comprehensive coverage")
    print("   - Provides unified, semantically ranked results")
    print("   - Generates natural language answer directly from search results")
    print("   - Synthesizes coherent, actionable guidance from multiple sources")

if __name__ == "__main__":
    print("Starting Agentic Search Demo")
    print("=" * 50)
    print("Based on Azure-Samples/azure-search-python-samples")
    print("Reference: https://github.com/Azure-Samples/azure-search-python-samples")
    
    # Verify configuration
    if not SEARCH_ENDPOINT or SEARCH_ENDPOINT == "https://your-search-service.search.windows.net":
        print("⚠️  Please set AZURE_SEARCH_ENDPOINT environment variable")
        print("   Example: export AZURE_SEARCH_ENDPOINT='https://your-service.search.windows.net'")
        exit(1)
    
    if not SEARCH_API_KEY:
        print("⚠️  Please set AZURE_SEARCH_API_KEY environment variable")
        print("   Example: export AZURE_SEARCH_API_KEY='your-search-api-key'")
        exit(1)
    
    if not AZURE_OPENAI_ENDPOINT:
        print("⚠️  Please set AZURE_OPENAI_ENDPOINT environment variable")
        print("   Example: export AZURE_OPENAI_ENDPOINT='https://your-openai.openai.azure.com'")
        exit(1)
    
    print("ℹ️  Using API key for Azure Search and managed identity for Azure OpenAI")
    
    # Show what we're comparing against
    compare_with_traditional()
      # Execute agentic search
    result = agentic_retrieval_search(USER_QUERY)
    
    if result:
        print(f"\n🏁 Agentic search completed in {result['execution_time_ms']:.2f} ms")
        print(f"   Executed {result['activities_executed']} activities")
        print(f"   Found {result['result_count']} references")
        
        if result['activities']:
            print(f"\n📊 Query Execution Summary:")
            for activity in result['activities']:
                if activity.get('type') == 'AzureSearchQuery':
                    search_query = activity.get('query', {}).get('search', '')
                    result_count = activity.get('count', 0)
                    print(f"   • \"{search_query}\" → {result_count} results")
    else:
        print("❌ Agentic search failed")
