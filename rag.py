import os
import re
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
from langchain_core.documents import Document

# ----------------------------
# CLEAN FILE NAME
# ----------------------------
UUID_PREFIX_RE = re.compile(r'^[0-9a-fA-F\-]{36}_(.+)$')

def normalize_source_name(path):
    base = os.path.basename(path)
    match = UUID_PREFIX_RE.match(base)
    return match.group(1) if match else base


# ----------------------------
# ✅ ULTRA LIGHT EMBEDDINGS
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
# CHUNKING (REDUCED)
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
# SIMPLE ANSWER GENERATOR
# ----------------------------
def generate_answer(context, question):
    # VERY LIGHT LOGIC (no LLM)
    return f"""Answer based on uploaded PDFs:

{context[:1500]}

---

Question: {question}
"""


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

    sources = []
    seen = set()

    for doc in docs:
        meta = doc.metadata
        key = f"{meta['source']}-{meta['page']}"

        if key not in seen:
            seen.add(key)
            sources.append({
                "source": normalize_source_name(meta["source"]),
                "page": meta["page"]
            })

    answer = generate_answer(context, question)

    return {
        "answer": answer.strip(),
        "sources": sources
    }