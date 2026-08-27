<!-- pyml disable MD041 -->
<!-- pyml disable MD022 -->
<!-- pyml disable MD003 -->
<!-- pyml disable MD023 -->
<!-- pyml disable MD026 -->
---
name: write-markdown
description: >
  Use when writing or rewriting Markdown docs and small snippets with clear
  structure and consistent formatting.
---
<!-- pyml enable MD022 -->
<!-- pyml enable MD041 -->
<!-- pyml enable MD023 -->
<!-- pyml enable MD026 -->

# Write Markdown

## Purpose

Use this skill to produce high-quality Markdown that is easy to scan, accurate, and consistent.
Prioritize reader intent, clear structure, and minimal noise.

## Scope

This skill applies to both:

* Small snippets (one paragraph, one list, short examples, brief sections).
* Full documents (README files, design notes, guides, changelogs).

Only use full-document structure when the task is document-sized.

## PyMarkdown First

Apply PyMarkdown compliance rules, and run checks when substantial Markdown has
been generated.
If a `pyproject.toml` file exists in the workspace, adhere to the
PyMarkdown exceptions/configuration settings in there.
If no `pyproject.toml` exists, follow the rules in this skill as defaults.

## Non-Negotiable Rules

Apply these defaults up front:

* Use ATX headings (`#`, `##`, `###`) consistently.
* Use asterisks (`*`) for bullet lists.
* Do not use bold text as a pseudo-heading.
* Keep lines at or below 100 characters.
* Use spaces only, never hard tabs.
* Add blank lines around headings and lists.

## Markdown Standards

* Keep section titles short and descriptive.
* Prefer flat bullet lists; avoid deep nesting.
* Use fenced code blocks with language tags when relevant.
* Use backticks for commands, paths, symbols, and config keys.
* Keep lines readable and avoid long, dense paragraphs.
* Use bold/italic text sparsely.

## Frontmatter Pattern

For frontmatter-based files, use this pattern when needed:

```markdown
<!-- pyml disable MD041 -->
<!-- pyml disable MD022 -->
<!-- pyml disable MD003 -->
<!-- pyml disable MD023 -->
<!-- pyml disable MD026 -->
---
name: ...
description: "..."
---
<!-- pyml enable MD022 -->
<!-- pyml enable MD041 -->
<!-- pyml enable MD023 -->
<!-- pyml enable MD026 -->
```

Keep `MD003` disabled for frontmatter-based skill files when repository heading
style expectations conflict with required ATX headings.

## Validation Policy

* Quick decision: small edits skip lint, substantial generated text runs lint.
* Treat text as substantial when any of these are true: more than two new
  sections, more than 150 new words, or a rewrite of an existing section.
* Prefer `pymarkdown scan <markdown-files>`.
* If unavailable, use `pre-commit run pymarkdown --files <markdown-files>`.

## Output Size Examples

* Snippet example: one short paragraph plus one bullet list.
* Document example: title, short context, three sections, and optional example.

## Inputs To Gather

Before writing, collect (as relevant):

* Audience: who will read this (users, maintainers, contributors).
* Goal: what the reader should understand or do.
* Scope: what to include and what to exclude.
* Constraints: style rules, required sections, and file location.

If details are missing, **ask** concise clarifying questions first.

## Writing Workflow (larger texts)

1. For snippet-sized output, prefer the smallest useful Markdown block.
2. Define a simple outline with short section titles.
3. Write a direct first draft with short paragraphs and concrete wording.
4. Add examples only where they remove ambiguity.
5. Check for consistency in tone, tense, and terminology.
6. Tighten language by removing filler and repeated ideas.

## Quality Checklist

* The document matches the intended audience and goal.
* The first section explains purpose and outcome.
* Steps are ordered and executable.
* Terminology matches the codebase and existing docs.
* Examples are correct and minimal.
* No contradictory instructions or missing prerequisites.

## Boundaries

* Do not invent APIs, commands, or behavior.
* Mark assumptions clearly when facts are missing.
* Preserve existing project conventions when editing existing docs.
