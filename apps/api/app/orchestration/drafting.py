from __future__ import annotations

import re

from app.orchestration.contracts import (
    BlueprintRoleRecord,
    JDAnalysisRecord,
    NarrativeBlueprintRecord,
    ResearchSummaryRecord,
    ConcernHandlingNoteRecord,
    InterviewTalkingPointRecord,
    ResumePackageRecord,
)

MAX_TALKING_POINTS = 3
MAX_CONCERNS = 3


def build_resume_package(
    *,
    blueprint: NarrativeBlueprintRecord,
    analysis: JDAnalysisRecord,
    research: ResearchSummaryRecord,
    email_address: str | None = None,
) -> ResumePackageRecord:
    markdown_resume = build_markdown_resume(
        blueprint=blueprint,
        analysis=analysis,
        research=research,
        email_address=email_address,
    )
    return ResumePackageRecord(
        markdownResume=markdown_resume,
        talkingPoints=build_talking_points(blueprint),
        concernHandlingNotes=build_concern_handling_notes(blueprint, analysis),
    )


def build_markdown_resume(
    *,
    blueprint: NarrativeBlueprintRecord,
    analysis: JDAnalysisRecord,
    research: ResearchSummaryRecord,
    email_address: str | None,
) -> str:
    lines = [
        "# Candidate Name",
        build_header_line(email_address=email_address, research=research),
        "",
        "## Target Narrative",
        blueprint.narrative_angle,
        "",
        "## Skills",
        ", ".join(format_term(item) for item in blueprint.skills_focus)
        or "Add validated skills here.",
        "",
        "## Experience",
    ]

    if blueprint.selected_roles:
        for role in blueprint.selected_roles:
            lines.extend(render_role(role))
    else:
        lines.append(
            "- Add draft-safe experience evidence before producing a recruiter-ready experience section."
        )

    project_lines = render_projects(blueprint.selected_roles)
    if project_lines:
        lines.extend(["", "## Projects", *project_lines])

    lines.extend(
        [
            "",
            "## Tailoring Notes",
            f"- Target role focus: {analysis.primary_focus}.",
            f"- Expected impact: {analysis.business_impact}.",
            f"- Strategic summary: {research.strategic_summary}.",
        ]
    )

    return "\n".join(line for line in lines if line is not None).strip()


def build_header_line(
    *,
    email_address: str | None,
    research: ResearchSummaryRecord,
) -> str:
    contact_line = email_address or "email@example.com"
    target = research.role_title or "Target Role"
    return f"{contact_line} | Tailored for {target}"


def render_role(role: BlueprintRoleRecord) -> list[str]:
    lines = [
        f"### {role.role_title} | {role.company_name}",
        f"*{role.why_selected}*",
    ]
    for bullet in role.selected_bullets:
        suffix = f" ({bullet.source_story_name})" if bullet.source_story_name else ""
        lines.append(f"- {highlight_bullet(bullet.text)}{suffix}")
    return lines + [""]


def render_projects(roles: list[BlueprintRoleRecord]) -> list[str]:
    project_lines: list[str] = []
    seen: set[str] = set()
    for role in roles:
        for bullet in role.selected_bullets:
            if not bullet.source_story_name:
                continue
            key = bullet.source_story_name.lower()
            if key in seen:
                continue
            seen.add(key)
            project_lines.append(
                f"- **{bullet.source_story_name}**: highlighted under {role.role_title} at {role.company_name}."
            )
    return project_lines


def build_talking_points(
    blueprint: NarrativeBlueprintRecord,
) -> list[InterviewTalkingPointRecord]:
    talking_points: list[InterviewTalkingPointRecord] = []
    for role in blueprint.selected_roles:
        for bullet in role.selected_bullets:
            talking_points.append(
                InterviewTalkingPointRecord(
                    title=f"{role.role_title} at {role.company_name}",
                    prompt=(
                        f"Expand on how you delivered: {bullet.text} "
                        f"Why it matters: {bullet.rationale}"
                    ),
                )
            )
            if len(talking_points) >= MAX_TALKING_POINTS:
                return talking_points
    return talking_points


def build_concern_handling_notes(
    blueprint: NarrativeBlueprintRecord,
    analysis: JDAnalysisRecord,
) -> list[ConcernHandlingNoteRecord]:
    notes: list[ConcernHandlingNoteRecord] = []
    omitted = blueprint.omitted_signals[:MAX_CONCERNS]
    for signal in omitted:
        notes.append(
            ConcernHandlingNoteRecord(
                concern=f"Direct evidence for {signal} is still thin.",
                mitigation=(
                    "Acknowledge the adjacent experience honestly and redirect to the "
                    "closest shipped work or validated learning pattern."
                ),
            )
        )

    if not notes:
        notes.append(
            ConcernHandlingNoteRecord(
                concern="The hiring team may probe for depth on the lead JD requirements.",
                mitigation=(
                    f"Anchor answers in {analysis.success_definition[0] if analysis.success_definition else 'business impact'}, "
                    "then walk through the implementation details behind the strongest bullet."
                ),
            )
        )

    return notes


def highlight_bullet(text: str) -> str:
    highlighted = re.sub(r"\b(\d[\d,.%+kKmM]*)\b", r"**\1**", text)
    return highlighted


def format_term(term: str) -> str:
    return f"**{term}**" if should_highlight_term(term) else term


def should_highlight_term(term: str) -> bool:
    normalized = term.strip()
    if not normalized:
        return False
    return (
        bool(re.search(r"[0-9]|[A-Z]{2,}", normalized)) or len(normalized.split()) <= 2
    )
