# Agentic Search vs Hybrid Search Presentation

A comprehensive technical presentation comparing Azure AI Search agentic search capabilities with traditional hybrid search patterns for developers familiar with RAG (Retrieval-Augmented Generation) systems.

## 📁 Project Structure

```
presentation/
├── slides/                    # Markdown presentation slides
│   ├── 01-introduction.md
│   ├── 02-traditional-rag.md
│   ├── 03-agentic-search-advantages.md
│   ├── 04-implementation-classes.md
│   └── 05-semantic-kernel-integration.md
├── python-demos/             # Complete Python demonstration scripts
│   ├── 01_traditional_hybrid_search.py
│   ├── 02_agentic_search.py
│   ├── requirements.txt
│   ├── sample.env
│   ├── UPDATE_SUMMARY.md
│   └── README.md
└── README.md                # This file
```

## 🎯 Presentation Overview

This presentation covers:

1. **Introduction to Search Patterns** - Overview of traditional search approaches
2. **Traditional RAG Limitations** - Understanding current hybrid search constraints
3. **Agentic Search Advantages** - Key benefits and use cases
4. **Implementation Classes** - Required components for agentic search
5. **Semantic Kernel Integration** - Practical implementation with chat completion

## 🔧 Technical Focus Areas

- **Azure AI Search** - Core search service capabilities
- **Semantic Kernel** - Microsoft's AI orchestration framework
- **Agentic Patterns** - AI-driven search decision making
- **Chat Completion Integration** - Connecting search results to conversational AI

## 🐍 Complete Python Demonstrations

The `python-demos/` directory contains fully functional, production-ready scripts that demonstrate both traditional and agentic search patterns:

### Traditional Hybrid Search (`01_traditional_hybrid_search.py`)
- LLM-powered category inference (improved over manual keyword mapping)
- Manual filter construction and search orchestration
- Single query execution with basic hybrid search
- Separate LLM call overhead and complexity
- Developer-intensive pipeline management

### Agentic Search (`02_agentic_search.py`)
- **Knowledge Agent Creation**: Automatic setup using Azure SDK's `KnowledgeAgent`
- **Intelligent Query Planning**: LLM automatically breaks down complex queries
- **Parallel Execution**: Multiple search activities executed simultaneously
- **Semantic Ranking**: Unified ranking across all subquery results
- **Context Awareness**: Conversation history and user intent understanding
- **Answer Generation**: Integrated Azure OpenAI for response synthesis

**Key Technical Features:**
- Uses latest Azure Search SDK preview (11.6.0b12+) for agentic retrieval
- Managed identity authentication for secure access
- Preview API version (2025-05-01-Preview) for knowledge agents
- Complete environment setup with `sample.env` template

**Demo Queries:**
- **Traditional**: `"What are the networking requirements for AKS?"` (simple, focused)
- **Agentic**: Complex multi-intent AKS networking query covering enterprise hub-and-spoke topology, Azure AI landing zones, security considerations, and integration patterns

Both scripts output execution times and result quality metrics for direct comparison.

### Setup and Dependencies

The Python demos include:
- **requirements.txt**: All necessary Azure SDK packages including preview versions
- **sample.env**: Environment configuration template for Azure services
- **README.md**: Detailed setup instructions, troubleshooting, and technical implementation details
- **UPDATE_SUMMARY.md**: Latest changes and version information

See the `python-demos/README.md` for complete setup instructions, including:
- Azure SDK preview package installation
- Environment configuration with Azure endpoints
- Managed identity authentication setup
- Required Azure service permissions and roles

## 📊 Diagrams and Visuals

Each slide includes:
- Mermaid flow diagrams for visual understanding
- Code snippets with practical examples
- Architecture comparisons
- Implementation patterns

## 🚀 Getting Started

1. **Navigate to the `slides/` directory** for the presentation content
2. **Open markdown files in VS Code** for best viewing experience
3. **Use a markdown preview extension** for slide presentation format
4. **Review and run Python demos** in the `python-demos/` directory:
   - Follow setup instructions in `python-demos/README.md`
   - Install preview Azure SDK packages
   - Configure environment variables with your Azure services
   - Run both traditional and agentic search demonstrations

## 📚 Prerequisites

- Familiarity with traditional RAG patterns
- Understanding of Azure AI Search basic concepts
- Knowledge of vector search, semantic search, and hybrid search
- Basic understanding of AI/ML concepts

## 🎪 Presentation Format

The slides are designed as standalone markdown files that can be:
- Viewed in VS Code with markdown preview
- Converted to presentation format using tools like Marp
- Used as reference documentation
- Adapted for different audiences

### 💻 From Theory to Practice

- **Slides 1-3**: Conceptual understanding and benefits of agentic search
- **Slides 4-5**: Technical implementation details with .NET/C# and Semantic Kernel
- **Python Demos**: Working implementations that you can run and modify
  - See `python-demos/` for hands-on experience with both traditional and agentic patterns
  - Complete with setup instructions, environment configuration, and detailed explanations

---

*This presentation is based on Microsoft Learn documentation and best practices for Azure AI Search agentic capabilities.*
