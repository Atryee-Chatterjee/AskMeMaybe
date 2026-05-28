# 📄 AskMeMaybe – Al-Powered RAG-Based PDF Question Answering System

**AskMeMaybe** is an AI-powered document assistant that allows users to **upload multiple PDFs and ask questions in natural language**. It uses a **Retrieval-Augmented Generation (RAG)** pipeline to provide **accurate, fast, and context-aware answers with citations**.

🔗 **Live Demo:** https://askmemaybe.onrender.com

---

# ❗ Problem Statement

## 🚫 Existing Challenges

Working with large PDF documents is often inefficient and time-consuming:

*  Lengthy documents require significant time to read and understand
*  Manually locating specific information is tedious and frustrating
*  Traditional PDF readers lack intelligent search and question-answering capabilities
*  Users spend excessive time scanning through irrelevant content

---

## 💡 Our Solution

**AskMeMaybe** transforms how users interact with documents by introducing AI-powered intelligence:

*  **Context-aware document understanding** using advanced NLP techniques
*  **Natural language question answering** — ask questions like chatting with a human
*  **Fast semantic search** to instantly retrieve relevant information
*  **Accurate, context-based responses** grounded strictly in document content

---

## 🎯 Objective

To build an intelligent system that enables users to **interact with documents conversationally**, making information retrieval **faster, smarter, and more efficient using AI**.

---

# 🚀 Tech Stack

| Layer           | Technology                                 | Environment Variables | Description            |
| --------------- | ------------------------------------------ | --------------------- |------------------------
| **Backend**     | Flask (Python)                             | OPENROUTER_API_KEY    | API key for LLM access |
| **Vector DB**   | FAISS                                      |
| **LLM**         | Llama 3.1 (8B Instruct)                    |
| **Embeddings**  | sentence-transformers (`all-MiniLM-L6-v2`) |
| **Chunking**    | RecursiveCharacterTextSplitter             |
| **Frontend**    | HTML, CSS, JavaScript                      |
| **PDF Parsing** | PyPDF                                      |

---

# ✨ Features

*  Upload multiple PDFs
*  Ask questions in natural language
*  AI-powered answers using document context
*  Source-based responses with citations
*  Clean and responsive UI
*  Chat history support

---

## 🎥 Demo Video

<div align="center">
  <h3>AskMeMaybe</h3>
  <a href="https://www.youtube.com/watch?v=_FBYV1ozumU">
    <img src="https://img.youtube.com/vi/_FBYV1ozumU/0.jpg" 
         alt="AskMeMaybe Demo - Chat with your PDFs" 
         width="70%">
  </a>
  <p>
    <em>⬆️ Click the thumbnail to watch the full demo on YouTube ⬆️</em>
  </p>
</div>

---

# ⚙️ How It Works

## 📄 Document Processing Pipeline

When a user uploads PDFs:

1. **Text Extraction**

   * The system uses **PyPDF** to extract text from each page
   * Metadata such as **file name** and **page number** is preserved

2. **Text Chunking**

   * The extracted text is split into smaller chunks using
     `RecursiveCharacterTextSplitter` from LangChain
   * This improves retrieval accuracy and context relevance

3. **Embedding Generation**

   * Each chunk is converted into vector embeddings using
     **HuggingFace model:** `all-MiniLM-L6-v2`

4. **Vector Storage (FAISS)**

   * All embeddings are stored in a **FAISS vector database**
   * This enables **fast and efficient semantic search**

---

## 🤖 Question Answering Flow

When a user asks a question:

1. **Semantic Search**

   * The system retrieves the most relevant chunks from FAISS

2. **Context Preparation**

   * Retrieved chunks are combined and sent as context to the LLM

3. **LLM Processing**

   * Uses **LLaMA 3.1 (8B Instruct)** via OpenRouter API

4. **Answer Generation**

   * The model generates answers **strictly based on PDF content**
   * Reduces hallucination and ensures **reliable responses**


---

# 🏗️ Project Structure

```
AskMeMaybe/
├── app.py
├── rag.py
├── requirements.txt
├── templates/
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
|          ├── images/
|          └── fonts/
├── uploads/
└── faiss_index/
```

---
# 👥 Meet the Team

<table>
<tr>
<td align="center" width="50%">

### ATRYEE CHATTERJEE

<img src="static/assets/images/AtryeeChatterjee.jpeg" width="50%"/>

<a href="https://www.linkedin.com/in/atryee-chatterjee/">LinkedIn</a>&nbsp;
<a href="https://github.com/Atryee-Chatterjee">GitHub</a>&nbsp;
<a href="mailto:atryeechatterjee31@gmail.com" title="Email">E-mail</a>

**Role:** Backend Developer & AI Engineer

</td>
<td align="center" width="50%">

### SUBHECCHA KAR

<img src="static/assets/images/SubhechhaKar.jpeg" width="50%"/>

<a href="https://www.linkedin.com/in/subhechha-kar-38688b247">LinkedIn</a>&nbsp;
<a href="https://github.com/SubhechhaK">GitHub</a>&nbsp;
<a href="mailto:subhechhakar6447@gmail.com" title="Email">E-mail</a>

**Role:** Frontend Developer & UI/UX Designer

</td>
</tr>
</table>


---

# 🧪 Local Setup

```bash
# Clone repo
git clone https://github.com/Atryee-Chatterjee/AskMeMaybe.git
cd AskMeMaybe

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Add API key in .env
OPENROUTER_API_KEY=your_key_here

# Run app
python app.py
```

---


# 🏆 Achievement

This project was presented at **TECH NOVA’2026** – National Technology Day Celebration organized by the Department of IT, <a href="https://www.georgecollege.org/nimas-barasat-campus">
NIMAS George Group of Colleges </a>.

---

# 🌐 Live App

https://askmemaybe.onrender.com
