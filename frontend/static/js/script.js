const state = { action: "chat", busy: false };
const $ = (id) => document.getElementById(id);
const conversation = $("conversation");
const promptInput = $("promptInput");
const codeInput = $("codeInput");

function setAction(action) {
  state.action = action;
  const labels = {chat:"AI Assistant",generate:"Code Generator",debug:"Debug Code",explain:"Explain Code",optimize:"Optimize Code",convert:"Convert Language"};
  $("modeLabel").textContent = labels[action] || "AI Assistant";
  document.querySelectorAll(".nav-item").forEach(btn => btn.classList.toggle("active", btn.dataset.action === action));
  const convert = action === "convert";
  $("targetLanguage").classList.toggle("hidden", !convert);
  $("targetLabel").classList.toggle("hidden", !convert);
  $("welcomePanel").classList.add("hidden");
  const placeholders = {
    chat:"Ask a programming question…",
    generate:"Describe the program you want to create…",
    debug:"Describe the error, if known…",
    explain:"What would you like to understand about this code?",
    optimize:"What should be improved? (optional)",
    convert:"Any special instructions for the conversion? (optional)"
  };
  promptInput.placeholder = placeholders[action] || placeholders.chat;
}

function addMessage(role, text, isLoading=false) {
  const item = document.createElement("div");
  item.className = `message ${role}`;
  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = role === "user" ? "YOU" : "CODEMATE AI";
  const body = document.createElement("div");
  body.textContent = text;
  if (isLoading) body.classList.add("loading");
  item.append(label, body);
  conversation.appendChild(item);
  item.scrollIntoView({behavior:"smooth", block:"nearest"});
  return {item, body};
}

async function sendMessage() {
  if (state.busy) return;
  const prompt = promptInput.value.trim();
  const code = codeInput.value.trim();
  if (!prompt && !code) {
    promptInput.focus();
    return;
  }
  const action = state.action;
  const language = $("languageSelect").value;
  const target_language = $("targetLanguage").value;
  const userText = [prompt, code ? `Code:\n${code}` : ""].filter(Boolean).join("\n\n");
  addMessage("user", userText);
  promptInput.value = "";
  const loading = addMessage("assistant", "Thinking…", true);
  state.busy = true;
  $("sendBtn").disabled = true;

  try {
    const response = await fetch("/api/assist", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({action, prompt, code, language, target_language})
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Request failed.");
    loading.body.textContent = result.answer;
    loading.body.classList.remove("loading");
    loadHistory();
  } catch (error) {
    loading.body.textContent = `Error: ${error.message}`;
    loading.body.classList.remove("loading");
  } finally {
    state.busy = false;
    $("sendBtn").disabled = false;
    promptInput.focus();
  }
}

async function loadHistory() {
  try {
    const response = await fetch("/api/history");
    const data = await response.json();
    const list = $("historyList");
    list.replaceChildren();
    if (!data.items.length) {
      const empty = document.createElement("span");
      empty.className = "muted small";
      empty.textContent = "No activity yet";
      list.appendChild(empty);
      return;
    }
    data.items.slice(0, 8).forEach(item => {
      const button = document.createElement("button");
      button.className = "history-entry";
      button.textContent = `${item.action} · ${item.prompt || "Code request"}`;
      button.title = button.textContent;
      list.appendChild(button);
    });
  } catch (_) {
    $("historyList").textContent = "History unavailable";
  }
}

document.querySelectorAll("[data-action]").forEach(button => {
  button.addEventListener("click", () => setAction(button.dataset.action));
});
$("sendBtn").addEventListener("click", sendMessage);
promptInput.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});
$("toggleCodeBtn").addEventListener("click", () => {
  codeInput.classList.toggle("hidden");
  $("toggleCodeBtn").textContent = codeInput.classList.contains("hidden") ? "＋ Add code" : "− Hide code";
  if (!codeInput.classList.contains("hidden")) codeInput.focus();
});
$("newChatBtn").addEventListener("click", () => {
  conversation.replaceChildren();
  promptInput.value = "";
  codeInput.value = "";
  $("welcomePanel").classList.remove("hidden");
  setAction("chat");
});
$("clearHistoryBtn").addEventListener("click", async () => {
  if (!confirm("Clear all saved request history?")) return;
  await fetch("/api/history", {method:"DELETE"});
  loadHistory();
});
document.querySelectorAll(".quick-card").forEach(button => {
  button.addEventListener("click", () => {
    setAction(button.dataset.action);
    promptInput.focus();
  });
});
loadHistory();
