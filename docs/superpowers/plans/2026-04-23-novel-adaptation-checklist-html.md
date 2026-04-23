# Novel Adaptation Checklist HTML Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file offline HTML workspace for the novel-to-AI-manga checklist with editable modules, dynamic repeatable sections, local image upload previews, and JSON import/export.

**Architecture:** Use one standalone `novel_manga_checklist.html` file that contains CSS, HTML scaffolding, and vanilla JavaScript state management. Store a normalized state tree in memory, render the active tab from schema-driven helpers, and persist the state to `localStorage` with import/export and print support.

**Tech Stack:** HTML, CSS, vanilla JavaScript, browser `localStorage`, FileReader API

---

### Task 1: Add the standalone HTML shell and default state

**Files:**
- Create: `novel_manga_checklist.html`
- Reference: `docs/superpowers/specs/2026-04-23-novel-adaptation-checklist-html-design.md`

- [ ] **Step 1: Add the document shell and toolbar markup**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>小说改编 AI 漫剧制作清单</title>
</head>
<body>
  <div id="app"></div>
  <input id="import-input" type="file" accept="application/json" hidden>
</body>
</html>
```

- [ ] **Step 2: Add the default state factory and module metadata**

```js
function createDefaultState() {
  return {
    projectInfo: { projectName: "", novelName: "" },
    workflow: { planning: [] },
    episodes: [],
    characters: [],
    scenes: [],
    props: [],
    storyboards: [],
    prompts: {},
    voiceLines: [],
    audio: {},
    editing: {},
    quality: {},
    folders: [],
    demoChecklist: [],
    meta: { version: 1, lastSavedAt: "" }
  };
}

const tabs = [
  { id: "projectInfo", label: "项目基础信息" },
  { id: "workflow", label: "制作流程" },
  { id: "episodes", label: "章节改编" }
];
```

- [ ] **Step 3: Add a top-level render loop and active-tab state**

```js
const STORAGE_KEY = "novel-manga-checklist-state-v1";
let state = loadInitialState();
let activeTab = "projectInfo";

function renderApp() {
  document.getElementById("app").innerHTML = `
    <div class="shell">
      ${renderToolbar()}
      ${renderOverview()}
      ${renderTabs()}
      <main>${renderActiveTab()}</main>
    </div>
  `;
}
```

- [ ] **Step 4: Run a quick file existence check**

Run: `test -f '/Users/aria.luo/Desktop/Aira Testing/AI 漫剧/novel_manga_checklist.html' && echo OK`
Expected: `OK`

### Task 2: Implement editable modules and repeatable sections

**Files:**
- Modify: `novel_manga_checklist.html`

- [ ] **Step 1: Add reusable render helpers for text, textarea, checkbox, and select fields**

```js
function renderField(label, path, value, options = {}) {
  const tag = options.type === "textarea" ? "textarea" : "input";
  return `<label class="field">
    <span>${label}</span>
    <${tag} data-path="${path}">${escapeHtml(value || "")}</${tag}>
  </label>`;
}
```

- [ ] **Step 2: Implement per-tab renderers for fixed sections**

```js
function renderProjectInfoTab() {
  return `<section class="card-grid">${[
    renderField("项目名称", "projectInfo.projectName", state.projectInfo.projectName),
    renderField("小说名称", "projectInfo.novelName", state.projectInfo.novelName)
  ].join("")}</section>`;
}
```

- [ ] **Step 3: Implement repeatable card rendering for episodes, characters, scenes, props, storyboards, voice lines, and folders**

```js
function renderRepeatableSection(sectionId, items, renderItem) {
  return `
    <section class="stack">
      <div class="section-actions">
        <button data-action="add-item" data-section="${sectionId}">新增条目</button>
      </div>
      ${items.map((item, index) => renderItem(item, index)).join("")}
    </section>
  `;
}
```

- [ ] **Step 4: Implement item actions for add, duplicate, delete, and collapse**

```js
function duplicateItem(sectionId, index) {
  const copy = structuredClone(state[sectionId][index]);
  state[sectionId].splice(index + 1, 0, copy);
  queueSave();
  renderApp();
}
```

- [ ] **Step 5: Verify the HTML contains all required module ids**

Run: `rg -n '"projectInfo"|"workflow"|"episodes"|"characters"|"scenes"|"props"|"storyboards"|"voiceLines"|"audio"|"editing"|"quality"|"folders"|"demoChecklist"' '/Users/aria.luo/Desktop/Aira Testing/AI 漫剧/novel_manga_checklist.html'`
Expected: matches for every module id used in the spec

### Task 3: Add persistence, image upload previews, and verification

**Files:**
- Modify: `novel_manga_checklist.html`

- [ ] **Step 1: Add local save/load helpers with merge-on-import**

```js
function saveState() {
  state.meta.lastSavedAt = new Date().toISOString();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadInitialState() {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved ? mergeWithDefaults(JSON.parse(saved)) : createDefaultState();
}
```

- [ ] **Step 2: Add JSON export and import handlers**

```js
function exportJson() {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  // create anchor and download
}
```

- [ ] **Step 3: Add FileReader-based image upload and preview removal**

```js
async function appendImages(sectionId, index, files) {
  const images = await Promise.all([...files].map(readFileAsDataUrl));
  state[sectionId][index].images.push(...images);
  queueSave();
  renderApp();
}
```

- [ ] **Step 4: Add print styles and an autosave status indicator**

```css
@media print {
  .toolbar, .tabs, .upload-row, button { display: none !important; }
  body { background: #fff; }
}
```

- [ ] **Step 5: Run a lightweight syntax and feature smoke check**

Run: `python3 - <<'PY'\nfrom pathlib import Path\ntext = Path('/Users/aria.luo/Desktop/Aira Testing/AI 漫剧/novel_manga_checklist.html').read_text()\nchecks = ['createDefaultState', 'localStorage', 'FileReader', 'renderApp', 'print()', '导出 JSON']\nmissing = [item for item in checks if item not in text]\nassert not missing, missing\nprint('HTML_SMOKE_OK')\nPY`
Expected: `HTML_SMOKE_OK`

- [ ] **Step 6: Run Git diff review**

Run: `git diff -- '/Users/aria.luo/Desktop/Aira Testing/AI 漫剧/novel_manga_checklist.html'`
Expected: one new standalone HTML file with embedded CSS and JavaScript
