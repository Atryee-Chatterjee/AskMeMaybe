from flask import Flask, render_template, request, jsonify, send_from_directory, abort
import os
import uuid

from rag import get_pdf_documents, get_text_chunks, create_vector_store, ask_question

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
VECTOR_DB_PATH = "faiss_index"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ----------------------------
# UPLOAD
# ----------------------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        files = request.files.getlist("pdfs")

        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        paths = []

        for file in files:
            if file.filename == "":
                continue

            # ✅ FILE SIZE LIMIT (2MB)
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)

            if size > 2 * 1024 * 1024:
                return jsonify({"error": "File too large (max 2MB)"}), 400

            filename = f"{uuid.uuid4()}_{file.filename}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            paths.append(path)

        if not paths:
            return jsonify({"error": "No valid files"}), 400

        docs = get_pdf_documents(paths)

        if not docs:
            return jsonify({"error": "No text extracted"}), 400

        chunks = get_text_chunks(docs)

        if not chunks:
            return jsonify({"error": "Chunking failed"}), 500

        create_vector_store(chunks)

        return jsonify({
            "message": f"{len(paths)} PDFs processed successfully"
        })

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# ----------------------------
# ASK
# ----------------------------
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        question = data.get("question")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        result = ask_question(question)

        return jsonify(result)

    except Exception as e:
        print("ASK ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# ----------------------------
# SERVE PDF
# ----------------------------
@app.route("/pdf/<path:filename>")
def serve_pdf(filename):
    try:
        return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename)
    except Exception:
        abort(404)


# ----------------------------
# HEALTH
# ----------------------------
@app.route("/health")
def health():
    return {"status": "ok"}, 200


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)