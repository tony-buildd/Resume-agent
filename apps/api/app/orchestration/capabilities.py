from __future__ import annotations

from app.llm.openai_client import OpenAIResponsesClient
from app.orchestration.contracts import (
    CapabilityDescriptorRecord,
    CapabilityRouteCandidateRecord,
    CapabilityRouteRecord,
    CapabilityRouteSummaryRecord,
)


def build_capability_registry() -> list[CapabilityDescriptorRecord]:
    return [
        CapabilityDescriptorRecord(
            key="internal_jd_analysis",
            label="Internal JD analyzer",
            scope=["job description parsing", "heuristic research fallback"],
            latency="low",
            trustLevel="high",
            authRequired=False,
            structuredOutput=True,
            sourceType="internal",
            preferredUseCases=[
                "user-provided job description",
                "deterministic parsing fallback",
            ],
        ),
        CapabilityDescriptorRecord(
            key="openai_web_research",
            label="OpenAI web research",
            scope=["company research", "role research", "citation-aware synthesis"],
            latency="medium",
            trustLevel="medium",
            authRequired=True,
            structuredOutput=True,
            sourceType="api",
            preferredUseCases=[
                "company context",
                "market signals",
                "source-backed strategy summaries",
            ],
        ),
        CapabilityDescriptorRecord(
            key="huggingface_papers",
            label="Hugging Face papers",
            scope=["paper metadata", "arXiv paper lookup", "research enrichment"],
            latency="medium",
            trustLevel="medium",
            authRequired=False,
            structuredOutput=True,
            sourceType="structured_external",
            preferredUseCases=[
                "paper or arXiv URLs",
                "research metadata enrichment",
            ],
        ),
        CapabilityDescriptorRecord(
            key="browser_use_fallback",
            label="Browser Use fallback",
            scope=["dynamic websites", "browser-only research", "fallback browsing"],
            latency="high",
            trustLevel="medium",
            authRequired=True,
            structuredOutput=False,
            sourceType="browser",
            preferredUseCases=[
                "dynamic sites without stable APIs",
                "last-resort browser automation",
            ],
        ),
        CapabilityDescriptorRecord(
            key="hermes_sidecar",
            label="Hermes sidecar",
            scope=["sidecar analysis", "comparative reasoning", "toolchain diagnostics"],
            latency="medium",
            trustLevel="medium",
            authRequired=True,
            structuredOutput=False,
            sourceType="sidecar",
            preferredUseCases=[
                "sidecar diagnostics",
                "comparative agent workflows",
            ],
        ),
        CapabilityDescriptorRecord(
            key="paper2code_design",
            label="Paper2Code design helper",
            scope=["paper-to-design translation", "implementation planning"],
            latency="high",
            trustLevel="medium",
            authRequired=False,
            structuredOutput=False,
            sourceType="structured_external",
            preferredUseCases=[
                "turning papers into design plans",
                "architecture research follow-up",
            ],
        ),
    ]


def plan_capability_route(
    *,
    job_description: str,
    client: OpenAIResponsesClient | None = None,
) -> CapabilityRouteRecord:
    registry = build_capability_registry()
    llm_client = client or OpenAIResponsesClient()
    normalized = job_description.lower()
    registry_map = {item.key: item for item in registry}

    selected_key = "internal_jd_analysis"
    candidates: list[CapabilityRouteCandidateRecord] = [
        CapabilityRouteCandidateRecord(
            capabilityKey="internal_jd_analysis",
            selected=True,
            reason="All runs start from the user-provided job description before using any external source.",
        )
    ]
    notes = [
        "Routing policy prefers internal and structured sources before browser fallback.",
    ]
    source_type = "internal"
    fallback_used = False
    confidence = "high"

    if llm_client.enabled:
        selected_key = "openai_web_research"
        source_type = "api"
        candidates.append(
            CapabilityRouteCandidateRecord(
                capabilityKey="openai_web_research",
                selected=True,
                reason="OpenAI structured web research is available for source-backed company and role context.",
            )
        )
        notes.append("External company and market context can be sourced through structured API-backed web research.")
    else:
        candidates.append(
            CapabilityRouteCandidateRecord(
                capabilityKey="openai_web_research",
                selected=False,
                reason="Provider-backed web research is unavailable, so the system stays on internal parsing and heuristic research.",
            )
        )
        notes.append("External API research is unavailable, so the route remains deterministic.")

    if any(token in normalized for token in ("paper", "arxiv", "research", "agent")):
        candidates.append(
            CapabilityRouteCandidateRecord(
                capabilityKey="huggingface_papers",
                selected=False,
                reason="Relevant when the task references papers or research metadata, but not needed for ordinary JD analysis.",
            )
        )

    candidates.extend(
        [
            CapabilityRouteCandidateRecord(
                capabilityKey="browser_use_fallback",
                selected=False,
                fallback=True,
                reason="Browser automation is reserved for cases where internal and API-backed sources are insufficient.",
            ),
            CapabilityRouteCandidateRecord(
                capabilityKey="hermes_sidecar",
                selected=False,
                reason="Hermes remains a sidecar capability and is not part of the primary runtime route.",
            ),
            CapabilityRouteCandidateRecord(
                capabilityKey="paper2code_design",
                selected=False,
                reason="Paper2Code is reserved for architecture research follow-up, not direct JD processing.",
            ),
        ]
    )

    return CapabilityRouteRecord(
        summary=CapabilityRouteSummaryRecord(
            selectedCapability=selected_key,
            sourceType=source_type,
            fallbackUsed=fallback_used,
            confidence=confidence,
            notes=notes,
        ),
        selectedCapability=registry_map[selected_key],
        candidates=candidates,
        registry=registry,
    )
