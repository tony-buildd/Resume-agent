from __future__ import annotations

from app.llm.openai_client import OpenAIResponsesClient
from app.orchestration.contracts import (
    CapabilityDescriptorRecord,
    CapabilityRouteCandidateRecord,
    CapabilityRouteRecord,
    CapabilityRouteSummaryRecord,
    CapabilityRouteTraceStepRecord,
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
    route_trace = [
        CapabilityRouteTraceStepRecord(
            capabilityKey="internal_jd_analysis",
            sourceType="internal",
            decision="selected",
            reason="The runtime always begins from the user-provided job description and deterministic parsing.",
        )
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
        route_trace.append(
            CapabilityRouteTraceStepRecord(
                capabilityKey="openai_web_research",
                sourceType="api",
                decision="selected",
                reason="Structured web research is available, so company and market context can use an API-backed source before any browser fallback.",
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
        route_trace.append(
            CapabilityRouteTraceStepRecord(
                capabilityKey="openai_web_research",
                sourceType="api",
                decision="deferred",
                reason="Provider-backed web research is unavailable for this runtime.",
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
        route_trace.append(
            CapabilityRouteTraceStepRecord(
                capabilityKey="huggingface_papers",
                sourceType="structured_external",
                decision="available",
                reason="Paper-oriented metadata lookup is available for research-heavy tasks, but not selected for standard JD research.",
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
    route_trace.extend(
        [
            CapabilityRouteTraceStepRecord(
                capabilityKey="browser_use_fallback",
                sourceType="browser",
                decision="fallback",
                reason="Browser automation remains a last resort after internal and API-backed sources.",
            ),
            CapabilityRouteTraceStepRecord(
                capabilityKey="hermes_sidecar",
                sourceType="sidecar",
                decision="deferred",
                reason="Hermes is intentionally kept out of the primary runtime route.",
            ),
            CapabilityRouteTraceStepRecord(
                capabilityKey="paper2code_design",
                sourceType="structured_external",
                decision="deferred",
                reason="Paper2Code is reserved for architecture research follow-up rather than normal JD analysis.",
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
        routeTrace=route_trace,
        registry=registry,
    )
