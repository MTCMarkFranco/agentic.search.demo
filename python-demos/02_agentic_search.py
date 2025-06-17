"""
Agentic Search Demo
Demonstrates AI-powered query understanding and automatic filtering with Azure AI Search

This script shows the agentic approach where the LLM:
1. Automatically analyzes complex queries and breaks them down
2. Intelligently determines appropriate categories without manual mapping
3. Executes parallel subqueries for better coverage
4. Provides unified, semantically ranked results
"""

import os
import time
import json
import textwrap
from dotenv import load_dotenv
import chainlit as cl
from azure.identity import DefaultAzureCredential
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

load_dotenv(override=True)

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")
AGENT_NAME = os.getenv("AZURE_SEARCH_AGENT_NAME")
AZURE_OPENAI_KNOWLEDGE_MODEL = os.getenv("AZURE_OPENAI_KNOWLEDGE_MODEL")
AZURE_OPENAI_KNOWLEDGE_DEPLOYMENT = os.getenv("AZURE_OPENAI_KNOWLEDGE_DEPLOYMENT")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

async def create_knowledge_agent():
    await cl.Message(content="\n1. Setting up knowledge agent...").send()
    try:
        index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_API_KEY))
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
        index_client.create_or_update_agent(agent)
        await cl.Message(content=f"   ✅ Knowledge agent '{AGENT_NAME}' created or updated successfully").send()
        return True
    except Exception as e:
        await cl.Message(content=f"   ❌ Error setting up knowledge agent: {e}").send()
        return False

async def agentic_retrieval_search(query):
    await cl.Message(content=f"\n=== Agentic Search Demo ===").send()
    await cl.Message(content=f"Query: {query}").send()
    start_time = time.time()
    try:
        # Step 1: Setup knowledge agent
        agent_ok = await create_knowledge_agent()
        if not agent_ok:
            return None
        # Step 2: Create agent client for retrieval
        await cl.Message(content="\n2. Creating agent client for retrieval...").send()
        agent_client = KnowledgeAgentRetrievalClient(
            endpoint=SEARCH_ENDPOINT, 
            agent_name=AGENT_NAME, 
            credential=AzureKeyCredential(SEARCH_API_KEY)
        )
        # Step 3: Set up messages for conversation
        await cl.Message(content="\n3. Preparing conversation messages...").send()
        instructions = """
        You are an intelligent search assistant specializing in Azure architecture and best practices.
        When processing queries, analyze the user's intent and provide comprehensive information
        covering security, architecture, networking, and operational considerations.
        """
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": query}
        ]
        # Step 4: Execute agentic retrieval using the SDK
        await cl.Message(content="\n4. Executing agentic retrieval...").send()
        await cl.Message(content="   🤖 LLM analyzing query and planning subqueries...").send()
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
        execution_time = (end_time - start_time) * 1000
        # Step 5: Process and display results
        await cl.Message(content="\n5. Processing agentic results...").send()
        unified_result = retrieval_result.response[0].content[0].text if retrieval_result.response else ""
        references = retrieval_result.references or []
        activities = retrieval_result.activity or []
        # Show LLM's query breakdown and execution plan
        if activities:
            plan_content = f"\n🧠 LLM Query Breakdown & Execution Plan:"
            for i, activity in enumerate(activities, 1):
                activity_dict = activity.as_dict()
                activity_type = activity_dict.get("type", "Unknown")
                if activity_type == "AzureSearchQuery":
                    search_query = activity_dict.get("query", {}).get("search", "")
                    result_count = activity_dict.get("count", 0)
                    plan_content += f"\n   {i}. Search Query: \"{search_query}\""
                    plan_content += f"\n      Type: {activity_type}"
                    plan_content += f"\n      Results: {result_count}"
            await cl.Message(content=plan_content).send()
        # Show top references
        top_refs_content = f"\n**Top {min(3, len(references))} references:**\n"
        for i, ref in enumerate(references[:3], 1):
            ref_dict = ref.as_dict()
            doc_key = ref_dict.get("doc_key", "Unknown")
            activity_source = ref_dict.get("activity_source", 0)
            top_refs_content += f"\n{i}. Document: {doc_key}\n   Activity Source: {activity_source}\n   Reference ID: {ref_dict.get('id', 'N/A')}\n"
        await cl.Message(content=top_refs_content).send()
        # Generate natural language answer
        natural_answer = await generate_natural_language_answer(query, retrieval_result)
        # Highlight agentic advantages
        advantages_content = """
## Agentic Search Advantages Demonstrated

- Automatic query decomposition (no manual breakdown needed)
- Intelligent LLM-powered query planning
- Parallel subquery execution (better coverage)
- Semantic understanding and ranking
- Unified result synthesis
- Context-aware conversation handling
- Natural language answer generation from search results
        """
        await cl.Message(content=advantages_content).send()
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
        await cl.Message(content=f"Error in agentic search: {e}").send()
        return None

async def generate_natural_language_answer(query, retrieval_result):
    await cl.Message(content=f"\n6. Generating natural language answer...").send()
    try:
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT
        )
        references_content = ""
        if retrieval_result.references:
            for i, ref in enumerate(retrieval_result.references[:5], 1):
                ref_dict = ref.as_dict()
                if 'content' in ref_dict:
                    references_content += f"\nReference {i}: {ref_dict['content'][:500]}...\n"
        system_prompt = """You are an expert Azure architect and consultant. Based on the provided search results and references, \
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
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = client.chat.completions.create(
            model=AZURE_OPENAI_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=3000
        )
        answer = response.choices[0].message.content
        await cl.Message(content=f"   ✅ Generated natural language answer ({len(answer)} characters)").send()
        answer_content = f"""
## Natural Language Answer

{answer}
        """
        await cl.Message(content=answer_content).send()
        return answer
    except Exception as e:
        await cl.Message(content=f"   ⚠️  Natural language answer generation failed: {e}").send()
        return None

@cl.on_message
async def main(message: cl.Message):
    user_query = message.content
    if not hasattr(cl.user_session, "initialized"):
        welcome_content = """
# Agentic Search Demo

Welcome! This demo shows the agentic approach to Azure AI Search with automatic query understanding and filtering.

Ask me any Azure architecture question to see how agentic search works!

Examples:
- "What are the networking requirements for AKS?"
- "How do I configure security for Azure containers?"
- "What are the best practices for Azure storage?"
        """
    await cl.Message(content=welcome_content).send()
    cl.user_session.set("initialized", True)
    result = await agentic_retrieval_search(user_query)
    if result:
        summary_content = f"""
## Search Summary

🏁 Agentic search completed in **{result['execution_time_ms']:.2f} ms**

- Found **{result['result_count']}** references using agentic retrieval
- Generated natural language answer: **{'Yes' if result.get('natural_answer') else 'No'}**
- Note: Automatic query breakdown, parallel subqueries, and unified answer generation
        """
        await cl.Message(content=summary_content).send()
    else:
        await cl.Message(content="❌ Agentic search failed").send()
