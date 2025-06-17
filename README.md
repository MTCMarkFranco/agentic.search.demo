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
├── code-examples/            # Supporting code samples
│   ├── hybrid-search/
│   └── agentic-search/
├── python-demos/             # Live demonstration scripts
│   ├── 01_traditional_hybrid_search.py
│   ├── 02_agentic_search.py
│   ├── requirements.txt
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

## 🐍 Live Python Demonstrations

The `python-demos/` directory contains ready-to-run scripts that demonstrate:

### Traditional Hybrid Search (`01_traditional_hybrid_search.py`)
- Manual query analysis and category mapping
- Single query execution with manual filtering
- Basic hybrid search (keyword + vector + semantic)
- Developer-intensive implementation

### Agentic Search (`02_agentic_search.py`)
- LLM-powered query understanding and breakdown
- Automatic category inference and filtering
- Parallel subquery execution
- Unified semantic ranking and result synthesis

**Demo Queries:**
- **Traditional**: `"What are the networking requirements for AKS?"` (simple, focused)
- **Agentic**: Complex AKS networking query covering enterprise hub-and-spoke topology, Azure AI landing zones, security considerations, and integration patterns

Both scripts output execution times and result quality metrics for direct comparison.

## 📊 Diagrams and Visuals

Each slide includes:
- Mermaid flow diagrams for visual understanding
- Code snippets with practical examples
- Architecture comparisons
- Implementation patterns

## 🚀 Getting Started

1. Navigate to the `slides/` directory
2. Open markdown files in VS Code for best viewing experience
3. Use a markdown preview extension for slide presentation
4. Review code examples in the `code-examples/` directory

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

---

*This presentation is based on Microsoft Learn documentation and best practices for Azure AI Search agentic capabilities.*
