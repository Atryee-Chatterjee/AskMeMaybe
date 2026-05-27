import os
import re
from pypdf import PdfReader
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from openai import OpenAI

load_dotenv()

UUID_PREFIX_RE = re.compile(r'^[0-9a-fA-F\-]{36}_(.+)$')

def normalize_source_name(path):
    base = os.path.basename(path)
    match = UUID_PREFIX_RE.match(base)
    return match.group(1) if match else base


# ----------------------------
# ✅ EMBEDDINGS (CACHED + LIGHT)
# ----------------------------
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        _embeddings = OpenAIEmbeddings()
    return _embeddings


# ----------------------------
# PDF READER
# ----------------------------
def get_pdf_documents(pdf_paths):
    docs = []

    for path in pdf_paths:
        try:
            reader = PdfReader(path)

            for i, page in enumerate(reader.pages):
                text = page.extract_text()

                if text:
                    docs.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": path,
                                "page": i + 1
                            }
                        )
                    )
        except Exception as e:
            print(f"Skipped {path}: {e}")

    return docs


# ----------------------------
# CHUNKING
# ----------------------------
def get_text_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)


# ----------------------------
# VECTOR STORE
# ----------------------------
def create_vector_store(documents):
    embeddings = get_embeddings()

    os.makedirs("faiss_index", exist_ok=True)
    index_file = os.path.join("faiss_index", "index.faiss")

    try:
        if os.path.exists(index_file):
            db = FAISS.load_local(
                "faiss_index",
                embeddings,
                allow_dangerous_deserialization=True
            )
            db.add_documents(documents)
        else:
            db = FAISS.from_documents(documents, embedding=embeddings)

        db.save_local("faiss_index")

    except Exception as e:
        raise Exception(f"Vector DB error: {str(e)}")


# ----------------------------
# LOAD DB
# ----------------------------
def load_vector_store():
    index_file = os.path.join("faiss_index", "index.faiss")

    if not os.path.exists(index_file):
        raise Exception("FAISS index not found. Upload PDFs first.")

    embeddings = get_embeddings()

    return FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )


# ----------------------------
# LLM (OPENROUTER)
# ----------------------------
def get_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    def generate(prompt):
        completion = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return completion.choices[0].message.content

    return generate


# ----------------------------
# QUERY
# ----------------------------
def ask_question(question):
    index_file = os.path.join("faiss_index", "index.faiss")

    if not os.path.exists(index_file):
        return {
            "answer": "No PDFs processed yet. Please upload PDFs first.",
            "sources": []
        }

    try:
        db = load_vector_store()
        docs = db.similarity_search(question, k=5)
    except Exception as e:
        return {
            "answer": f"DB error: {str(e)}",
            "sources": []
        }

    if not docs:
        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    context = "\n\n".join([doc.page_content for doc in docs])

    sources = []
    seen = set()

    for doc in docs:
        meta = doc.metadata
        source_path = meta.get("source", "")
        page = meta.get("page", "")

        key = f"{source_path}-{page}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": normalize_source_name(source_path),
                "page": page,
                "file_name": os.path.basename(source_path)
            })

    try:
        llm = get_llm()
        answer = llm(f"""
Answer ONLY using the context below.
If not found, say: Answer not found in provided PDFs.

Context:
{context}

Question:
{question}
""")
    except Exception as e:
        return {
            "answer": f"LLM error: {str(e)}",
            "sources": sources
        }

    return {
        "answer": answer.strip(),
        "sources": sources
    }