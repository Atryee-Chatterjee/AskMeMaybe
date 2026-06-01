# 📄 AskMeMaybe – AI-Powered RAG-Based PDF Question Answering System (Streamlit Version)

**AskMeMaybe** is an AI-powered document assistant that allows users to upload multiple PDFs and ask questions in natural language. This version is built using Streamlit and runs a Retrieval-Augmented Generation (RAG) pipeline to generate accurate, context-aware answers directly from document content.

🔗 **Live Demo:** https://askmemaybe.onrender.com

---

# ❗ Problem & Solution

## 🚫 Existing Challenges

Working with large PDF documents is often inefficient and time-consuming:

* Lengthy documents require significant time to read and understand
* Manually locating specific information is tedious and frustrating
* Traditional PDF readers lack intelligent search and question-answering capabilities
* Users spend excessive time scanning through irrelevant content

---

## 💡 Our Solution

**AskMeMaybe** transforms how users interact with documents by introducing AI-powered intelligence:

* **Context-aware document understanding** using advanced NLP techniques
* **Natural language question answering** — ask questions like chatting with a human
* **Fast semantic search** to instantly retrieve relevant information
* **Accurate, context-based responses** grounded strictly in document content

---

## 🎯 Objective

To build an intelligent system that enables users to **interact with documents conversationally**, making information retrieval **faster, smarter, and more efficient using AI**.

---

# ✨ Features

* Upload multiple PDFs
* Ask questions in natural language
* AI-powered answers using document context
* Source-based responses with citations
* Clean and responsive UI
* Chat history support

---

# 🚀 Tech Stack

| Layer            | Technology                                 | Description                                |
| ---------------- | ------------------------------------------ | ------------------------------------------ |
| **Frontend/UI**  | Streamlit (Python)                         | Interactive web interface                  |
| **LLM**          | LLaMA 3.1 (8B Instruct)                    | Generates context-aware answers            |
| **LLM Wrapper**  | HuggingFaceEndpoint + ChatHuggingFace      | Connects app to Hugging Face models        |
| **Vector Store** | FAISS                                      | Fast similarity search for document chunks |
| **Embeddings**   | sentence-transformers (`all-MiniLM-L6-v2`) | Converts text into vector embeddings       |
| **Chunking**     | RecursiveCharacterTextSplitter             | Splits text into manageable chunks         |
| **PDF Parsing**  | PyPDF                                      | Extracts text from uploaded PDFs           |
| **Framework**    | LangChain                                  | Manages RAG pipeline                       |

---

# 🏗️ Project Structure

```
AskMeMaybe-Streamlit/
├── streamlit_app.py
├── requirements.txt
├── .env
├── faiss_index/
```

---

# 🧪 Local Setup

```bash
# Clone repo
git clone https://github.com/Atryee-Chatterjee/AskMeMaybe.git
cd AskMeMaybe

# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate      # Windows
# source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add API key in .env file
HUGGINGFACEHUB_API_TOKEN=your_token_here

# Run app
streamlit run streamlit_app.py
```

---

# ⚙️ How It Works

## 📄 Document Processing Pipeline

When a user uploads PDFs:

1. **Text Extraction**

   * The system uses **PyPDF** to extract text from each page
   * Important metadata like **file name** and **page number** is preserved

2. **Text Chunking**

   * The extracted text is split into smaller chunks using
     `RecursiveCharacterTextSplitter`
   * This improves retrieval accuracy and maintains context

3. **Embedding Generation**

   * Each chunk is converted into vector embeddings using
     **sentence-transformers:** `all-MiniLM-L6-v2`

4. **Vector Storage (FAISS)**

   * All embeddings are stored in a **FAISS vector database**
   * Enables **fast and efficient semantic search**

---

## 🤖 Question Answering Flow

When a user asks a question:

1. **Semantic Retrieval**

   * The system fetches the most relevant chunks from FAISS

2. **Context Building**

   * Retrieved chunks are combined to form the context

3. **LLM Processing**

   * The query + context is sent to **LLaMA 3.1 (8B Instruct)** via **HuggingFaceEndpoint**

4. **Answer Generation**

   * A custom prompt ensures:

     * Answers are generated **strictly from document context**
     * If not found → *"I don't know based on the document."*
   * Minimizes hallucination and ensures **reliable responses**

---

# 🔗 Links

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge\&logo=github)](https://github.com/Atryee-Chatterjee/AskMeMaybe)
[![Live Demo](https://img.shields.io/badge/Live-Demo-green?style=for-the-badge\&logo=render)](https://askmemaybe.onrender.com/)
[![LinkedIn Post](https://img.shields.io/badge/LinkedIn-Post-blue?style=for-the-badge\&logo=linkedin)](https://www.linkedin.com/posts/atryee-chatterjee_technova2026-nationaltechnologyday-askmemaybe-ugcPost-7465847924850188289-5eSb/?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEb74ZoBICyUgQDFx2VPI9S7blTYHMjiD78)
[![YouTube Demo](https://img.shields.io/badge/YouTube-Demo-red?style=for-the-badge\&logo=youtube)](https://www.youtube.com/watch?v=_FBYV1ozumU)

---

# 👩‍💻 Developer

<table>
<tr>
<td align="center">

### ATRYEE CHATTERJEE

<img src="https://github.com/Atryee-Chatterjee.png" width="120px" style="border-radius:50%" />

<br><br>

<a href="https://www.linkedin.com/in/atryee-chatterjee/">LinkedIn</a> • <a href="https://github.com/Atryee-Chatterjee">GitHub</a> • <a href="mailto:atryeechatterjee31@gmail.com">Email</a>

<br><br>

**Role:** Backend Developer & AI Engineer

</td>
</tr>
</table>


