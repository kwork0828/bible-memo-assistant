const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

const apiBaseUrlInput = document.querySelector("#apiBaseUrl");
const saveApiBaseUrlButton = document.querySelector("#saveApiBaseUrl");
const refreshAllButton = document.querySelector("#refreshAll");
const summaryCards = document.querySelector("#summaryCards");
const dataForm = document.querySelector("#dataForm");
const editingDataIdInput = document.querySelector("#editingDataId");
const dataDateInput = document.querySelector("#dataDate");
const dataValueInput = document.querySelector("#dataValue");
const dataMemoInput = document.querySelector("#dataMemo");
const saveDataButton = document.querySelector("#saveDataButton");
const cancelEditButton = document.querySelector("#cancelEditButton");
const dataStatus = document.querySelector("#dataStatus");
const dataTableBody = document.querySelector("#dataTableBody");
const chatMessages = document.querySelector("#chatMessages");
const chatStatus = document.querySelector("#chatStatus");
const chatForm = document.querySelector("#chatForm");
const chatInput = document.querySelector("#chatInput");
const sendChatButton = document.querySelector("#sendChatButton");
const newConversationButton = document.querySelector("#newConversation");
const conversationList = document.querySelector("#conversationList");

let dataItems = [];
let currentConversationId = null;

function getApiBaseUrl() {
  const value = apiBaseUrlInput.value.trim() || DEFAULT_API_BASE_URL;
  return value.replace(/\/$/, "");
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  let body = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const detail = body?.detail || `HTTP ${response.status}`;
    throw new Error(detail);
  }
  return body;
}

function setStatus(element, message = "", type = "") {
  element.textContent = message;
  element.className = `status${type ? ` ${type}` : ""}`;
}

function createSummaryCard(label, value) {
  const card = document.createElement("div");
  card.className = "summary-card";

  const labelElement = document.createElement("span");
  labelElement.textContent = label;
  const valueElement = document.createElement("strong");
  valueElement.textContent = value ?? "-";

  card.append(labelElement, valueElement);
  return card;
}

async function loadSummary() {
  summaryCards.replaceChildren(createSummaryCard("상태", "불러오는 중..."));
  try {
    const summary = await apiFetch("/api/data/summary");
    summaryCards.replaceChildren(
      createSummaryCard("데이터 수", summary.count),
      createSummaryCard("총 단어 수", summary.total_value),
      createSummaryCard("평균 단어 수", summary.average_value),
      createSummaryCard("첫 일정", summary.first_date || "없음"),
      createSummaryCard("마지막 일정", summary.last_date || "없음"),
    );
  } catch (error) {
    summaryCards.replaceChildren(createSummaryCard("오류", error.message));
  }
}

function resetDataForm() {
  editingDataIdInput.value = "";
  dataForm.reset();
  dataMemoInput.value = '{"new": [], "review": []}';
  saveDataButton.textContent = "데이터 추가";
  cancelEditButton.hidden = true;
}

function renderDataTable() {
  dataTableBody.replaceChildren();

  if (!dataItems.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = "저장된 데이터가 없습니다.";
    row.append(cell);
    dataTableBody.append(row);
    return;
  }

  for (const item of dataItems) {
    const row = document.createElement("tr");

    const dateCell = document.createElement("td");
    dateCell.textContent = item.date || "-";

    const valueCell = document.createElement("td");
    valueCell.textContent = String(item.value ?? 0);

    const memoCell = document.createElement("td");
    const memoPre = document.createElement("pre");
    memoPre.textContent = JSON.stringify(item.memo || {}, null, 2);
    memoCell.append(memoPre);

    const actionCell = document.createElement("td");
    const actions = document.createElement("div");
    actions.className = "table-actions";

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "secondary";
    editButton.textContent = "수정";
    editButton.addEventListener("click", () => {
      editingDataIdInput.value = item.id;
      dataDateInput.value = item.date || "";
      dataValueInput.value = item.value ?? 0;
      dataMemoInput.value = JSON.stringify(item.memo || {}, null, 2);
      saveDataButton.textContent = "수정 저장";
      cancelEditButton.hidden = false;
      dataDateInput.focus();
    });

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "삭제";
    deleteButton.addEventListener("click", async () => {
      const approved = window.confirm(`${item.date || "이 데이터"}를 정말 삭제할까요?`);
      if (!approved) return;

      try {
        await apiFetch(`/api/data/${encodeURIComponent(item.id)}`, { method: "DELETE" });
        setStatus(dataStatus, "데이터를 삭제했습니다.", "success");
        await Promise.all([loadData(), loadSummary()]);
      } catch (error) {
        setStatus(dataStatus, error.message, "error");
      }
    });

    actions.append(editButton, deleteButton);
    actionCell.append(actions);
    row.append(dateCell, valueCell, memoCell, actionCell);
    dataTableBody.append(row);
  }
}

async function loadData() {
  setStatus(dataStatus, "데이터를 불러오는 중...");
  try {
    const result = await apiFetch("/api/data");
    dataItems = result.items || [];
    renderDataTable();
    setStatus(dataStatus, `${result.count ?? dataItems.length}건을 불러왔습니다.`, "success");
  } catch (error) {
    dataItems = [];
    renderDataTable();
    setStatus(dataStatus, error.message, "error");
  }
}

function appendChatBubble(role, content) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  bubble.textContent = content;
  chatMessages.append(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderConversationMessages(messages = []) {
  chatMessages.replaceChildren();
  if (!messages.length) {
    appendChatBubble("assistant", "암송 일정에 대해 궁금한 점을 물어보세요.");
    return;
  }
  for (const message of messages) {
    if (message.role === "user" || message.role === "assistant") {
      appendChatBubble(message.role, message.content || "");
    }
  }
}

async function loadConversation(conversationId) {
  setStatus(chatStatus, "대화를 불러오는 중...");
  try {
    const conversation = await apiFetch(`/api/conversations/${encodeURIComponent(conversationId)}`);
    currentConversationId = conversation.id;
    renderConversationMessages(conversation.messages || []);
    setStatus(chatStatus, "이전 대화를 불러왔습니다.", "success");
  } catch (error) {
    setStatus(chatStatus, error.message, "error");
  }
}

function renderConversationList(items = []) {
  conversationList.replaceChildren();

  if (!items.length) {
    const empty = document.createElement("p");
    empty.textContent = "저장된 대화가 없습니다.";
    conversationList.append(empty);
    return;
  }

  for (const item of items) {
    const wrapper = document.createElement("div");
    wrapper.className = "conversation-item";

    const info = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = item.title || "새 대화";
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = item.updated_at || item.created_at || "";
    info.append(title, meta);

    const actions = document.createElement("div");
    actions.className = "table-actions";

    const loadButton = document.createElement("button");
    loadButton.type = "button";
    loadButton.textContent = "불러오기";
    loadButton.addEventListener("click", () => loadConversation(item.id));

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "secondary";
    deleteButton.textContent = "삭제";
    deleteButton.addEventListener("click", async () => {
      const approved = window.confirm("이 대화를 정말 삭제할까요?");
      if (!approved) return;
      try {
        await apiFetch(`/api/conversations/${encodeURIComponent(item.id)}`, { method: "DELETE" });
        if (currentConversationId === item.id) {
          currentConversationId = null;
          renderConversationMessages([]);
        }
        await loadConversations();
      } catch (error) {
        setStatus(chatStatus, error.message, "error");
      }
    });

    actions.append(loadButton, deleteButton);
    wrapper.append(info, actions);
    conversationList.append(wrapper);
  }
}

async function loadConversations() {
  try {
    const result = await apiFetch("/api/conversations");
    renderConversationList(result.items || []);
  } catch (error) {
    conversationList.replaceChildren();
    const message = document.createElement("p");
    message.textContent = `대화 목록 오류: ${error.message}`;
    conversationList.append(message);
  }
}

async function refreshAll() {
  await Promise.all([loadSummary(), loadData(), loadConversations()]);
}

saveApiBaseUrlButton.addEventListener("click", async () => {
  localStorage.setItem("BIBLE_MEMO_API_BASE_URL", getApiBaseUrl());
  await refreshAll();
});

refreshAllButton.addEventListener("click", refreshAll);

cancelEditButton.addEventListener("click", () => {
  resetDataForm();
  setStatus(dataStatus, "수정을 취소했습니다.");
});

dataForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(dataStatus, "저장 중...");

  let memo;
  try {
    memo = JSON.parse(dataMemoInput.value || "{}");
    if (Array.isArray(memo) || memo === null || typeof memo !== "object") {
      throw new Error("memo는 JSON 객체여야 합니다.");
    }
  } catch (error) {
    setStatus(dataStatus, `memo JSON 오류: ${error.message}`, "error");
    return;
  }

  const payload = {
    date: dataDateInput.value,
    value: Number(dataValueInput.value),
    memo,
  };
  const editingId = editingDataIdInput.value;

  try {
    if (editingId) {
      await apiFetch(`/api/data/${encodeURIComponent(editingId)}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      setStatus(dataStatus, "데이터를 수정했습니다.", "success");
    } else {
      await apiFetch("/api/data", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setStatus(dataStatus, "데이터를 추가했습니다.", "success");
    }
    resetDataForm();
    await Promise.all([loadData(), loadSummary()]);
  } catch (error) {
    setStatus(dataStatus, error.message, "error");
  }
});

newConversationButton.addEventListener("click", () => {
  currentConversationId = null;
  renderConversationMessages([]);
  setStatus(chatStatus, "새 대화를 시작합니다.");
  chatInput.focus();
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  sendChatButton.disabled = true;
  chatInput.disabled = true;
  setStatus(chatStatus, "AI 답변을 생성하는 중...");

  try {
    const result = await apiFetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: currentConversationId,
      }),
    });
    appendChatBubble("user", message);
    appendChatBubble("assistant", result.reply);
    currentConversationId = result.conversation_id;
    chatInput.value = "";
    setStatus(chatStatus, "답변을 받았습니다.", "success");
    await Promise.all([loadConversations(), loadSummary()]);
  } catch (error) {
    setStatus(chatStatus, error.message, "error");
  } finally {
    sendChatButton.disabled = false;
    chatInput.disabled = false;
    chatInput.focus();
  }
});

apiBaseUrlInput.value = localStorage.getItem("BIBLE_MEMO_API_BASE_URL") || DEFAULT_API_BASE_URL;
renderConversationMessages([]);
refreshAll();
