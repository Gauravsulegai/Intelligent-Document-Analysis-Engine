# Approach Explanation for Round 1B: Persona-Driven Document Intelligence

## Overview

The goal of Challenge 1B was to build an intelligent system that could analyze a collection of PDF documents and extract the most relevant sections based on a specific user persona and their "job-to-be-done." This task requires moving beyond simple keyword matching to understand the underlying meaning and context of the user's request.

## The Core Challenge

A simple keyword search is insufficient for this task. For example, a user looking for "revenue growth" might miss a relevant section that discusses "increased annual income" or "a surge in sales." To solve this, our solution needed to understand language semantically.

## Our Solution: A Semantic Search Engine

We engineered a lightweight, offline semantic search engine that uses text embeddings to find relevant information based on meaning rather than exact words. Our approach is a four-step pipeline:

#### **1. Document Parsing and Chunking**
The system first ingests the collection of PDFs. Each document is carefully parsed into smaller, logical chunks of text, such as paragraphs. This ensures that the context of each piece of information is preserved.

#### **2. Text Embedding**
We use the `all-MiniLM-L6-v2` sentence-transformer model to convert the user's request and every text chunk from the documents into numerical vectors (embeddings). This model was specifically chosen for its excellent balance of performance and size (~80MB), making it ideal for fast, offline execution on a CPU.

#### **3. Relevance Scoring with Cosine Similarity**
To find the most relevant information, we calculate the cosine similarity between the user's request vector and the vector for every text chunk. A score closer to 1 indicates a strong semantic match in meaning, even if the phrasing is different.

#### **4. Ranking and Output**
The text chunks are ranked based on their cosine similarity scores. The system then returns the top-ranked sections from across the document collection, providing the user with a prioritized list of the most relevant information to help them accomplish their task.

This approach ensures our solution is robust, context-aware, and capable of uncovering genuinely relevant insights that a traditional search method would miss.