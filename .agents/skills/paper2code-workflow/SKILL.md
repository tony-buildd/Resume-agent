---
name: paper2code-workflow
description: Use the Paper2Code / PaperCoder workflow to turn a research paper into an implementation plan or generated repository through planning, analysis, and coding stages.
---

# Paper2Code Workflow

Use this skill when the user wants to transform a research paper into code, implementation plans, or a generated repository using the Paper2Code methodology.

## Source

- Upstream repository: `going-doer/paper2code`
- Core workflow: planning -> analysis -> code generation
- Example assets include Transformer paper inputs and generated repository evaluation

## Best Uses

- Turning a paper into an implementation roadmap
- Extracting architecture and algorithm requirements before coding
- Comparing a generated implementation against an official repository
- Running paper-to-code experiments with OpenAI or vLLM backends

## Operating Guidance

- Start by deciding whether the goal is:
  - implementation planning only
  - full code generation
  - evaluation of an existing generated repo
- Prefer breaking the work into the same stages as the upstream system:
  1. planning
  2. analyzing
  3. coding
  4. optional evaluation

## Local Notes

- Upstream examples use `pip`, but for local work in this repo prefer `uv` environments.
- If the user wants direct upstream execution, make the environment explicit before running anything expensive.
- Treat generated code as a draft that still needs repository-specific review and verification.

## Upstream Script Surface

Representative upstream commands:

```bash
bash scripts/run.sh
bash scripts/run_latex.sh
bash scripts/run_llm.sh
bash scripts/run_latex_llm.sh
```

## Practical Codex Workflow

1. Read the paper or paper summary.
2. Produce a structured implementation plan.
3. Identify missing configuration, datasets, or architecture details.
4. Generate or adapt code in phases.
5. Evaluate faithfulness and repository quality before calling the work done.

## Guardrails

- Do not pretend paper details are certain when they are underspecified.
- Separate what the paper states from what you infer for implementation.
- Prefer a faithful baseline before making improvements or optimizations.
