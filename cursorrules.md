# PROJECT MEMORY RULES FOR CURSOR

# 1. MEMORY BANK — `.cursor_memory.md`
- Maintain a single file named `.cursor_memory.md` at the project root.
- This file must include:
  - Project purpose (1 paragraph).
  - Key components and their roles.
  - High-level file/folder structure (tree view).
  - Active tasks (bullet list, update weekly).
  - Known issues and pending questions.
- ⚠️ Update this file:
  - When project scope or purpose changes
  - When major components are added/removed
  - When task list or known issues change

# 2. CHANGELOG — `CHANGELOG.md`
- All significant code or structural changes must be logged in `CHANGELOG.md`.
- Each entry must include:
  - Date (YYYY-MM-DD)
  - Summary of change
  - Files or components affected
  - Reason for change
- ⚠️ Update this file:
  - Immediately after implementing non-trivial changes to logic, structure, or components

# 3. FILE HEADER COMMENTS
- Every new or edited file must include a header with:
  - Author (if collaborative)
  - Last updated (date)
  - Purpose of file
  - Dependencies (internal/external)
- ⚠️ Update header:
  - Any time the file is modified in a meaningful way
  - Automatically update `Last updated` with current date

# 4. CURRENT FOCUS — `.cursor_focus.md`
- Track the current feature or bugfix in `.cursor_focus.md`.
- Include:
  - Goal
  - Files involved
  - Progress notes
  - Next steps
- ⚠️ Update this file:
  - At the beginning and end of each work session
  - When shifting to a new feature, task, or investigation

# 5. SCRATCHPAD — `.cursor_scratch.md`
- Maintain a `.cursor_scratch.md` file for:
  - Experiments tried
  - Abandoned ideas (with reasons)
  - Questions or blockers
- ⚠️ Update this file:
  - After any experiment, idea, or failed attempt
  - When encountering technical or conceptual blockers

# 6. STRUCTURE SNAPSHOT — `STRUCTURE.md`
- Maintain a file called `STRUCTURE.md` with:
  - A tree view of the full directory structure
  - Description for each major folder and file
- ⚠️ Update this file:
  - After adding, renaming, moving, or deleting major files/folders
  - At the end of each day when structural edits were made

# 7. CURSOR MEMORY SYNC
- On opening the project or prompting Cursor:
  - Always load `.cursor_memory.md`, `CHANGELOG.md`, and `.cursor_focus.md`
  - Use them to maintain context for code generation, planning, or debugging
- ⚠️ Ensure these files are actively referenced during all assistance or output

# 8. GENERAL
- All memory and tracking files must be in Markdown
- Use consistent headings and date format (YYYY-MM-DD)
- Do not delete past memory—append only unless correcting for clarity
- ⚠️ Commit changes to memory and tracking files alongside code commits where relevant
