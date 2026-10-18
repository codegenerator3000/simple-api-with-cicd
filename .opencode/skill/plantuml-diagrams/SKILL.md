---
name: plantuml-diagrams
description: Use when creating, editing, or rendering PlantUML diagrams in this repo (ER, sequence, use-case, etc.), or when asked to add or regenerate diagrams under doc/diagrams.
---

# PlantUML Diagrams (t_py_fapi)

## Layout

- **Sources:** `doc/diagrams/src/*.puml` — one diagram per file.
- **Rendered SVGs:** `doc/diagrams/*.svg`, named after the file.
- Never hand-edit the SVGs; edit the source and re-render.

## Render

```bash
plantuml -tsvg -o .. doc/diagrams/src/<name>.puml
```

`-o` is relative to the **source file's** directory, hence `..`. Quick visual
check: render `-tpng` to `/tmp/opencode` and view it.

Requires PlantUML ≥ 1.2026.

## Required style block

Every diagram starts with this (theme = spacelab, white background, padding):

```plantuml
@startuml <name>
!theme spacelab
skinparam BackgroundColor white
skinparam padding 8
```

## Conventions

- Name the diagram: `@startuml <name>` (matches the SVG filename).
- **Entity blocks must be multi-line.** Single-line `entity A { * id }` fails
  to parse; put each field on its own line.
- ER diagrams: `*` marks PKs, `<<PK>>`/`<<FK>>` stereotypes, `--` separates
  the PK block from other columns, `||--o{` for one-to-many relations.
- After rendering, sanity-check the SVG actually changed (e.g. `diff`
  themed vs. unthemed) if the output looks suspiciously stale.
