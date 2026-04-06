# Phase 8 Context

## User Goal

Replace flat retrieval with hierarchical role/story/evidence retrieval and budget-aware context assembly that can scale as the career vault grows.

## Constraints

- Preserve the one-page output target while changing how evidence is selected.
- Expose omission and compression decisions as inspectable artifacts.

## Source Findings

- Current retrieval is mostly lexical whole-role ranking plus hard caps.
- The current blueprint builder uses fixed limits rather than explicit evidence budgets.
