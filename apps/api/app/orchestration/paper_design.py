from __future__ import annotations

from app.orchestration.contracts import PaperDesignBriefRecord, PaperDesignInputRecord


def build_paper_design_brief(
    paper: PaperDesignInputRecord,
) -> PaperDesignBriefRecord:
    title = paper.paper_title
    findings = paper.key_findings
    abstract = paper.abstract.strip()

    stated_claims = findings[:5] if findings else [abstract]
    inferred_decisions = [
        "Implement a faithful baseline first and separate any repository-specific optimizations.",
        "Model each claimed subsystem as an explicit module boundary before coding.",
        "Capture underspecified paper details as open questions instead of inventing certainty.",
    ]
    analysis_questions = [
        "Which parts of the paper are directly specified versus left to implementation choice?",
        "What data flow or orchestration boundaries are required to reproduce the paper faithfully?",
        "Which evaluation checks prove fidelity before optimization begins?",
    ]
    coding_phases = [
        "Planning: extract the architecture, interfaces, and constraints from the paper.",
        "Analysis: map missing implementation details and isolate inference versus stated claims.",
        "Coding: implement the baseline modules in dependency order.",
        "Evaluation: verify fidelity against the paper's reported behaviors or success checks.",
    ]
    evaluation_checks = [
        "Confirm each core paper claim maps to an implemented module or explicit TODO.",
        "Document every inferred design decision separately from the paper's stated content.",
        "Run a fidelity review before layering repo-specific improvements.",
    ]

    return PaperDesignBriefRecord(
        paperTitle=title,
        implementationGoal=paper.implementation_goal,
        planningSummary=(
            f"Use the Paper2Code-style planning -> analysis -> coding workflow to translate {title} "
            "into an implementation brief while keeping stated claims separate from inferred design choices."
        ),
        statedClaims=stated_claims,
        inferredDesignDecisions=inferred_decisions,
        analysisQuestions=analysis_questions,
        codingPhases=coding_phases,
        evaluationChecks=evaluation_checks,
    )
