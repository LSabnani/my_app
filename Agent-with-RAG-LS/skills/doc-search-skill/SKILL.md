---
name: doc_search_tool
description: Queries the Document Vector Database to retrieve text chunks and evidence matching the user query from ingested files and websites.
---

# Document Search Skill

## Description
Queries the Document Vector Database to retrieve text chunks and evidence matching the user query from ingested files and websites.

## Metadata
- **Name**: doc_search_tool
- **Function**: `doc_search.query_document_store`
- **Trigger Queries**:
  - What does the company marketing strategy say about North America?
  - Search documents for Q3 financial performance and gross revenue.
  - What are the core components of RAG architecture in sample docs?

## Parameters
- `query` (string): Search query string to match document vector store chunks.
- `top_k` (integer, optional): Maximum number of document chunks to return. Default: 5.
- `doc_threshold` (float, optional): Minimum similarity threshold. Default: 0.3.
