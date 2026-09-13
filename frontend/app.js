const verses = [
    { ref: "Philippians 4:13", stage: "D+3 복습", text: "I can do all things through Christ, who strengthens me.", ko: "내게 능력 주시는 자 안에서 내가 모든 것을 할 수 있느니라." },
    { ref: "Psalm 119:105", stage: "D+7 복습", text: "Your word is a lamp to my feet, and a light for my path.", ko: "주의 말씀은 내 발에 등이요 내 길에 빛이니이다." },
    { ref: "Romans 8:28", stage: "D+0 신규", text: "We know that all things work together for good for those who love God.", ko: "하나님을 사랑하는 자들에게는 모든 것이 합력하여 선을 이룹니다." },
    { ref: "John 3:16", stage: "D+30 복습", text: "For God so loved the world, that he gave his one and only Son.", ko: "하나님이 세상을 이처럼 사랑하사 독생자를 주셨습니다." }
];

const builtInBible = [
    { id: "web-php-4-13", reference: "Philippians 4:13", text: "I can do all things through Christ, who strengthens me.", source: "WEB", uploaded: false },
    { id: "web-psa-119-105", reference: "Psalm 119:105", text: "Your word is a lamp to my feet, and a light for my path.", source: "WEB", uploaded: false },
    { id: "web-rom-8-28", reference: "Romans 8:28", text: "We know that all things work together for good for those who love God.", source: "WEB", uploaded: false },
    { id: "web-jhn-3-16", reference: "John 3:16", text: "For God so loved the world, that he gave his one and only Son.", source: "WEB", uploaded: false },
    { id: "web-isa-41-10", reference: "Isaiah 41:10", text: "Don't you be afraid, for I am with you. Don't be dismayed, for I am your God.", source: "WEB", uploaded: false }
];

function readStoredArray(key) {
    try {
        const value = JSON.parse(localStorage.getItem(key) || "[]");
        return Array.isArray(value) ? value : [];
    } catch {
        return [];
    }
}

let uploadedBible = readStoredArray("versemate_uploaded_bible");
let favoriteIds = new Set(readStoredArray("versemate_favorites"));
let libraryFilter = "all";

let currentVerse = 0;
let completed = 3;
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const date = new Intl.DateTimeFormat("ko-KR", { month: "long", day: "numeric", weekday: "long" }).format(new Date());
$("#todayDate").textContent = date;

function showView(name) {
    $$(".view").forEach((view) => view.classList.toggle("active-view", view.id === name));
    $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === name));
    const titles = { home: "오늘도 말씀 한 구절", schedule: "복습 흐름을 한눈에", library: "나만의 영어성경 보관함", coach: "내 진도를 아는 AI 코치", records: "쌓여가는 암송 기록" };
    $("#pageTitle").textContent = titles[name];
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderVerse() {
    const verse = verses[currentVerse];
    $("#verseRef").textContent = verse.ref;
    $("#verseStage").textContent = verse.stage;
    $("#verseText").textContent = `“${verse.text}”`;
    $("#verseTranslation").textContent = verse.ko;
    $("#verseNumber").textContent = currentVerse + 1;
    $("#recallInput").value = "";
    $("#recallFeedback").textContent = "";
}

function toast(message) {
    const element = $("#toast");
    element.textContent = message;
    element.classList.add("show");
    setTimeout(() => element.classList.remove("show"), 2200);
}

function allBibleVerses() {
    return [...builtInBible, ...uploadedBible];
}

function renderLibrary() {
    const query = $("#bibleSearch").value.trim().toLowerCase();
    const allVerses = allBibleVerses();
    const visible = allVerses.filter((verse) => {
        const matchesQuery = `${verse.reference} ${verse.text}`.toLowerCase().includes(query);
        const matchesFilter = libraryFilter === "all"
            || (libraryFilter === "favorites" && favoriteIds.has(verse.id))
            || (libraryFilter === "uploaded" && verse.uploaded);
        return matchesQuery && matchesFilter;
    });

    $("#allCount").textContent = allVerses.length;
    $("#favoriteCount").textContent = favoriteIds.size;
    $("#uploadedCount").textContent = uploadedBible.length;
    $("#libraryEmpty").hidden = visible.length > 0;
    $("#bibleList").replaceChildren();

    visible.forEach((verse) => {
        const item = document.createElement("article");
        item.className = "bible-item";
        const content = document.createElement("div");
        const heading = document.createElement("h3");
        heading.textContent = verse.reference;
        const text = document.createElement("p");
        text.textContent = verse.text;
        const meta = document.createElement("div");
        meta.className = "verse-meta";
        const source = document.createElement("span");
        source.className = "source-badge";
        source.textContent = verse.source;
        const words = document.createElement("span");
        words.textContent = `${verse.text.trim().split(/\s+/).length} words`;
        meta.append(source, words);
        content.append(heading, text, meta);

        const favorite = document.createElement("button");
        const isFavorite = favoriteIds.has(verse.id);
        favorite.className = `favorite-button${isFavorite ? " active" : ""}`;
        favorite.textContent = isFavorite ? "★" : "☆";
        favorite.setAttribute("aria-label", `${verse.reference} ${isFavorite ? "즐겨찾기 해제" : "즐겨찾기 추가"}`);
        favorite.addEventListener("click", () => toggleFavorite(verse.id));
        item.append(content, favorite);
        $("#bibleList").appendChild(item);
    });
}

function toggleFavorite(id) {
    if (favoriteIds.has(id)) {
        favoriteIds.delete(id);
        toast("즐겨찾기에서 해제했습니다.");
    } else {
        favoriteIds.add(id);
        toast("즐겨찾기에 저장했습니다.");
    }
    localStorage.setItem("versemate_favorites", JSON.stringify([...favoriteIds]));
    renderLibrary();
}

function normalizeUploadedVerse(value, index) {
    const reference = String(value.reference || value.ref || "").trim();
    const text = String(value.text || "").trim();
    if (!reference || !text || !/[A-Za-z]/.test(text) || /[가-힣ㄱ-ㅎㅏ-ㅣ]/.test(text)) {
        throw new Error(`${index + 1}번째 항목은 영어 성경 구절 형식이 아닙니다.`);
    }
    return {
        id: value.id || `upload-${Date.now()}-${index}`,
        reference,
        text,
        source: "내 파일",
        uploaded: true
    };
}

function parseBibleFile(fileName, rawText) {
    if (fileName.toLowerCase().endsWith(".json")) {
        const parsed = JSON.parse(rawText);
        if (!Array.isArray(parsed)) throw new Error("JSON 최상위 값은 배열이어야 합니다.");
        return parsed.map(normalizeUploadedVerse);
    }
    return rawText.split(/\r?\n/).filter((line) => line.trim()).map((line, index) => {
        const separator = line.indexOf("|");
        if (separator < 1) throw new Error(`${index + 1}번째 줄에 | 구분자가 없습니다.`);
        return normalizeUploadedVerse({ reference: line.slice(0, separator), text: line.slice(separator + 1) }, index);
    });
}

$$(".nav-item").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));
$$("[data-go]").forEach((button) => button.addEventListener("click", () => showView(button.dataset.go)));
$("#prevVerse").addEventListener("click", () => { currentVerse = (currentVerse + verses.length - 1) % verses.length; renderVerse(); });
$("#nextVerse").addEventListener("click", () => { currentVerse = (currentVerse + 1) % verses.length; renderVerse(); });
$("#toggleVerse").addEventListener("click", (event) => {
    const hidden = $("#verseText").classList.toggle("hidden");
    $("#verseTranslation").classList.toggle("hidden", hidden);
    event.target.textContent = hidden ? "본문 보기" : "본문 가리기";
});
$("#checkRecall").addEventListener("click", () => {
    const typed = $("#recallInput").value.toLowerCase().replace(/[^a-z ]/g, "").trim();
    const answer = verses[currentVerse].text.toLowerCase().replace(/[^a-z ]/g, "").trim();
    if (!typed) { $("#recallFeedback").textContent = "먼저 기억나는 문장을 적어보세요."; return; }
    const typedWords = new Set(typed.split(/\s+/));
    const answerWords = answer.split(/\s+/);
    const score = Math.round(answerWords.filter((word) => typedWords.has(word)).length / answerWords.length * 100);
    $("#recallFeedback").textContent = `핵심 단어 일치율 ${score}% · 본문과 비교해 보세요.`;
});
$("#completeVerse").addEventListener("click", () => {
    completed = Math.min(4, completed + 1);
    $("#heroPercent").textContent = `${completed * 25}%`;
    toast("오늘의 암송 기록에 저장했습니다.");
});

const dialog = $("#addDialog");
$("#openAddButton").addEventListener("click", () => dialog.showModal());
$$("[data-add]").forEach((button) => button.addEventListener("click", () => dialog.showModal()));
$("#saveVerse").addEventListener("click", (event) => {
    if (!$("#addForm").checkValidity()) { event.preventDefault(); $("#addForm").reportValidity(); return; }
    toast("목업 일정이 생성되었습니다. 실제 저장은 백엔드 연결 후 동작합니다.");
});

function sendChat(text) {
    if (!text.trim()) return;
    const messages = $("#messages");
    const user = document.createElement("div");
    user.className = "message user";
    user.textContent = text;
    messages.appendChild(user);
    setTimeout(() => {
        const ai = document.createElement("div");
        ai.className = "message ai";
        ai.textContent = "오늘 기록을 보면 복습 3절이 우선입니다. 10분씩 두 번 나누고, 정확도가 낮은 Psalm 119:105를 마지막에 다시 확인해 보세요.";
        messages.appendChild(ai);
        messages.scrollTop = messages.scrollHeight;
    }, 500);
}

$("#chatForm").addEventListener("submit", (event) => { event.preventDefault(); sendChat($("#chatInput").value); $("#chatInput").value = ""; });
$$(".suggestions button").forEach((button) => button.addEventListener("click", () => sendChat(button.textContent)));
$("#bibleSearch").addEventListener("input", renderLibrary);
$$("[data-library-filter]").forEach((button) => button.addEventListener("click", () => {
    libraryFilter = button.dataset.libraryFilter;
    $$("[data-library-filter]").forEach((item) => item.classList.toggle("active", item === button));
    renderLibrary();
}));
$("#uploadBibleButton").addEventListener("click", () => $("#bibleFileInput").click());
$("#bibleFileInput").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    try {
        const imported = parseBibleFile(file.name, await file.text());
        const existingKeys = new Set(uploadedBible.map((verse) => `${verse.reference}|${verse.text}`.toLowerCase()));
        const newVerses = imported.filter((verse) => !existingKeys.has(`${verse.reference}|${verse.text}`.toLowerCase()));
        uploadedBible = [...uploadedBible, ...newVerses];
        localStorage.setItem("versemate_uploaded_bible", JSON.stringify(uploadedBible));
        libraryFilter = "uploaded";
        $$("[data-library-filter]").forEach((item) => item.classList.toggle("active", item.dataset.libraryFilter === "uploaded"));
        renderLibrary();
        toast(`${newVerses.length}개 영어 구절을 추가했습니다.`);
    } catch (error) {
        toast(`업로드 실패: ${error.message}`);
    } finally {
        event.target.value = "";
    }
});
$("#downloadSample").addEventListener("click", () => {
    const sample = [
        { reference: "Matthew 6:33", text: "But seek first God's Kingdom, and his righteousness; and all these things will be given to you as well." },
        { reference: "Proverbs 3:5", text: "Trust in Yahweh with all your heart, and don't lean on your own understanding." }
    ];
    const url = URL.createObjectURL(new Blob([JSON.stringify(sample, null, 2)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "versemate-bible-sample.json";
    link.click();
    URL.revokeObjectURL(url);
});
renderLibrary();
renderVerse();
