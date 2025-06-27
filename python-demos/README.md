# Python Demo Scripts: Traditional vs Agentic Search

This directory contains Python demo scripts comparing traditional hybrid search with Azure AI Search's agentic retrieval capabilities.

## 📁 Files

- `01_traditional_hybrid_search.py` - Traditional approach with manual query processing
- `02_agentic_search.py` - Modern agentic approach with LLM-powered query understanding
- `requirements.txt` - Python dependencies with latest Azure SDK versions
- `sample.env` - Environment configuration template
- `README.md` - This file

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
# Install preview packages for agentic retrieval support
pip install azure-search-documents --pre
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and update with your Azure service values:

```bash
cp .env.example .env
```

Edit `.env` with your Azure service endpoints and credentials:

```bash
# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX=index-arch-data
AZURE_SEARCH_AGENT_NAME=azure-arch-agent

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-deployment
AZURE_OPENAI_MODEL=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Knowledge Agent Configuration (for agentic search)
AZURE_OPENAI_KNOWLEDGE_MODEL=gpt-4o
AZURE_OPENAI_KNOWLEDGE_DEPLOYMENT=gpt-4o-knowledge-deployment
```

**Note**: For production environments, leave API keys empty to use managed identity authentication.

**🔒 Security Note**: 
- Never commit `.env` files to version control
- The `.env.example` file is provided as a template
- Use Azure Key Vault or managed identity for production deployments

### 3. Authentication & Permissions

**Using Managed Identity (Recommended)**:
Ensure your user account or managed identity has these Azure roles:
- **Search Service Contributor** (on Azure AI Search)
- **Search Index Data Contributor** (on Azure AI Search)  
- **Search Index Data Reader** (on Azure AI Search)
- **Cognitive Services User** (on Azure OpenAI)

### 4. Azure AI Search Index Requirements

The scripts target an index with these specifications:
- **Index Name**: `index-arch-data` (configurable)
- **Semantic Configuration**: Required for agentic retrieval
- **Vector Fields**: For hybrid search capabilities
- **Key Field**: Unique document identifier

## 🚀 Running the Demos

### Traditional Hybrid Search Demo

```bash
python 01_traditional_hybrid_search.py
```

**What it demonstrates:**
- LLM-powered category inference (improvement over manual keyword mapping)
- Manual filter construction and search orchestration
- Single query execution with basic hybrid search
- Separate LLM call overhead and complexity
- Still requires developer management of the search pipeline

### Agentic Search Demo

```bash
python 02_agentic_search.py
```

**What it demonstrates:**
- **Knowledge Agent Creation**: Automatic setup of LLM-powered search agent
- **Intelligent Query Planning**: LLM automatically breaks down complex queries
- **Parallel Execution**: Multiple search activities executed simultaneously
- **Semantic Ranking**: Unified ranking across all subquery results
- **Context Awareness**: Conversation history and user intent understanding
- **Answer Generation**: Integrated Azure OpenAI for response synthesis

**Key Features Based on Azure SDK**:
- Uses `KnowledgeAgent` for agent creation
- `KnowledgeAgentRetrievalClient` for retrieval operations
- `KnowledgeAgentRetrievalRequest` with message-based conversation
- Managed identity authentication (secure, recommended)

**Sample Query**: Complex multi-intent query about AKS networking requirements in enterprise hub-and-spoke topology with Azure AI landing zones

## 💻 Technical Implementation Details

### Azure SDK Versions Used
- **azure-search-documents**: >=11.6.0b12 (preview for agentic retrieval)
- **azure-identity**: >=1.17.0 (latest managed identity support)
- **openai**: >=1.50.0 (Azure OpenAI integration)
- **python-dotenv**: >=1.0.0 (environment configuration)

### API Versions
- **Azure AI Search**: 2025-05-01-Preview (required for knowledge agents)
- **Azure OpenAI**: 2025-03-01-preview (latest chat completions)

### Prerequisites
- **Azure AI Search**: Basic tier or higher with semantic ranker enabled
- **Azure OpenAI**: Deployed model (gpt-4o recommended)
- **Python**: 3.8+ (tested with 3.11+)

## 🔍 Troubleshooting

### Common Issues

1. **"Knowledge agent not found"**
   - Ensure you have the preview SDK version: `pip install azure-search-documents --pre`
   - Verify API version: 2025-05-01-Preview

2. **Authentication errors**
   - Check your Azure role assignments (see Authentication & Permissions section)
   - Verify environment variables are set correctly

3. **Index not found**
   - Update `AZURE_SEARCH_INDEX` in your .env file
   - Ensure the index has a semantic configuration

4. **OpenAI deployment errors**
   - Verify `AZURE_OPENAI_GPT_DEPLOYMENT` matches your deployed model name
   - Check model availability in your region

## 📚 Additional Resources

- [Azure AI Search Agentic Retrieval Documentation](https://learn.microsoft.com/azure/search/search-agentic-retrieval-concept)
- [Azure Search Python SDK Reference](https://docs.microsoft.com/python/api/overview/azure/search-documents-readme)
- [Azure OpenAI Python SDK](https://github.com/openai/openai-python)
- [Managed Identity Best Practices](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)

---

*These demos are designed to showcase the evolution from traditional RAG patterns to modern agentic search capabilities.*
