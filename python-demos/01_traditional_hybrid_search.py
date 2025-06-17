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
import chainlit as cl
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
        raise Exception(f"Error creating OpenAI client: {e}")

def create_search_client():
    """Create Azure AI Search client with proper authentication"""
    try:
        # Prefer managed identity over API key for production
        if SEARCH_API_KEY:
            credential = AzureKeyCredential(SEARCH_API_KEY)
        else:
            credential = DefaultAzureCredential()
        
        return SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=INDEX_NAME,
            credential=credential
        )
    except Exception as e:
        raise Exception(f"Error creating search client: {e}")

async def llm_category_mapping(query):
    """
    LLM-powered category inference - more intelligent than manual keyword mapping
    Still shows traditional approach limitations vs agentic search
    """
    try:
        await cl.Message(content="   🤖 Using LLM for category detection...").send()
        
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
        
        await cl.Message(content=f"   ✅ LLM detected categories: {categories}").send()
        return categories
        
    except Exception as e:
        await cl.Message(content=f"   ⚠️  LLM categorization failed, using fallback: {e}").send()
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

async def generate_natural_language_answer(query, documents):
    """
    Generate a comprehensive natural language answer using Azure OpenAI
    based on the traditional search results
    
    Args:
        query (str): The original user query
        documents (list): List of search result documents
    
    Returns:
        str: Natural language answer or None if generation fails
    """
    await cl.Message(content=f"\n5. Generating natural language answer...").send()
    
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
        await cl.Message(content=f"   ✅ Generated natural language answer ({len(natural_answer)} characters)").send()
        
        return natural_answer
        
    except Exception as e:
        await cl.Message(content=f"   ⚠️  Natural language answer generation failed: {e}").send()
        return f"I found {len(documents)} relevant results for your query, but encountered an issue generating a comprehensive answer. Please review the search results above for detailed information."

async def traditional_hybrid_search(query):
    """
    Traditional hybrid search implementation
    Requires manual category detection and filter construction
    """
    await cl.Message(content=f"\n=== Traditional Hybrid Search Demo ===").send()
    await cl.Message(content=f"Query: {query}").send()
    
    start_time = time.time()
    
    try:        
        # Step 1: LLM-powered category inference (still traditional approach)
        await cl.Message(content="\n1. LLM-powered category detection...").send()
        categories = await llm_category_mapping(query)
        await cl.Message(content=f"   Detected categories: {categories}").send()
        
        # Step 2: Manual filter construction
        await cl.Message(content="\n2. Building manual filter...").send()
        filter_expr = build_filter_expression(categories)
        await cl.Message(content=f"   Filter expression: {filter_expr}").send()
        
        # Step 3: Create search client
        search_client = create_search_client()
        
        # Step 4: Execute single hybrid search
        await cl.Message(content="\n3. Executing hybrid search...").send()
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
        await cl.Message(content="\n4. Processing results...").send()
        documents = []
        total_count = 0
        
        for result in results:
            full_content = result.get("content", "")
            documents.append({
                "title": result.get("chunk_title", ""),
                "content": full_content,
                "categories": result.get("category", []),
                "reference_link": result.get("url", "")})
            total_count += 1
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Step 6: Generate natural language answer
        natural_answer = None
        if documents:
            natural_answer = await generate_natural_language_answer(query, documents)
        
        # Display results
        results_content = f"""
            ## Traditional Search Results

            **Execution time:** {execution_time:.2f} ms  
            **Total results:** {total_count}  
            **Applied categories filter:** {categories}  
            **Search strategy:** Single hybrid query (keyword + vector + semantic)
                    """
        await cl.Message(content=results_content).send()
                    
        # Display natural language answer if generated
        if natural_answer:
            answer_content = f"""
            ## Natural Language Answer
                {natural_answer}
            """
            await cl.Message(content=answer_content).send()
                    
            # Display top results
            top_results_content = f"\n**Top {min(3, len(documents))} results:**\n"
            for i, doc in enumerate(documents[:3], 1):
                top_results_content += f"""
                **{i}. {doc['title']}**  
                Categories: {doc['categories']}  
                Content: {doc['content']}
    """
        
        # Highlight limitations
        limitations_content = """
        ## Traditional Search Limitations (Even with LLM Answer Generation)

        - Still requires separate LLM calls for categorization AND answer generation
        - Single query execution (no parallel processing)
        - Manual filter construction and result processing
        - No integrated query understanding and breakdown
        - No conversation context support
        - Additional complexity and latency from multiple separate LLM calls
        - Manual orchestration of search -> answer generation pipeline
                """
        await cl.Message(content=limitations_content).send()
        
        return {
            "execution_time_ms": execution_time,
            "result_count": total_count,
            "categories_used": categories,
            "search_type": "traditional_hybrid",
            "natural_answer": natural_answer
        }
        
    except Exception as e:
        await cl.Message(content=f"Error in traditional search: {e}").send()
        return None

@cl.on_message
async def main(message: cl.Message):
    """Main Chainlit message handler that processes user queries"""
    user_query = message.content
    
    # Display welcome message for the first interaction
    if not hasattr(cl.user_session, "initialized"):
        welcome_content = """
    # Traditional Hybrid Search Demo

    Welcome! This demo shows the traditional approach to Azure AI Search with manual filtering and query processing.

    Ask me any Azure architecture question to see how traditional hybrid search works!

    Examples:
    - "What are the networking requirements for AKS?"
    - "How do I configure security for Azure containers?"
    - "What are the best practices for Azure storage?"
            """
        await cl.Message(content=welcome_content).send()
        cl.user_session.set("initialized", True)
    
    # Execute traditional search with user query
    result = await traditional_hybrid_search(user_query)
    
    if result:
        summary_content = f"""
    ## Search Summary

    🏁 Traditional search (with LLM categorization + answer generation) completed in **{result['execution_time_ms']:.2f} ms**

    - Found **{result['result_count']}** results using LLM-powered category detection
    - Generated natural language answer: **{'Yes' if result.get('natural_answer') else 'No'}**
    - Note: Requires multiple separate LLM calls + manual search orchestration
            """
        await cl.Message(content=summary_content).send()
    else:
        await cl.Message(content="❌ Traditional search failed").send()
