import os
import re
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
from langchain_core.documents import Document

from openai import OpenAI

# ----------------------------
# CLEAN FILE NAME
# ----------------------------
UUID_PREFIX_RE = re.compile(r'^[0-9a-fA-F\-]{36}_(.+)$')

def normalize_source_name(path):
    base = os.path.basename(path)
    match = UUID_PREFIX_RE.match(base)
    return match.group(1) if match else base


# ----------------------------
# LIGHT EMBEDDINGS
# ----------------------------
def get_embeddings():
    return FakeEmbeddings(size=384)


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
        chunk_size=400,
        chunk_overlap=50
    )
    return splitter.split_documents(docs)


# ----------------------------
# VECTOR STORE
# ----------------------------
def create_vector_store(documents):
    embeddings = get_embeddings()

    os.makedirs("faiss_index", exist_ok=True)
    index_file = os.path.join("faiss_index", "index.faiss")

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


# ----------------------------
# LOAD DB
# ----------------------------
def load_vector_store():
    embeddings = get_embeddings()

    return FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )


# ----------------------------
# 🔥 SMART LLM (OPENROUTER)
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
                {"role": "system", "content": "Answer using ONLY the given context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400,
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
            "answer": "Upload PDFs first.",
            "sources": []
        }

    db = load_vector_store()
    docs = db.similarity_search(question, k=3)

    if not docs:
        return {
            "answer": "No relevant info found.",
            "sources": []
        }

    context = "\n\n".join([doc.page_content for doc in docs])

    # ✅ FIXED SOURCES
    sources = []
    seen = set()

    for doc in docs:
        meta = doc.metadata
        key = f"{meta['source']}-{meta['page']}"

        if key not in seen:
            seen.add(key)
            sources.append({
                "source": normalize_source_name(meta["source"]),
                "page": meta["page"],
                "file_name": os.path.basename(meta["source"])  # 🔥 FIX
            })

    prompt = f"""
Use ONLY the context below to answer.

Context:
{context}

Question:
{question}

If answer not found, say: Not found in PDFs.
"""

    try:
        llm = get_llm()
        answer = llm(prompt)
    except Exception as e:
        return {
            "answer": f"LLM error: {str(e)}",
            "sources": sources
        }

    return {
        "answer": answer.strip(),
        "sources": sources
    }