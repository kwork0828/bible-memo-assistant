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
    { id: "web-isa-41-10", reference: "Isaiah 41:10", text: "Don't you be afraid, for I am with you. Don't be dismayed, for I am your God.", source: "WEB", uploaded: false },
    { id: "web-gen-39-9", reference: "Genesis 39:9", text: "How then can I do this great wickedness, and sin against God?", source: "WEB", uploaded: false },
    { id: "web-gen-39-10", reference: "Genesis 39:10", text: "As she spoke to Joseph day by day, he didn't listen to her, to lie by her, or to be with her.", source: "WEB", uploaded: false },
    { id: "web-gen-39-12", reference: "Genesis 39:12", text: "He left his garment in her hand, and ran outside.", source: "WEB", uploaded: false },
    { id: "web-psa-16-8", reference: "Psalm 16:8", text: "I have set Yahweh always before me. Because he is at my right hand, I shall not be moved.", source: "WEB", uploaded: false }
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
let selectedJournalEntry = null;
let selectedShareFormat = "blog";
let presenceTimerId = null;
let quizActive = false;
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const date = new Intl.DateTimeFormat("ko-KR", { month: "long", day: "numeric", weekday: "long" }).format(new Date());
$("#todayDate").textContent = date;

function showView(name) {
    $$(".view").forEach((view) => view.classList.toggle("active-view", view.id === name));
    $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === name));
    const titles = { home: "오늘도 말씀 한 구절", schedule: "복습 흐름을 한눈에", library: "나만의 영어성경 보관함", bod: "말씀을 삶으로 잇는 루틴", coach: "내 진도를 아는 AI 코치", records: "쌓여가는 암송과 묵상 기록" };
    $("#pageTitle").textContent = titles[name];
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderVerse() {
    const verse = verses[currentVerse];
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    $("#verseRef").textContent = verse.ref;
    $("#verseStage").textContent = verse.stage;
    $("#verseText").textContent = `“${verse.text}”`;
    $("#verseTranslation").textContent = verse.ko;
    $("#verseNumber").textContent = currentVerse + 1;
    $("#verseTotal").textContent = verses.length;
    $("#recallInput").value = "";
    $("#recallFeedback").textContent = "";
    $("#recallReviewText").textContent = "";
    $("#recallReview").hidden = true;
    quizActive = false;
    $("#quizMode").textContent = "QUIZ 모드";
    $("#verseText").hidden = false;
    $("#quizText").hidden = true;
    $("#toggleVerse").textContent = "본문 가리기";
    $("#speechStatus").textContent = "재생 대기";
    $("#playVerse").textContent = "▶ 영어 듣기";
    renderSpeechCaption(false);
    renderQuizText();
}

function renderQuizText() {
    const quizText = $("#quizText");
    quizText.replaceChildren();
    verses[currentVerse].text.split(/(\s+)/).forEach((token, index) => {
        if (/\s+/.test(token)) {
            quizText.appendChild(document.createTextNode(token));
            return;
        }
        const word = document.createElement("span");
        const shouldBlank = token.replace(/[^A-Za-z]/g, "").length > 3 && index % 4 === 0;
        word.className = shouldBlank ? "quiz-blank" : "quiz-word";
        word.textContent = shouldBlank ? "????" : token;
        word.setAttribute("aria-label", shouldBlank ? "빈칸" : token);
        quizText.appendChild(word);
    });
}

function renderSpeechCaption(isSpeaking) {
    const caption = $("#speechCaption");
    const shouldShow = $("#captionToggle").checked && isSpeaking;
    caption.textContent = shouldShow ? verses[currentVerse].text : "";
    caption.classList.toggle("visible", shouldShow);
    caption.classList.toggle("speaking", shouldShow);
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
        item.tabIndex = 0;
        item.setAttribute("role", "button");
        item.setAttribute("aria-label", `${verse.reference} 본문을 오늘 학습으로 선택`);
        item.title = "카드 아무 곳이나 눌러 오늘 학습으로 가져오기";
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
        const clickHint = document.createElement("span");
        clickHint.className = "click-hint";
        clickHint.textContent = "카드 클릭 → 오늘 학습";
        meta.append(source, words, clickHint);
        content.append(heading, text, meta);

        const favorite = document.createElement("button");
        const isFavorite = favoriteIds.has(verse.id);
        favorite.className = `favorite-button${isFavorite ? " active" : ""}`;
        favorite.textContent = isFavorite ? "★" : "☆";
        favorite.setAttribute("aria-label", `${verse.reference} ${isFavorite ? "즐겨찾기 해제" : "즐겨찾기 추가"}`);
        favorite.addEventListener("click", (event) => {
            event.stopPropagation();
            toggleFavorite(verse.id);
        });
        item.addEventListener("click", () => selectLibraryVerse(verse));
        item.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                selectLibraryVerse(verse);
            }
        });
        item.append(content, favorite);
        $("#bibleList").appendChild(item);
    });
}

function selectLibraryVerse(libraryVerse) {
    let verseIndex = verses.findIndex((verse) => verse.ref === libraryVerse.reference);
    if (verseIndex < 0) {
        verses.push({
            ref: libraryVerse.reference,
            stage: "D+0 신규",
            text: libraryVerse.text,
            ko: "선택한 World English Bible 영어 본문입니다."
        });
        verseIndex = verses.length - 1;
    }
    currentVerse = verseIndex;
    renderVerse();
    showView("home");
    toast(`${libraryVerse.reference}을 오늘 학습으로 가져왔습니다.`);
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
    if (quizActive) {
        quizActive = false;
        $("#quizText").hidden = true;
        $("#verseText").hidden = false;
        $("#verseTranslation").classList.remove("hidden");
        $("#quizMode").textContent = "QUIZ 모드";
    }
    const hidden = $("#verseText").classList.toggle("hidden");
    $("#verseTranslation").classList.toggle("hidden", hidden);
    event.target.textContent = hidden ? "본문 보기" : "본문 가리기";
});
$("#quizMode").addEventListener("click", () => {
    quizActive = !quizActive;
    if (quizActive) {
        renderQuizText();
        $("#verseText").hidden = true;
        $("#verseTranslation").classList.add("hidden");
        $("#quizText").hidden = false;
        $("#toggleVerse").textContent = "본문 보기";
        $("#quizMode").textContent = "QUIZ 종료";
    } else {
        $("#verseText").hidden = false;
        $("#verseTranslation").classList.remove("hidden");
        $("#quizText").hidden = true;
        $("#toggleVerse").textContent = "본문 가리기";
        $("#quizMode").textContent = "QUIZ 모드";
    }
});
$("#playVerse").addEventListener("click", () => {
    if (!("speechSynthesis" in window)) {
        $("#speechStatus").textContent = "이 브라우저는 음성 재생을 지원하지 않습니다.";
        return;
    }
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        $("#speechStatus").textContent = "재생 중지";
        $("#playVerse").textContent = "▶ 영어 듣기";
        renderSpeechCaption(false);
        return;
    }

    const utterance = new SpeechSynthesisUtterance(verses[currentVerse].text);
    utterance.lang = "en-US";
    utterance.rate = Number($("#speechRate").value);
    utterance.onstart = () => {
        $("#speechStatus").textContent = `${utterance.rate}× 재생 중`;
        $("#playVerse").textContent = "■ 듣기 중지";
        renderSpeechCaption(true);
    };
    utterance.onend = () => {
        $("#speechStatus").textContent = "재생 완료";
        $("#playVerse").textContent = "▶ 다시 듣기";
        renderSpeechCaption(false);
    };
    utterance.onerror = () => {
        $("#speechStatus").textContent = "음성 재생 실패";
        $("#playVerse").textContent = "▶ 다시 듣기";
        renderSpeechCaption(false);
    };
    window.speechSynthesis.speak(utterance);
});
$("#captionToggle").addEventListener("change", () => {
    renderSpeechCaption("speechSynthesis" in window && window.speechSynthesis.speaking);
});
$("#checkRecall").addEventListener("click", () => {
    const typed = $("#recallInput").value.toLowerCase().replace(/[^a-z ]/g, "").trim();
    const answer = verses[currentVerse].text.toLowerCase().replace(/[^a-z ]/g, "").trim();
    if (!typed) { $("#recallFeedback").textContent = "먼저 기억나는 문장을 적어보세요."; return; }
    const typedWords = new Set(typed.split(/\s+/));
    const answerWords = answer.split(/\s+/);
    const score = Math.round(answerWords.filter((word) => typedWords.has(word)).length / answerWords.length * 100);
    $("#recallFeedback").textContent = `핵심 단어 일치율 ${score}% · 본문과 비교해 보세요.`;
    $("#recallReviewText").textContent = $("#recallInput").value;
    $("#recallReview").hidden = false;
});
$("#editRecall").addEventListener("click", () => {
    $("#recallInput").focus();
    $("#recallFeedback").textContent = "답을 수정한 뒤 다시 ‘답 확인’을 눌러보세요.";
});
const reflectionDialog = $("#reflectionDialog");
$("#completeVerse").addEventListener("click", () => {
    completed = Math.min(4, completed + 1);
    $("#heroPercent").textContent = `${completed * 25}%`;
    toast("오늘의 암송 기록에 저장했습니다.");
    reflectionDialog.showModal();
});

$("#reflectionForm").addEventListener("submit", (event) => {
    if (event.submitter?.value !== "default") return;
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget).entries());
    const reflections = readStoredArray("versemate_reflections");
    reflections.push({ id: `reflection-${Date.now()}`, type: "reflection", date: new Date().toISOString(), reference: verses[currentVerse].ref, ...values });
    localStorage.setItem("versemate_reflections", JSON.stringify(reflections.slice(-90)));
    event.currentTarget.reset();
    reflectionDialog.close();
    renderJournal();
    toast("한 줄 평을 기록했습니다. 자세한 적용은 말씀 루틴에서 이어가세요.");
});

const bodForm = $("#bodForm");
$("#fillJosephPlan").addEventListener("click", () => {
    bodForm.elements.reference.value = "Genesis 39:9–12";
    bodForm.elements.god_reflection.value = "사람이 보지 않는 자리에서도 나와 함께하시며, 정직한 선택을 기뻐하시는 하나님";
    bodForm.elements.heart_check.value = "사람의 평가를 의식해 맡은 일을 대충하거나 불의와 타협하려는 마음";
    bodForm.elements.today_action.value = "오후 보고서를 제출하기 전 수치와 출처를 한 번 더 확인한다.";
    bodForm.elements.action_time.value = "14:00";
    bodForm.elements.action_place.value = "회사 자리";
    bodForm.elements.integrity_boundary.value = "불리해도 숫자와 진행 상태를 사실과 다르게 말하지 않는다.";
    bodForm.elements.temptation_trigger.value = "급하게 결과를 요구받아 편법을 쓰고 싶어질 때";
    bodForm.elements.escape_action.value = "답변을 바로 보내지 않고 자리에서 일어나 1분간 멈춘다.";
    bodForm.elements.support_action.value = "믿을 만한 동료에게 사실 기준을 확인하고 정직하게 보고한다.";
    toast("요셉 적용 예시를 채웠습니다. 내 상황에 맞게 바꿔보세요.");
});

bodForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!bodForm.checkValidity()) {
        bodForm.reportValidity();
        return;
    }
    const plan = Object.fromEntries(new FormData(bodForm).entries());
    const plans = readStoredArray("versemate_bod_plans");
    plans.push({
        id: `bod-${Date.now()}`,
        type: "bod",
        date: new Date().toISOString(),
        status: "planned",
        ...plan
    });
    localStorage.setItem("versemate_bod_plans", JSON.stringify(plans.slice(-90)));
    renderJournal();
    showView("records");
    toast("오늘의 적용 계획을 이 브라우저에 임시 저장했습니다.");
});

$("#startPresencePause").addEventListener("click", () => {
    if (presenceTimerId) {
        clearInterval(presenceTimerId);
        presenceTimerId = null;
    }
    let seconds = 60;
    $("#pauseTimer").textContent = "01:00";
    $("#startPresencePause").textContent = "하나님 앞에서 잠시 멈춥니다";
    presenceTimerId = setInterval(() => {
        seconds -= 1;
        $("#pauseTimer").textContent = `00:${String(seconds).padStart(2, "0")}`;
        if (seconds <= 0) {
            clearInterval(presenceTimerId);
            presenceTimerId = null;
            $("#pauseTimer").textContent = "완료";
            $("#startPresencePause").textContent = "1분 임재 멈춤 다시 시작";
            toast("1분 멈춤을 마쳤습니다. 오늘의 한 행동을 적어보세요.");
        }
    }, 1000);
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

function getJournalEntries() {
    const reflections = readStoredArray("versemate_reflections").map((entry, index) => ({
        id: entry.id || `legacy-reflection-${index}`,
        type: "reflection",
        ...entry
    }));
    const plans = readStoredArray("versemate_bod_plans");
    const entries = [...reflections, ...plans].sort((a, b) => new Date(b.date) - new Date(a.date));
    if (entries.length) return entries;
    return [{
        id: "demo-joseph-plan",
        type: "bod",
        demo: true,
        date: new Date().toISOString(),
        reference: "Genesis 39:9–12",
        god_reflection: "보이지 않는 자리에서도 함께하시며 정직한 선택을 기뻐하시는 하나님",
        heart_check: "사람의 평가 때문에 사실을 흐리려는 마음을 경계한다.",
        today_action: "오후 보고서를 보내기 전 수치와 출처를 한 번 더 확인한다.",
        integrity_boundary: "불리해도 진행 상태를 사실과 다르게 말하지 않는다.",
        escape_action: "급한 압박이 오면 즉답하지 않고 자리에서 일어나 1분간 멈춘다.",
        status: "planned"
    }];
}

function journalEntryText(entry) {
    return [
        entry.reference,
        entry.quick_note,
        entry.feeling,
        entry.god_reflection,
        entry.heart_check,
        entry.today_application,
        entry.today_action,
        entry.yesterday_application,
        entry.integrity_boundary,
        entry.escape_action
    ].filter(Boolean).join(" ");
}

function addJournalField(container, label, value) {
    if (!value) return;
    const row = document.createElement("div");
    const title = document.createElement("b");
    const text = document.createElement("p");
    title.textContent = label;
    text.textContent = value;
    row.append(title, text);
    container.appendChild(row);
}

function renderJournal() {
    const list = $("#journalList");
    const query = $("#journalSearch").value.trim().toLowerCase();
    const entries = getJournalEntries().filter((entry) => journalEntryText(entry).toLowerCase().includes(query));
    list.replaceChildren();
    $("#journalEmpty").hidden = entries.length > 0;

    entries.forEach((entry) => {
        const card = document.createElement("article");
        card.className = "journal-card";

        const head = document.createElement("div");
        head.className = "journal-card-head";
        const titleWrap = document.createElement("div");
        const meta = document.createElement("span");
        meta.className = "journal-meta";
        meta.textContent = `${new Date(entry.date).toLocaleDateString("ko-KR")} · ${entry.type === "bod" ? "말씀 루틴" : "짧은 묵상"}`;
        const title = document.createElement("h3");
        title.textContent = entry.reference || "말씀 묵상";
        titleWrap.append(meta, title);
        const state = document.createElement("span");
        state.className = `practice-state ${entry.status === "done" ? "done" : "planned"}`;
        state.textContent = entry.demo ? "예시 기록" : entry.status === "done" ? "실행 완료" : entry.type === "bod" ? "실행 예정" : "묵상 저장";
        head.append(titleWrap, state);

        const body = document.createElement("div");
        body.className = "journal-body";
        addJournalField(body, "오늘의 한 줄 평", entry.quick_note || entry.feeling);
        addJournalField(body, "하나님에 대한 묵상", entry.god_reflection);
        addJournalField(body, "마음 점검", entry.heart_check);
        addJournalField(body, "오늘의 한 행동", entry.today_action || entry.today_application);
        addJournalField(body, "타협하지 않을 기준", entry.integrity_boundary);
        addJournalField(body, "유혹에서 떠날 행동", entry.escape_action);
        addJournalField(body, "어제의 적용", entry.yesterday_application);

        const actions = document.createElement("div");
        actions.className = "journal-actions";
        if (entry.type === "bod" && !entry.demo) {
            const done = document.createElement("button");
            done.className = "secondary-button";
            done.type = "button";
            done.textContent = entry.status === "done" ? "실행 예정으로 되돌리기" : "오늘 실행 완료";
            done.addEventListener("click", () => togglePlanStatus(entry.id));
            actions.appendChild(done);
        }
        const share = document.createElement("button");
        share.className = "ghost-button";
        share.type = "button";
        share.textContent = "나눔 글 초안 만들기";
        share.addEventListener("click", () => openShareDraft(entry));
        actions.appendChild(share);

        card.append(head, body, actions);
        list.appendChild(card);
    });
}

function togglePlanStatus(entryId) {
    const plans = readStoredArray("versemate_bod_plans");
    const target = plans.find((plan) => plan.id === entryId);
    if (!target) return;
    target.status = target.status === "done" ? "planned" : "done";
    localStorage.setItem("versemate_bod_plans", JSON.stringify(plans));
    renderJournal();
    toast(target.status === "done" ? "오늘의 적용을 실행 완료로 표시했습니다." : "실행 예정으로 되돌렸습니다.");
}

function buildShareDraft(entry, format) {
    const reference = entry.reference || "오늘의 말씀";
    const reflection = entry.god_reflection || entry.quick_note || entry.feeling || "말씀을 천천히 마음에 새겼습니다.";
    const action = entry.today_action || entry.today_application || "오늘의 자리에서 작은 순종을 실천해 보려 합니다.";
    if (format === "threads") {
        return `${reference} 묵상\n\n오늘 말씀을 통해 ${reflection}\n\n그래서 오늘은 이렇게 적용해 봅니다.\n→ ${action}\n\n기록에서 실행으로, 작은 순종을 이어갑니다.\n\n#영어성경암송 #말씀묵상 #오늘의적용`;
    }
    if (format === "short") {
        return `${reference}\n${reflection}\n오늘의 한 행동: ${action}\n#말씀묵상 #삶의적용`;
    }
    return `[오늘의 말씀] ${reference}\n\n오늘 마음에 남은 것\n${reflection}\n\n삶에 적용할 한 가지\n${action}\n\n말씀을 읽고 좋은 생각을 남기는 데서 멈추지 않고, 오늘의 구체적인 행동으로 이어가 보려 합니다. 하루가 끝난 뒤 실제로 어떻게 적용했는지도 다시 돌아보겠습니다.`;
}

function refreshShareDraft() {
    if (!selectedJournalEntry) return;
    $("#shareDraft").value = buildShareDraft(selectedJournalEntry, selectedShareFormat);
}

function openShareDraft(entry) {
    selectedJournalEntry = entry;
    selectedShareFormat = "blog";
    $$("[data-share-format]").forEach((button) => button.classList.toggle("active", button.dataset.shareFormat === "blog"));
    $("#privacyChecked").checked = false;
    $("#copyShareDraft").disabled = true;
    refreshShareDraft();
    $("#shareDialog").showModal();
}

$$('[data-share-format]').forEach((button) => button.addEventListener("click", () => {
    selectedShareFormat = button.dataset.shareFormat;
    $$('[data-share-format]').forEach((item) => item.classList.toggle("active", item === button));
    refreshShareDraft();
}));
$("#privacyChecked").addEventListener("change", (event) => {
    $("#copyShareDraft").disabled = !event.target.checked;
});
$("#copyShareDraft").addEventListener("click", async () => {
    if (!$("#privacyChecked").checked) return;
    try {
        await navigator.clipboard.writeText($("#shareDraft").value);
        toast("검토한 나눔 글 초안을 복사했습니다. 자동 게시되지는 않습니다.");
    } catch {
        $("#shareDraft").select();
        toast("자동 복사가 막혔습니다. 선택된 글을 Ctrl+C로 복사하세요.");
    }
});
$("#journalSearch").addEventListener("input", renderJournal);

function renderHeatmap() {
    const heatmap = $("#heatmap");
    if (!heatmap) return;
    const activeDays = new Set([1, 3, 5, 8, 10, 12, 15, 17, 18, 21, 24, 26, 29, 31, 34, 37, 39, 42, 45, 48, 50, 53, 56, 58, 61, 64, 67, 69, 72, 76, 78, 81, 82, 83]);
    const today = new Date();
    for (let index = 0; index < 84; index += 1) {
        const cell = document.createElement("span");
        const level = activeDays.has(index) ? ((index % 4) + 1) : 0;
        const date = new Date(today);
        date.setDate(today.getDate() - (83 - index));
        cell.className = `heatmap-cell level-${level}`;
        cell.title = `${date.toLocaleDateString("ko-KR")} · ${level ? level * 10 + 5 : 0}분 학습`;
        heatmap.appendChild(cell);
    }
}

renderHeatmap();
renderLibrary();
renderVerse();
renderJournal();
