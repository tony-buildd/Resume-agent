from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

from pydantic import ValidationError

from app.llm.openai_client import OpenAIResponsesClient
from app.orchestration.contracts import (
    JDAnalysisRecord,
    ResearchSourceRecord,
    ResearchSummaryRecord,
)

STOPWORDS = {
    "about",
    "across",
    "also",
    "and",
    "are",
    "building",
    "company",
    "data",
    "deliver",
    "experience",
    "for",
    "from",
    "have",
    "help",
    "into",
    "looking",
    "must",
    "our",
    "role",
    "that",
    "the",
    "their",
    "this",
    "through",
    "using",
    "with",
    "will",
    "work",
    "you",
    "your",
}

PRIMARY_FOCUS_KEYWORDS: dict[str, set[str]] = {
    "backend": {
        "api",
        "backend",
        "distributed",
        "microservice",
        "services",
        "python",
        "java",
        "go",
    },
    "frontend": {
        "frontend",
        "react",
        "typescript",
        "ui",
        "ux",
        "design",
        "accessibility",
    },
    "full-stack": {"full stack", "full-stack", "end-to-end", "frontend", "backend"},
    "platform": {
        "platform",
        "infrastructure",
        "reliability",
        "ci/cd",
        "devops",
        "kubernetes",
    },
    "data": {"data", "etl", "warehouse", "analytics", "pipeline", "spark", "airflow"},
    "ai": {"llm", "ml", "machine learning", "ai", "prompt", "agent", "rag"},
}

ARCHETYPE_KEYWORDS: list[tuple[str, set[str]]] = [
    ("AI workflow builder", {"llm", "agent", "prompt", "automation", "ocr"}),
    (
        "platform and systems optimizer",
        {"reliability", "platform", "latency", "scale", "infrastructure"},
    ),
    (
        "product and integration builder",
        {"customer", "product", "feature", "integration", "ship"},
    ),
    ("data pipeline builder", {"data", "pipeline", "warehouse", "analytics", "batch"}),
]

LEVEL_KEYWORDS: list[tuple[str, set[str]]] = [
    ("staff", {"staff"}),
    ("principal", {"principal"}),
    ("senior", {"senior", "lead"}),
    ("mid-level", {"engineer ii", "sde2", "experienced"}),
    ("entry-level", {"junior", "new grad", "intern", "entry"}),
]


def generate_jd_analysis_bundle(
    job_description: str,
    *,
    client: OpenAIResponsesClient | None = None,
) -> tuple[JDAnalysisRecord, ResearchSummaryRecord]:
    llm_client = client or OpenAIResponsesClient()
    analysis = analyze_job_description(job_description, client=llm_client)
    research = summarize_role_research(
        job_description,
        analysis=analysis,
        client=llm_client,
    )
    return analysis, research


def analyze_job_description(
    job_description: str,
    *,
    client: OpenAIResponsesClient | None = None,
) -> JDAnalysisRecord:
    if client and client.enabled:
        try:
            payload = client.create_json_response(
                system_prompt=(
                    "You are a resume strategy analyst. Extract structured constraints from a job "
                    "description without inventing facts."
                ),
                user_prompt=(
                    "Analyze this job description and return structured output only.\n\n"
                    f"{job_description}"
                ),
                schema_name="jd_analysis",
                json_schema=JDAnalysisRecord.model_json_schema(),
            )
            return JDAnalysisRecord.model_validate(payload)
        except Exception:
            pass

    return heuristic_jd_analysis(job_description)


def summarize_role_research(
    job_description: str,
    *,
    analysis: JDAnalysisRecord,
    client: OpenAIResponsesClient | None = None,
) -> ResearchSummaryRecord:
    if client and client.enabled:
        try:
            response = client.create_response(
                system_prompt=(
                    "You are a company and role researcher. Use web search when helpful, cite sources, "
                    "and return only the requested JSON."
                ),
                user_prompt=(
                    "Research the company and role context for this job description. Use the job description "
                    "and web search results to produce a concise strategy summary with sources.\n\n"
                    f"Job description:\n{job_description}\n\n"
                    f"Structured JD analysis:\n{analysis.model_dump_json(by_alias=True)}"
                ),
                tools=[{"type": "web_search"}],
                include=["web_search_call.action.sources"],
                text_format={
                    "type": "json_schema",
                    "name": "research_summary",
                    "schema": ResearchSummaryRecord.model_json_schema(),
                    "strict": True,
                },
            )
            parsed = ResearchSummaryRecord.model_validate(json.loads(response.text))
            extracted_sources = extract_sources_from_payload(response.payload)
            if extracted_sources and not parsed.sources:
                return parsed.model_copy(update={"sources": extracted_sources})
            if extracted_sources:
                return parsed.model_copy(
                    update={"sources": merge_sources(parsed.sources, extracted_sources)}
                )
            return parsed
        except Exception:
            pass

    return heuristic_research_summary(job_description, analysis=analysis)


def heuristic_jd_analysis(job_description: str) -> JDAnalysisRecord:
    normalized = normalize_text(job_description)
    lines = split_relevant_lines(job_description)
    terms = extract_repeating_terms(normalized)

    return JDAnalysisRecord(
        topRequirements=extract_top_requirements(lines, normalized),
        primaryFocus=guess_primary_focus(normalized),
        repeatingTerms=terms[:8],
        expectedLevel=guess_expected_level(normalized),
        engineeringArchetype=guess_archetype(normalized),
        businessImpact=guess_business_impact(lines),
        successDefinition=extract_success_definition(lines),
    )


def heuristic_research_summary(
    job_description: str,
    *,
    analysis: JDAnalysisRecord,
) -> ResearchSummaryRecord:
    company_name = extract_company_name(job_description)
    role_title = extract_role_title(job_description)
    requirements = ", ".join(analysis.top_requirements[:3]) or analysis.primary_focus
    strategic_summary = (
        f"This role reads like a {analysis.engineering_archetype.lower()} search with emphasis on "
        f"{requirements}. The resume should foreground proof of {analysis.primary_focus} ownership and "
        "make the business outcome legible early."
    )

    market_signals = [
        f"Primary focus: {analysis.primary_focus}",
        f"Expected level: {analysis.expected_level}",
        f"Business impact: {analysis.business_impact}",
    ]
    source_notes = [
        "Derived from the user-provided job description.",
        "External web research is used only when OpenAI web search is configured.",
    ]

    return ResearchSummaryRecord(
        companyName=company_name,
        roleTitle=role_title,
        strategicSummary=strategic_summary,
        marketSignals=market_signals,
        sourceNotes=source_notes,
        sources=[
            ResearchSourceRecord(
                title="Provided job description",
                url=None,
                note="Primary source supplied directly by the user.",
            )
        ],
    )


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def split_relevant_lines(job_description: str) -> list[str]:
    lines = [line.strip(" -*\t") for line in job_description.splitlines()]
    return [line for line in lines if len(line) > 20]


def extract_top_requirements(lines: list[str], normalized: str) -> list[str]:
    candidates = [
        line
        for line in lines
        if any(
            token in line.lower()
            for token in (":", "experience", "build", "design", "develop", "knowledge")
        )
    ]
    if len(candidates) >= 5:
        return candidates[:5]

    fallback_terms = extract_repeating_terms(normalized)
    return [term.title() for term in fallback_terms[:5]]


def extract_repeating_terms(normalized: str) -> list[str]:
    words = re.findall(r"[a-z0-9/+.#-]{3,}", normalized)
    filtered = [word for word in words if word not in STOPWORDS and not word.isdigit()]
    counts = Counter(filtered)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked]


def guess_primary_focus(normalized: str) -> str:
    scores = {
        focus: sum(normalized.count(keyword) for keyword in keywords)
        for focus, keywords in PRIMARY_FOCUS_KEYWORDS.items()
    }
    best_focus = max(scores, key=scores.get)
    return best_focus if scores[best_focus] > 0 else "software engineering"


def guess_expected_level(normalized: str) -> str:
    for label, keywords in LEVEL_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            return label
    return "not explicitly stated"


def guess_archetype(normalized: str) -> str:
    scored = [
        (label, sum(normalized.count(keyword) for keyword in keywords))
        for label, keywords in ARCHETYPE_KEYWORDS
    ]
    label, score = max(scored, key=lambda item: item[1])
    return label if score > 0 else "generalist product engineer"


def guess_business_impact(lines: list[str]) -> str:
    for line in lines:
        lower = line.lower()
        if any(
            token in lower
            for token in (
                "customer",
                "revenue",
                "efficiency",
                "latency",
                "scale",
                "growth",
            )
        ):
            return line
    return "Business impact is implied but not stated explicitly."


def extract_success_definition(lines: list[str]) -> list[str]:
    candidates = [
        line
        for line in lines
        if any(
            token in line.lower()
            for token in ("you will", "responsible", "deliver", "improve", "own")
        )
    ]
    return candidates[:3] or lines[:3]


def extract_company_name(job_description: str) -> str | None:
    patterns = [
        r"company[:\s]+([A-Z][A-Za-z0-9& .-]+)",
        r"about\s+([A-Z][A-Za-z0-9& .-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, job_description)
        if match:
            return match.group(1).strip().rstrip(".")
    return None


def extract_role_title(job_description: str) -> str | None:
    lines = [line.strip() for line in job_description.splitlines() if line.strip()]
    for line in lines[:5]:
        if len(line) < 80 and any(
            token in line.lower()
            for token in ("engineer", "developer", "manager", "scientist")
        ):
            return line
    return None


def extract_sources_from_payload(payload: dict[str, Any]) -> list[ResearchSourceRecord]:
    collected: list[ResearchSourceRecord] = []
    seen: set[tuple[str, str | None]] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            url = node.get("url")
            title = node.get("title") or node.get("name")
            if isinstance(title, str) and (isinstance(url, str) or url is None):
                key = (title, url if isinstance(url, str) else None)
                if key not in seen and (url or title):
                    seen.add(key)
                    collected.append(
                        ResearchSourceRecord(
                            title=title,
                            url=url if isinstance(url, str) else None,
                            note=(
                                node.get("snippet")
                                if isinstance(node.get("snippet"), str)
                                else None
                            ),
                        )
                    )
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(payload)
    return collected[:6]


def merge_sources(
    left: list[ResearchSourceRecord],
    right: list[ResearchSourceRecord],
) -> list[ResearchSourceRecord]:
    merged: list[ResearchSourceRecord] = []
    seen: set[tuple[str, str | None]] = set()

    for source in [*left, *right]:
        key = (source.title, source.url)
        if key in seen:
            continue
        seen.add(key)
        merged.append(source)

    return merged
