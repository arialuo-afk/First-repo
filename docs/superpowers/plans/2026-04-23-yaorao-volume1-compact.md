# Yaorao Volume 1 Compact Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the folder-template tab, make the checklist workspace denser and easier to scan, and replace the sample content with a first-volume grouped classification for 《妖娆召唤师》.

**Architecture:** Keep the existing single-file `novel_manga_checklist.html` structure intact, but trim tab metadata, tighten the CSS layout, and expand the seeded template builder from a 3-chapter sample to a 6-arc first-volume sample. Preserve the same state shape where possible so import/export stays compatible.

**Tech Stack:** HTML, CSS, vanilla JavaScript, browser localStorage

---

### Task 1: Update structure and compact styling

**Files:**
- Modify: `novel_manga_checklist.html`
- Reference: `docs/superpowers/specs/2026-04-23-yaorao-volume1-compact-design.md`

- [ ] Remove the `folders` tab metadata and its collection factory entry.
- [ ] Remove the `renderFoldersTab()` branch from the active-tab switch.
- [ ] Tighten the page spacing in the CSS for `.page`, `.hero`, `.overview`, `.panel`, `.card`, `.repeatable-card`, `.form-grid`, `.mini-row`, and `.check-grid`.
- [ ] Keep responsive behavior intact after spacing changes.

### Task 2: Replace the sample data with first-volume grouping

**Files:**
- Modify: `novel_manga_checklist.html`

- [ ] Rename the seeded sample copy from “前 3 章” to “第一卷”.
- [ ] Replace the current 3-episode seeded content with 6 grouped first-volume arcs.
- [ ] Expand characters, scenes, props, prompts, voice lines, music cues, and storyboard examples to cover the first-volume storyline.
- [ ] Mark most seeded repeatable items as collapsed to improve scanability.

### Task 3: Verify and publish

**Files:**
- Modify: `novel_manga_checklist.html`
- Modify: `novel_manga_checklist_zhuque_demo.html`

- [ ] Copy the updated main HTML into the demo HTML so both entry points stay consistent.
- [ ] Run text smoke checks for the first-volume title and key arc labels.
- [ ] Run JavaScript syntax verification and a runtime seed check.
- [ ] Commit and push once verification passes.
