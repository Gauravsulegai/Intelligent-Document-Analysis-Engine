# Adobe India Hackathon 2025: Connecting the Dots
## Round 1A: PDF Document Structure Extraction

### Overview

This project is a robust, high-performance solution for **Challenge 1A** of the Adobe India Hackathon. The mission is to transform raw PDFs into structured data by intelligently extracting their hierarchical outline (Title, H1, H2, etc.).

Our solution is packaged in a lightweight, offline Docker container and is engineered to process a wide variety of document types—from structured reports and forms to highly stylized flyers—with exceptional accuracy and speed.

### Our Approach: A Context-Aware Heuristic Engine

Recognizing that a one-size-fits-all rule set is insufficient for the diversity of PDF documents, we developed a **context-aware, multi-pass heuristic engine**. Instead of relying on a single attribute like font size, our engine analyzes the document as a whole to understand its context and then applies a sophisticated scoring model.

The process works as follows:

1.  **Contextual Analysis**: The engine first performs a quick scan of the entire document to determine its properties. Is it a dense, text-heavy report, a sparse form with many small labels, or a visually-driven flyer? This initial analysis allows the engine to adjust its strategy.

2.  **Candidate Scoring**: The solution processes the document in logical text blocks (not just single lines), preserving multi-line headings. Each block is scored based on a weighted combination of universal, language-agnostic features:
    * **Font Size**: Relative size compared to the document's main body text.
    * **Font Weight**: Boldness is detected using language-agnostic font metadata flags.
    * **Structural Patterns**: A high score is given to text that follows common heading patterns, like numbered lists ("1.", "2.1") or appendices.
    * **Contextual Clues**: The score is adjusted based on the document's context. For example, short, bold text in a "form-like" document is penalized, while large, stylized text in a "sparse" document (like an invitation) is given a significant boost.

3.  **Dynamic Level Assignment**: Finally, the scores are clustered to dynamically assign heading levels (H1, H2, H3, etc.) based on the document's own unique visual hierarchy. This allows the solution to adapt to any styling convention.

This intelligent, multi-layered approach ensures high accuracy and resilience, allowing the engine to "connect the dots" in a way that a simple rules-based system cannot.

### Libraries & Models

* **Primary Library**: **PyMuPDF (`fitz`)** for its high-speed and detailed PDF parsing.
* **No ML Models**: This solution is a pure, advanced heuristic engine and does not use any pre-trained machine learning models, ensuring it is lightweight and fast. All libraries are open-source.

### Submission Requirements Checklist

-   [x] **GitHub Project**: Complete and functional solution repository.
-   [x] **Dockerfile**: Located in the `round1a/` directory and fully functional.
-   [x] **README.md**: This file.

### Build and Run Commands

**Prerequisites**: Docker Desktop must be installed and running.

1.  **Build the Docker Image**:
    ```bash
    docker build --platform linux/amd64 -t round1a-solution round1a/
    ```

2.  **Run the Container**:
    _Place your PDFs in an `input` folder in the project root before running._
    ```bash
    docker run --rm -v /$(pwd)/input:/app/input -v /$(pwd)/output:/app/output --network none round1a-solution
    ```
    The processed JSON files will appear in an `output` folder.

### Validation Checklist

-   [x] **All PDFs in input directory are processed**: Yes.
-   [x] **JSON output files are generated for each PDF**: Yes.
-   [x] **Output format matches required structure**: Yes.
-   [x] **Processing completes within 10 seconds for 50-page PDFs**: Yes.
-   [x] **Solution works without internet access**: Yes.
-   [x] **Memory usage stays within 16GB limit**: Yes.
-   [x] **Compatible with AMD64 architecture**: Yes.

---

## Round 1B: Persona-Driven Document Intelligence

### Overview

This project is an intelligent document analysis engine for **Challenge 1B**. The goal is to read a collection of 3-10 PDFs and, based on a user persona and a "job-to-be-done," extract and rank the most semantically relevant sections from the document collection.

### Our Approach: Semantic Search with Text Embeddings

To determine relevance, our solution goes beyond keywords and analyzes the *meaning* of the text using a state-of-the-art Natural Language Processing (NLP) model.

1.  **Document Parsing**: The engine first uses the logic from Round 1A to identify potential section headings. It then parses each document into small, meaningful paragraphs (chunks).
2.  **Text Embedding**: A lightweight but powerful NLP model (`all-MiniLM-L6-v2`) converts the user's request (persona + job) and every text chunk into numerical vectors, or "embeddings," that capture their semantic meaning.
3.  **Relevance Ranking**: The system calculates the **cosine similarity** between the user's request embedding and each text chunk's embedding to score relevance.
4.  **Diversified Output**: To ensure a comprehensive and useful result, the engine first identifies the single most relevant chunk from *each* document in the collection. It then ranks these top chunks to produce a final, diversified list of the most important sections and subsections from across the entire document set.

This semantic search approach allows the system to uncover genuinely relevant information, even if the text doesn't contain the exact keywords from the user's request.

### Libraries & Models

* **Primary Libraries**: **PyMuPDF**, **Sentence-Transformers**, **PyTorch**, and **Scikit-learn**.
* **NLP Model**: `all-MiniLM-L6-v2` (80MB), a lightweight sentence-embedding model chosen for its excellent balance of performance and speed on a CPU. The model is included in the repository to ensure the solution works completely offline.

### Submission Requirements Checklist

-   [x] **GitHub Project**: Complete and functional solution repository.
-   [x] **Dockerfile**: Located in the `round1b/` directory and fully functional.
-   [x] **README.md**: This file.
-   [x] **approach_explanation.md**: A separate file detailing the methodology.

### Build and Run Commands

**Prerequisites**: Docker Desktop must be installed and running.

1.  **Build the Docker Image**:
    ```bash
    docker build --platform linux/amd64 -t round1b-solution round1b/
    ```

2.  **Run the Container**:
    *Place your `PDFs` folder and `challenge1b_input.json` file in an `input` folder in the project root before running.*
    ```bash
    docker run --rm -v /$(pwd)/input:/app/input -v /$(pwd)/output:/app/output --network none round1b-solution
    ```
    The final `challenge1b_output.json` file will be generated in an `output` folder.

### Validation Checklist

-   [x] **Processing completes within 60 seconds for 3-5 documents**: Yes.
-   [x] **Solution works without internet access**: Yes.
-   [x] **Model size stays within 1GB limit**: Yes, our model is ~80MB.
-   [x] **Compatible with AMD64 architecture**: Yes.


### Our Team & Contributions

This project was a collaborative effort by all three team members. We divided our roles based on our strengths to work efficiently.

*[Gaurav SK] - Lead Developer & Architect*

* Designed and implemented the core logic for the PDF parsing engine (Round 1A).
* Developed the semantic search and relevance ranking system (Round 1B).
* Set up the Docker environment and managed the final build process.

[Piyush Kumar] - Research & Quality Assurance
    
* Conducted initial research on PDF parsing libraries and NLP models to help the team decide on the optimal tech stack.

* Sourced and curated a diverse set of test PDFs (e.g., reports, forms, multi-language documents) to ensure the solution
was robust.

* Performed rigorous testing, identified bugs, and provided feedback for performance improvements.

[Shivam Kumar] - Project Management & Strategy

* Managed the project timeline and ensured the team met all submission requirements and deadlines.

* Led the initial brainstorming sessions to define the project's core strategy and scope.

* Analyzed the user persona requirements for Round 1B, helping to define the key use-cases that guided the development process.
