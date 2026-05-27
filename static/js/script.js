// Enhanced frontend with all requested features
let conversationHistory = [];
let uploadedFileNames = [];
let pendingUploadFiles = [];

// DOM elements
const chatContainer = document.getElementById("chatMessagesContainer");
const questionInput = document.getElementById("userQuestionInput");
const sendBtn = document.getElementById("sendMessageBtn");
const processBtn = document.getElementById("processBtn");
const attachFileBtn = document.getElementById("attachFileBtn");
const pdfFileInput = document.getElementById("pdfUploadInput");
const fileStatusArea = document.getElementById("fileStatusArea");
const historyListDiv = document.getElementById("historyList");
const clearChatSideBtn = document.getElementById("clearChatBtn");
const globalLoader = document.getElementById("globalLoader");
const clearInputBtn = document.getElementById("clearInputBtn");
const toastEl = document.getElementById("toastNotification");

// Mobile elements
const mobileToggle = document.getElementById("mobileMenuToggle");
const mobileOverlay = document.getElementById("mobileOverlay");
const sidebar = document.getElementById("sidebar");
const closeSidebarBtn = document.getElementById("closeSidebarMobile");

function showToast(message, duration = 2500) {
  toastEl.textContent = message;
  toastEl.classList.add("show");
  setTimeout(() => {
    toastEl.classList.remove("show");
  }, duration);
}

function showLoader(text = "Processing...") {
  const loaderText = globalLoader.querySelector(".loader-text");
  if (loaderText) loaderText.innerText = text;
  globalLoader.style.display = "flex";
}
function hideLoader() {
  globalLoader.style.display = "none";
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>]/g, function (m) {
    if (m === "&") return "&amp;";
    if (m === "<") return "&lt;";
    if (m === ">") return "&gt;";
    return m;
  });
}

function formatAnswerText(text) {
  if (!text) return "";

  let normalized = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  normalized = escapeHtml(normalized);
  normalized = normalized.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  normalized = normalized.replace(/\*(.*?)\*/g, "<em>$1</em>");

  const lines = normalized.split("\n");
  let html = "";
  let paragraphLines = [];
  let inList = false;
  let listTag = "";

  const closeParagraph = () => {
    if (paragraphLines.length) {
      html += `<p>${paragraphLines.join("<br>")}</p>`;
      paragraphLines = [];
    }
  };

  const closeList = () => {
    if (inList) {
      html += `</${listTag}>`;
      inList = false;
      listTag = "";
    }
  };

  lines.forEach((line) => {
    const trimmed = line.trim();

    if (!trimmed) {
      closeParagraph();
      closeList();
      return;
    }

    const unorderedMatch = trimmed.match(/^[\-•\*]\s+(.*)$/);
    const orderedMatch = trimmed.match(/^\d+[\.)]\s+(.*)$/);

    if (unorderedMatch) {
      closeParagraph();
      if (!inList || listTag !== "ul") {
        closeList();
        html += "<ul>";
        inList = true;
        listTag = "ul";
      }
      html += `<li>${unorderedMatch[1]}</li>`;
      return;
    }

    if (orderedMatch) {
      closeParagraph();
      if (!inList || listTag !== "ol") {
        closeList();
        html += "<ol>";
        inList = true;
        listTag = "ol";
      }
      html += `<li>${orderedMatch[1]}</li>`;
      return;
    }

    if (inList) {
      closeList();
    }

    paragraphLines.push(trimmed);
  });

  closeParagraph();
  closeList();

  if (!html) {
    html = `<p>${normalized.replace(/\n/g, "<br>")}</p>`;
  }

  return html;
}

// Deduplicate sources (same file + page)
function deduplicateSources(sources) {
  const seen = new Set();
  return sources.filter((source) => {
    const key = `${source.source}|${source.page}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function updateFileSidebar() {
  if (!fileStatusArea) return;
  fileStatusArea.innerHTML = "";
  if (uploadedFileNames.length === 0) {
    fileStatusArea.innerHTML =
      '<div style="font-size:12px; opacity:0.6; padding:6px;"><i class="fa-regular fa-folder-open"></i> No PDFs uploaded</div>';
    updateClearChatButtonState();
    return;
  }
  uploadedFileNames.forEach((name, idx) => {
    const div = document.createElement("div");
    div.className = "file-item";
    div.innerHTML = `
            <i class="fa-regular fa-file-pdf"></i>
            <span title="${escapeHtml(name)}">${escapeHtml(name.length > 30 ? name.substring(0, 30) + "..." : name)}</span>
            <button class="delete-file-btn" data-filename="${escapeHtml(name)}" data-index="${idx}">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;
    fileStatusArea.appendChild(div);
  });
  document.querySelectorAll(".delete-file-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const fileName = btn.getAttribute("data-filename");
      deleteUploadedFile(fileName);
    });
  });
  updateClearChatButtonState();
}

function deleteUploadedFile(fileName) {
  const index = uploadedFileNames.indexOf(fileName);
  if (index !== -1) {
    uploadedFileNames.splice(index, 1);
    updateFileSidebar();
    showToast(`Removed ${fileName}`);
    if (uploadedFileNames.length === 0) {
      // Clear chat messages when all PDFs are removed
      const messages = chatContainer.querySelectorAll(".message");
      messages.forEach((msg) => msg.remove());
      conversationHistory = [];
      updateHistorySidebar();
      addMessageToChat(`All PDFs removed. Upload new PDFs to continue!`, "bot");
    }
    updateClearChatButtonState();
  }
}

function updateClearChatButtonState() {
  if (clearChatSideBtn) {
    clearChatSideBtn.disabled = uploadedFileNames.length === 0;
  }
}

function addMessageToChat(text, type, sources = null) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${type === "user" ? "user-message" : "bot-message"}`;

  const avatarIcon =
    type === "user"
      ? '<i class="fa-regular fa-user"></i>'
      : '<i class="fa-solid fa-robot"></i>';
  let formattedText =
    type === "bot" ? formatAnswerText(text) : escapeHtml(text);

  let bubbleContent = `<div class="avatar">${avatarIcon}</div><div class="message-bubble"><div>${formattedText}</div>`;

  if (sources && sources.length > 0 && type === "bot") {
    bubbleContent += '<div class="source-citation"></div>';
  }
  bubbleContent += `</div>`;
  messageDiv.innerHTML = bubbleContent;

  if (sources && sources.length > 0 && type === "bot") {
    const uniqueSources = deduplicateSources(sources);
    const citation = messageDiv.querySelector(".source-citation");
    uniqueSources.forEach((src) => {
      const sourceItem = document.createElement("div");
      sourceItem.className = "source-item";

      const icon = document.createElement("i");
      icon.className = "fa-regular fa-file-lines";
      sourceItem.appendChild(icon);

      const fileLink = document.createElement("a");
      fileLink.href = "#";
      fileLink.className = "source-link";
      fileLink.dataset.file = src.file_name;
      fileLink.dataset.page = String(src.page);
      fileLink.textContent = src.source;
      sourceItem.appendChild(fileLink);

      const separator = document.createTextNode(" — page ");
      sourceItem.appendChild(separator);

      const pageLink = document.createElement("a");
      pageLink.href = "#";
      pageLink.className = "source-link";
      pageLink.dataset.file = src.file_name;
      pageLink.dataset.page = String(src.page);
      pageLink.textContent = String(src.page);
      sourceItem.appendChild(pageLink);

      citation.appendChild(sourceItem);
    });
  }

  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  return messageDiv;
}

const pdfPreviewModal = document.getElementById("pdfPreviewModal");
const pdfPreviewFrame = document.getElementById("pdfPreviewFrame");
const pdfPreviewTitle = document.getElementById("pdfPreviewTitle");
const closePdfPreviewBtn = document.getElementById("closePdfPreviewBtn");
const openPdfInTabBtn = document.getElementById("openPdfInTabBtn");
let currentPreviewUrl = "";

function openPdfPreview(fileName, page) {
  if (!pdfPreviewModal || !pdfPreviewFrame || !pdfPreviewTitle) return;
  const url = `/pdf/${encodeURIComponent(fileName)}#page=${page}`;
  currentPreviewUrl = url;
  pdfPreviewTitle.textContent = `${fileName} — Page ${page}`;
  pdfPreviewFrame.src = url;
  pdfPreviewModal.classList.add("open");
  pdfPreviewModal.setAttribute("aria-hidden", "false");
}

function closePdfPreview() {
  if (!pdfPreviewModal || !pdfPreviewFrame) return;
  pdfPreviewModal.classList.remove("open");
  pdfPreviewModal.setAttribute("aria-hidden", "true");
  pdfPreviewFrame.src = "";
  currentPreviewUrl = "";
}

if (closePdfPreviewBtn) {
  closePdfPreviewBtn.addEventListener("click", closePdfPreview);
}  

if (openPdfInTabBtn) {
  openPdfInTabBtn.addEventListener("click", () => {
    if (currentPreviewUrl) {
      window.open(currentPreviewUrl, "_blank");
    }
  });
}

if (pdfPreviewModal) {
  pdfPreviewModal.addEventListener("click", (event) => {
    if (event.target === pdfPreviewModal) {
      closePdfPreview();
    }
  });
}

chatContainer.addEventListener("click", (event) => {
  const sourceLink = event.target.closest(".source-link");
  if (!sourceLink) return;
  event.preventDefault();
  const fileName = sourceLink.dataset.file;
  const page = sourceLink.dataset.page;
  if (fileName && page) {
    openPdfPreview(fileName, page);
  }
});

let typingInterval = null;
let typingDiv = null;

function showTypingIndicator() {
  if (typingDiv) typingDiv.remove();
  if (typingInterval) clearInterval(typingInterval);

  typingDiv = document.createElement("div");
  typingDiv.className = "message bot-message";
  typingDiv.innerHTML = `<div class="avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="message-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
  chatContainer.appendChild(typingDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTypingIndicator() {
  if (typingDiv) {
    typingDiv.remove();
    typingDiv = null;
  }
  if (typingInterval) {
    clearInterval(typingInterval);
    typingInterval = null;
  }
}

function updateHistorySidebar() {
  if (!historyListDiv) return;
  if (conversationHistory.length === 0) {
    historyListDiv.innerHTML = `<div class="empty-history-placeholder"><i class="fa-regular fa-comment-dots"></i><span>No questions yet</span></div>`;
    return;
  }
  historyListDiv.innerHTML = "";
  conversationHistory.forEach((item, idx) => {
    const historyItem = document.createElement("div");
    historyItem.className = "history-question-item";
    historyItem.setAttribute("data-q-index", idx);
    historyItem.innerHTML = `<i class="fa-regular fa-circle-question"></i><div class="history-text">${escapeHtml(item.question.length > 38 ? item.question.substring(0, 38) + "..." : item.question)}</div>`;
    historyItem.addEventListener("click", () => {
      scrollToQuestionInChat(idx);
    });
    historyListDiv.appendChild(historyItem);
  });
}

function scrollToQuestionInChat(index) {
  const messages = chatContainer.querySelectorAll(".message");
  let userMsgCount = 0;
  for (let i = 0; i < messages.length; i++) {
    if (messages[i].classList.contains("user-message")) {
      if (userMsgCount === index) {
        messages[i].scrollIntoView({ behavior: "smooth", block: "center" });
        messages[i].style.transition = "0.2s";
        messages[i].style.backgroundColor = "rgba(168,85,247,0.3)";
        setTimeout(() => {
          messages[i].style.backgroundColor = "";
        }, 1000);
        break;
      }
      userMsgCount++;
    }
  }
}

async function askUserQuestion(question) {
  if (!question.trim()) return;
  if (uploadedFileNames.length === 0) {
    showToast("Please upload PDFs first");
    return;
  }

  addMessageToChat(question, "user");
  questionInput.value = "";

  showTypingIndicator();

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();
    removeTypingIndicator();

    if (response.status !== 200 || data.error) {
      const errorMsg =
        data.error || "Failed to get answer. Please upload PDFs first.";
      addMessageToChat(`⚠️ ${errorMsg}`, "bot");
      return;
    }

    const answerText = data.answer || "No answer generated.";
    const sourcesArr = data.sources || [];

    addMessageToChat(answerText, "bot", sourcesArr);

    conversationHistory.push({
      question: question,
      answer: answerText,
      sources: sourcesArr,
    });
    updateHistorySidebar();
  } catch (err) {
    removeTypingIndicator();
    addMessageToChat(`⚠️ Network error: ${err.message}`, "bot");
  }
}

async function uploadAndProcessPDFs() {
  if (!pendingUploadFiles || pendingUploadFiles.length === 0) {
    showToast("Select PDF files first");
    return;
  }

  const formData = new FormData();
  const fileNames = [];
  for (let i = 0; i < pendingUploadFiles.length; i++) {
    formData.append("pdfs", pendingUploadFiles[i]);
    fileNames.push(pendingUploadFiles[i].name);
  }

  showLoader(`Processing ${fileNames.length} PDF(s)...`);
  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();
    hideLoader();

    if (response.status !== 200 || result.error) {
      addMessageToChat(
        `❌ Upload failed: ${result.error || "Unknown error"}`,
        "bot",
      );
      return;
    }

    for (let name of fileNames) {
      if (!uploadedFileNames.includes(name)) {
        uploadedFileNames.push(name);
      }
    }
    updateFileSidebar();
    showToast(
      `✅ ${fileNames.length} PDF${fileNames.length > 1 ? "s" : ""} processed successfully`,
    );
    addMessageToChat(
      `✅ ${fileNames.length} PDF${fileNames.length > 1 ? "s" : ""} processed successfully: ${fileNames.join(", ")}`,
      "bot",
    );
    addMessageToChat(
      `Hi! I've analyzed your document${fileNames.length > 1 ? "s" : ""}. What would you like to know?`,
      "bot",
    );
    resetPendingFiles();
  } catch (err) {
    hideLoader();
    addMessageToChat(`⚠️ Upload error: ${err.message}`, "bot");
  }
}

function clearChatAndHistory() {
  if (uploadedFileNames.length === 0 && conversationHistory.length === 0)
    return;
  const messages = chatContainer.querySelectorAll(".message");
  messages.forEach((msg) => msg.remove());
  conversationHistory = [];
  updateHistorySidebar();
  addMessageToChat(
    `Chat cleared. Upload more PDFs or continue asking questions!`,
    "bot",
  );
  updateClearChatButtonState();
}

// Event Listeners
sendBtn.addEventListener("click", () => {
  const q = questionInput.value.trim();
  if (q) askUserQuestion(q);
});

questionInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    const q = questionInput.value.trim();
    if (q) askUserQuestion(q);
  }
});

clearInputBtn.addEventListener("click", () => {
  questionInput.value = "";
  questionInput.focus();
});

if (attachFileBtn) {
  attachFileBtn.addEventListener("click", () => {
    if (pdfFileInput) pdfFileInput.click();
  });
}

function addPendingFiles(fileList) {
  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i];
    const exists = pendingUploadFiles.some(
      (p) => p.name === file.name && p.size === file.size,
    );
    if (!exists) pendingUploadFiles.push(file);
  }
}

function resetPendingFiles() {
  pendingUploadFiles = [];
  if (pdfFileInput) pdfFileInput.value = "";
}

if (pdfFileInput) {
  pdfFileInput.addEventListener("change", () => {
    if (pdfFileInput.files.length > 0) {
      addPendingFiles(pdfFileInput.files);
      showToast(
        `${pendingUploadFiles.length} PDF file(s) selected. Click Process Files to upload.`,
      );
    }
  });
}

processBtn.addEventListener("click", () => {
  if (pendingUploadFiles.length === 0) {
    showToast("Select PDF files first");
    return;
  }
  uploadAndProcessPDFs();
});

clearChatSideBtn.addEventListener("click", clearChatAndHistory);

// Mobile sidebar handlers
function closeMobileSidebar() {
  sidebar.classList.remove("open");
  mobileOverlay.classList.remove("active");
}

function openMobileSidebar() {
  sidebar.classList.add("open");
  mobileOverlay.classList.add("active");
}

if (mobileToggle) mobileToggle.addEventListener("click", openMobileSidebar);
if (closeSidebarBtn)
  closeSidebarBtn.addEventListener("click", closeMobileSidebar);
if (mobileOverlay) mobileOverlay.addEventListener("click", closeMobileSidebar);

window.addEventListener("DOMContentLoaded", () => {
  updateFileSidebar();
  updateHistorySidebar();
  if (chatContainer.children.length === 0) {
    addMessageToChat(
      `Welcome to AskMeMaybe! Upload your PDF documents using the sidebar. I'll help you extract insights.`,
      "bot",
    );
  }
});
