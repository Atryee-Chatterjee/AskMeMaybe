import streamlit as st
from pypdf import PdfReader
import os

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline


from dotenv import load_dotenv
load_dotenv()

# ----------------------------
# ⚡ CACHE EMBEDDINGS
# ----------------------------
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# ----------------------------
# 📄 PDF Reader
# ----------------------------
def get_pdf_text(pdf_docs):
    text = ""

    for pdf in pdf_docs:
        try:
            reader = PdfReader(pdf)

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        except:
            st.warning(f"⚠️ Skipped corrupted PDF: {pdf.name}")

    return text


# ----------------------------
# ✂️ Chunking
# ----------------------------
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_text(text)


# ----------------------------
# 🧠 VECTOR STORE
# ----------------------------
def get_vector_store(text_chunks):
    embeddings = get_embeddings()

    vector_store = FAISS.from_texts(
        text_chunks,
        embedding=embeddings
    )

    vector_store.save_local("faiss_index")


# ----------------------------
# 🤖 LLM (CACHED)
# ----------------------------
@st.cache_resource
def get_llm():
    llm = HuggingFaceEndpoint(
        task="text-generation",
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        temperature=0.3
    )

    return ChatHuggingFace(llm=llm)


# ----------------------------
# 🔍 QUERY FUNCTION
# ----------------------------
def user_input(user_question):

    embeddings = get_embeddings()

    db = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = db.similarity_search(user_question)

    context = "\n".join([doc.page_content for doc in docs])

    llm = get_llm()
    prompt = f"""
You are a helpful AI assistant.

Use ONLY the context below to answer the question.
If answer is not in context, say "I don't know based on the document."

Context:
{context}

Question:
{user_question}

Answer in a clear and simple way:
"""

    response = llm.invoke(prompt)

    st.write("🤖 Reply:")
    st.write(response.content)


# ----------------------------
# 🖥️ STREAMLIT UI
# ----------------------------
def main():
    st.set_page_config(page_title="AskMeMaybe")
    st.header("📄 AskMeMaybe – Chat with PDFs (Offline RAG)")

    user_question = st.text_input("Ask a question from your PDFs")

    if user_question:
        if os.path.exists("faiss_index"):
            user_input(user_question)
        else:
            st.error("⚠️ Please upload and process PDFs first!")

    with st.sidebar:
        st.title("📂 Menu")

        pdf_docs = st.file_uploader(
            "Upload PDF files",
            accept_multiple_files=True
        )

        if st.button("Submit & Process"):
            if not pdf_docs:
                st.warning("Please upload PDFs first.")
                return

            with st.spinner("Processing PDFs..."):

                raw_text = get_pdf_text(pdf_docs)

                if not raw_text.strip():
                    st.error("No text extracted from PDF.")
                    return

                chunks = get_text_chunks(raw_text)
                get_vector_store(chunks)

                st.success("PDF processed successfully 🚀")


if __name__ == "__main__":
    main()