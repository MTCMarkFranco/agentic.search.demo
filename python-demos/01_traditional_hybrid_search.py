"""
Traditional Hybrid Search Demo
Demonstrates manual filtering and simple query processing with Azure AI Search SDK

This script shows the traditional approach where developers must:
1. Manually analyze the query to determine appropriate categories
2. Manually construct filters
3. Handle single query execution
4. Perform basic result processing
"""

import os
import time
import json
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - Use environment variables for security
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY") 
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
INDEX_NAME = "index-arch-data"

# Hard-coded simple query for demo
USER_QUERY = "What are the networking requirements for AKS?"

def create_openai_client():
    """Create Azure OpenAI client for LLM-based categorization"""
    try:
        if OPENAI_API_KEY:
            return AzureOpenAI(
                azure_endpoint=OPENAI_ENDPOINT,
                api_key=OPENAI_API_KEY,
                api_version="2024-12-01-preview"
            )
        else:
            # Use managed identity
            credential = DefaultAzureCredential()
            return AzureOpenAI(
                azure_endpoint=OPENAI_ENDPOINT,
                azure_ad_token_provider=credential,
                api_version="2024-12-01-preview"
            )
    except Exception as e:
        print(f"Error creating OpenAI client: {e}")
        raise
    """Create Azure AI Search client with proper authentication"""
    try:
        # Prefer managed identity over API key for production
        if SEARCH_API_KEY:
            credential = AzureKeyCredential(SEARCH_API_KEY)
            print("Using API key authentication")
        else:
            credential = DefaultAzureCredential()
            print("Using managed identity authentication")
        
        return SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=INDEX_NAME,
            credential=credential
        )
    except Exception as e:
        print(f"Error creating search client: {e}")
        raise

def create_search_client():
    """Create Azure AI Search client with proper authentication"""
    try:
        # Prefer managed identity over API key for production
        if SEARCH_API_KEY:
            credential = AzureKeyCredential(SEARCH_API_KEY)
            print("Using API key authentication")
        else:
            credential = DefaultAzureCredential()
            print("Using managed identity authentication")
        
        return SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=INDEX_NAME,
            credential=credential
        )
    except Exception as e:
        print(f"Error creating search client: {e}")
        raise

def llm_category_mapping(query):
    """
    LLM-powered category inference - more intelligent than manual keyword mapping
    Still shows traditional approach limitations vs agentic search
    """
    try:
        print("   🤖 Using LLM for category detection...")
        
        openai_client = create_openai_client()
        
        system_prompt = f"""
        You are an expert at categorizing Azure architecture and technology content. 
        You will be given a search query and you must return the most relevant categories.
        
        IMPORTANT: Only return relevant categories, nothing else except the categories in the form of a JSON Array of Strings
        IMPORTANT: When identifying categories, try to suggest as few categories as possible, keeping the relevancy high.
        IMPORTANT: Only add the Miscellaneous category if the content does not fit into any of the other categories.
        IMPORTANT: Do not add any other text or explanation, always return the categories in the form of a JSON Array of Strings in this structure:
        {{"categories": ["category1", "category2", "category3"]}}

        Select only from the categories below:

        Infrastructure, Architecture, Security, Networking, Compliance, Integration, Data, 
        Operation, Backup, Licenses, Logging, Exception Handling, AI and Machine Learning, 
        Analytics, Compute, Containers, Developer Tools, DevOps, Hybrid Cloud, Identity, 
        IoT, Messaging, Monitoring, Storage, Web, Migration, Virtual Desktop Infrastructure, 
        Resiliency, Disaster Recovery, Scaling, Performance, Miscellaneous
        """
        
        user_query = f"Categorize this search query: {query}"
        
        completion = openai_client.chat.completions.create(
            model=OPENAI_DEPLOYMENT,
            max_tokens=800,
            temperature=0.3,  # Lower temperature for more consistent categorization
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False,
            response_format={"type": "json_object"}
        )
        
        json_string = completion.choices[0].message.content
        data = json.loads(json_string)
        categories = data.get("categories", ["Miscellaneous"])
        
        print(f"   ✅ LLM detected categories: {categories}")
        return categories
        
    except Exception as e:
        print(f"   ⚠️  LLM categorization failed, using fallback: {e}")
        return manual_category_mapping_fallback(query)

def manual_category_mapping_fallback(query):
    """
    Fallback manual category inference - shows original limitations
    """
    query_lower = query.lower()
    categories = []
      # Manual keyword-to-category mapping (incomplete and error-prone)
    category_keywords = {
        "Networking": ["network", "networking", "vpc", "subnet", "firewall", "dns", "ingress", "load balancer"],
        "Containers": ["container", "docker", "kubernetes", "k8s", "pod", "aks", "cluster"],
        "Architecture": ["architecture", "design", "pattern", "structure", "topology", "hub", "spoke"],
        "Security": ["security", "secure", "protection", "threat", "vulnerability"],
        "Infrastructure": ["infrastructure", "infra", "deployment", "provisioning", "landing zone"],
        "Compliance": ["compliance", "regulatory", "audit", "governance"],
        "Monitoring": ["monitoring", "observability", "logging", "metrics"],
        "DevOps": ["devops", "ci/cd", "pipeline", "automation"],
        "AI and Machine Learning": ["ai", "machine learning", "ml", "artificial intelligence"]
    }
    
    # Simple keyword matching - limited accuracy
    for category, keywords in category_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            categories.append(category)
    
    # Default fallback if no categories detected
    if not categories:
        categories = ["Miscellaneous"]
    
    return categories

def build_filter_expression(categories):
    """Build OData filter expression for categories"""
    if not categories:
        return None
    
    # Build filter for collection field
    category_filters = [f"category/any(c: c eq '{cat}')" for cat in categories]
    return " or ".join(category_filters)

def generate_natural_language_answer(query, documents):
    """
    Generate a comprehensive natural language answer using Azure OpenAI
    based on the traditional search results
    
    Args:
        query (str): The original user query
        documents (list): List of search result documents
    
    Returns:
        str: Natural language answer or None if generation fails
    """
    print(f"\n5. Generating natural language answer...")
    
    try:
        # Create Azure OpenAI client
        openai_client = create_openai_client()
        
        # Extract relevant content from search results (take full content, not truncated)
        references_content = ""
        if documents:
            for i, doc in enumerate(documents[:5], 1):  # Top 5 results
                # Get full content instead of truncated version
                content = doc.get('full_content', doc.get('content', ''))
                if content.endswith('...'):
                    # Remove truncation indicator for LLM processing
                    content = content[:-3]
                
                references_content += f"\nReference {i} - {doc.get('title', 'Untitled')}:\n"
                references_content += f"Categories: {', '.join(doc.get('categories', []))}\n"
                references_content += f"Content: {content}\n"
                references_content += "-" * 50 + "\n"
        
        if not references_content.strip():
            return "I apologize, but I couldn't find sufficient relevant information to answer your question based on the search results."
        
        # Create comprehensive prompt for natural language answer
        system_prompt = """You are an expert Azure architect and consultant. Based on the provided search results and references, 
        provide a comprehensive, well-structured answer to the user's question. Your response should:
        
        1. Directly address the specific question asked
        2. Be technically accurate and detailed
        3. Include practical implementation guidance where applicable
        4. Cover security, networking, and operational considerations as relevant
        5. Be organized with clear sections and bullet points
        6. Include specific Azure service recommendations where appropriate
        7. Cite which reference sections inform your answer via the reference_link urls
        
        Format your response in a clear, professional manner suitable for technical stakeholders.
        Keep your answer focused and concise while being comprehensive."""
        
        user_prompt = f"""
        Original Question: {query}
        
        Search Results and References:
        {references_content}
        
        Please provide a comprehensive answer to the original question based on these search results. 
        Reference the specific sources that support your recommendations.
        """
        
        # Generate natural language response
        completion = openai_client.chat.completions.create(
            model=OPENAI_DEPLOYMENT,
            max_tokens=1500,  # Allow for comprehensive responses
            temperature=0.3,  # Lower temperature for more focused, factual responses
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        natural_answer = completion.choices[0].message.content
        print(f"   ✅ Generated natural language answer ({len(natural_answer)} characters)")
        
        return natural_answer
        
    except Exception as e:
        print(f"   ⚠️  Natural language answer generation failed: {e}")
        return f"I found {len(documents)} relevant results for your query, but encountered an issue generating a comprehensive answer. Please review the search results above for detailed information."

def traditional_hybrid_search(query):
    """
    Traditional hybrid search implementation
    Requires manual category detection and filter construction
    """
    print(f"\n=== Traditional Hybrid Search Demo ===")
    print(f"Query: {query}")
    
    start_time = time.time()
    
    try:        # Step 1: LLM-powered category inference (still traditional approach)
        print("\n1. LLM-powered category detection...")
        categories = llm_category_mapping(query)
        print(f"   Detected categories: {categories}")
        
        # Step 2: Manual filter construction
        print("\n2. Building manual filter...")
        filter_expr = build_filter_expression(categories)
        print(f"   Filter expression: {filter_expr}")
        
        # Step 3: Create search client
        search_client = create_search_client()
        
        # Step 4: Execute single hybrid search
        print("\n3. Executing hybrid search...")
        search_options = {
            "query_type": "semantic",
            "semantic_configuration_name": "my-semantic-config",
            "top": 10,
            "select": ["chunk_id", "chunk_title", "content", "category", "url"],
            "include_total_count": True
        }
        
        # Add manual filter if categories detected
        if filter_expr:
            search_options["filter"] = filter_expr
        
        # Single query execution - no parallel processing
        results = search_client.search(search_text=query, **search_options)
          # Step 5: Process results manually
        print("\n4. Processing results...")
        documents = []
        total_count = 0
        
        for result in results:
            full_content = result.get("content", "")
            documents.append({
                "chunk_id": result.get("chunk_id", ""),
                "title": result.get("chunk_title", ""),
                "content": full_content,
                "full_content": full_content,  # Store full content for natural language generation
                "categories": result.get("category", []),
                "score": result.get("@search.score", 0.0),
                "reference_link": result.get("url", "")})
            total_count += 1
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Step 6: Generate natural language answer
        natural_answer = None
        if documents:
            natural_answer = generate_natural_language_answer(query, documents)
        
        # Display results
        print(f"\n=== Traditional Search Results ===")
        print(f"Execution time: {execution_time:.2f} ms")
        print(f"Total results: {total_count}")
        print(f"Applied categories filter: {categories}")
        print(f"Search strategy: Single hybrid query (keyword + vector + semantic)")
        
        # Display natural language answer if generated
        if natural_answer:
            print(f"\n=== Natural Language Answer ===")
            print(natural_answer)
        
        print(f"\nTop {min(3, len(documents))} results:")
        for i, doc in enumerate(documents[:3], 1):
            print(f"\n{i}. {doc['title']}")
            print(f"   Score: {doc['score']:.4f}")
            print(f"   Categories: {doc['categories']}")
            print(f"   Content: {doc['content']}")
        
        # Highlight limitations
        print(f"\n=== Traditional Search Limitations (Even with LLM Answer Generation) ===")
        print("- Still requires separate LLM calls for categorization AND answer generation")
        print("- Single query execution (no parallel processing)")
        print("- Manual filter construction and result processing")
        print("- No integrated query understanding and breakdown")
        print("- No conversation context support")
        print("- Additional complexity and latency from multiple separate LLM calls")
        print("- Manual orchestration of search -> answer generation pipeline")
        
        return {
            "execution_time_ms": execution_time,
            "result_count": total_count,
            "categories_used": categories,
            "search_type": "traditional_hybrid",
            "natural_answer": natural_answer
        }
        
    except Exception as e:
        print(f"Error in traditional search: {e}")
        return None

if __name__ == "__main__":
    print("Starting Traditional Hybrid Search Demo")
    print("=" * 50)
      # Verify configuration
    if not SEARCH_ENDPOINT or SEARCH_ENDPOINT == "https://your-search-service.search.windows.net":
        print("⚠️  Please set AZURE_SEARCH_ENDPOINT environment variable")
        print("   Example: export AZURE_SEARCH_ENDPOINT='https://your-service.search.windows.net'")
        exit(1)
    
    if not OPENAI_ENDPOINT or OPENAI_ENDPOINT == "https://your-openai-service.openai.azure.com":
        print("⚠️  Please set AZURE_OPENAI_ENDPOINT environment variable")
        print("   Example: export AZURE_OPENAI_ENDPOINT='https://your-openai.openai.azure.com'")
        exit(1)
    
    if not SEARCH_API_KEY:
        print("ℹ️  No search API key provided - attempting to use managed identity")
    
    if not OPENAI_API_KEY:
        print("ℹ️  No OpenAI API key provided - attempting to use managed identity")    # Execute traditional search
    result = traditional_hybrid_search(USER_QUERY)
    
    if result:
        print(f"\n🏁 Traditional search (with LLM categorization + answer generation) completed in {result['execution_time_ms']:.2f} ms")
        print(f"   Found {result['result_count']} results using LLM-powered category detection")
        print(f"   Generated natural language answer: {'Yes' if result.get('natural_answer') else 'No'}")
        print(f"   Note: Requires multiple separate LLM calls + manual search orchestration")
    else:
        print("❌ Traditional search failed")
