# ScribeOne — TODO (Iteration Plan)

> Source of truth: `specs/specifications.md` and `specs/project_status.md`

## Milestone M0 — Project skeleton
- [x] Create modern Python project scaffold with `pyproject.toml` (PEP 621) and `src/` layout
- [x] Add entry points: `src/scribeone/main.py`, `src/scribeone/app.py`
- [x] Add core models and APIs per contract: `core/document.py`, `core/fileio.py`
- [x] Add UI shells: `ui/main_window.py`, `ui/dialogs.py`
- [x] Add minimal QSS themes: `theme/dark.qss`, `theme/light.qss`
- [x] Wire title/status format and dirty flag basics

## Milestone M1 — Core interactions and data flow
- [x] FR-002 Open file with encoding retry (default UTF-8)
- [ ] FR-003 Save (Ctrl+S); first save falls back to Save As
- [ ] FR-004 Save As (Ctrl+Shift+S) and title/status update
- [x] FR-005 Unsaved-close guard: modal dialog Save/Discard/Cancel
- [ ] FR-006 Status bar shows path and dirty indicator ●/○ (basic done, refine messages)
- [x] FR-008 Editing shortcuts (undo/redo/cut/copy/paste/select all)
- [x] Optional FR-007 Recent files (top 5)
- [x] Optional FR-009 Toggle word wrap persisted in app settings

## Milestone M2 — Modern UX and polish
- [x] Provide light/dark themes (QSS) and runtime toggle
- [ ] Animations ANM-001..005 (opt-out for low perf)
- [x] Snackbar for transient messages (e.g., saved)
- [x] About dialog (F1)

## Milestone M3 — Stability and tests
- [ ] tests/test_close_guard.py covering save/discard/cancel branches
- [ ] tests/test_fileio.py covering encoding/permission errors
- [ ] Ruff + mypy configuration and CI hooks

## Nice-to-haves and unique ideas
- [ ] Distraction-free mode (Ctrl+K Z) to hide chrome
- [ ] Smart encoding detector fallback (charset-normalizer)
- [ ] Built-in command palette for actions (Ctrl+Shift+P)
- [ ] Auto-backup temp snapshots on dirty edits (crash-safe)

---

Next iteration (target):
- Wire unified messages from `src/scribeone/ui/messages.py` for ERR/MSG/WARN per specs.
- Add overwrite confirmation on Save As when path exists.
- Add recent files cleanup entry and max count setting.
- Tests: implement `tests/test_close_guard.py` branches and `tests/test_fileio.py` error cases.

---

Notes:
- Keep OOP design; Document is the single source of truth for path/text/dirty.
- Follow button/action IDs and naming from specs (BTN-001..013; ANM-001..005).
- Prefer explicit, minimal dependencies; add only when clearly valuable.
