from __future__ import annotations

import re

from app.db.models import VaultReviewState, VaultSourceType
from app.vault.contracts import (
    CreateVaultRoleRequest,
    GuidedRoleCaptureRequest,
    SeedImportRequest,
    StoryCheckpointRecord,
    VaultBulletCandidateInput,
    VaultFactInput,
    VaultIngestionResponse,
    VaultProjectStoryInput,
    VaultRoleRecord,
)

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def build_seed_import_request(payload: SeedImportRequest) -> CreateVaultRoleRequest:
    notes = extract_statements(payload.seed_text)
    story_name = payload.story_name or "Imported background"

    role_facts = [
        VaultFactInput(
            clientKey=f"seed-fact-{index}",
            kind="seed_note",
            statement=statement,
            evidence=None,
            sourceType=VaultSourceType.SEED_MATERIAL,
            reviewState=VaultReviewState.USER_STATED,
            draftEligible=True,
            details={"origin": "seed_import"},
        )
        for index, statement in enumerate(notes[:4], start=1)
    ]

    project_story = VaultProjectStoryInput(
        clientKey="seed-story-1",
        name=story_name,
        summary=f"Imported from existing material for {payload.title}.",
        stackSummary=None,
        impactSummary=None,
        sourceType=VaultSourceType.SEED_MATERIAL,
        reviewState=VaultReviewState.USER_STATED,
        draftEligible=True,
        details={"origin": "seed_import"},
        facts=[
            VaultFactInput(
                clientKey=f"seed-story-fact-{index}",
                kind="seed_detail",
                statement=statement,
                evidence=None,
                sourceType=VaultSourceType.SEED_MATERIAL,
                reviewState=VaultReviewState.USER_STATED,
                draftEligible=True,
                details={"origin": "seed_import"},
            )
            for index, statement in enumerate(notes[4:8], start=1)
        ],
        bulletCandidates=(
            [
                VaultBulletCandidateInput(
                    text=notes[0],
                    storyAngle="seed_import",
                    sourceType=VaultSourceType.SEED_MATERIAL,
                    reviewState=VaultReviewState.USER_STATED,
                    draftEligible=True,
                    supportingFactClientKeys=["seed-fact-1"] if role_facts else [],
                    details={"origin": "seed_import"},
                )
            ]
            if notes
            else []
        ),
    )

    return CreateVaultRoleRequest(
        companyName=payload.company_name,
        companyDomain=None,
        companySummary="Imported from existing user material.",
        title=payload.title,
        startDate=payload.start_date,
        endDate=payload.end_date,
        location=payload.location,
        summary="Seeded from imported material.",
        roleFacts=role_facts,
        roleBulletCandidates=[],
        projectStories=[project_story],
    )


def build_guided_capture_request(
    payload: GuidedRoleCaptureRequest,
) -> CreateVaultRoleRequest:
    details = extract_statements(payload.raw_details)

    project_story = VaultProjectStoryInput(
        clientKey="guided-story-1",
        name=payload.story_name,
        summary=payload.role_summary or f"Guided capture for {payload.story_name}.",
        stackSummary=payload.stack_summary,
        impactSummary=payload.impact_summary,
        sourceType=VaultSourceType.INTERVIEW_ANSWER,
        reviewState=VaultReviewState.USER_STATED,
        draftEligible=True,
        details={"origin": "guided_capture"},
        facts=[
            VaultFactInput(
                clientKey=f"guided-fact-{index}",
                kind="interview_detail",
                statement=statement,
                evidence=None,
                sourceType=VaultSourceType.INTERVIEW_ANSWER,
                reviewState=VaultReviewState.USER_STATED,
                draftEligible=True,
                details={"origin": "guided_capture"},
            )
            for index, statement in enumerate(details, start=1)
        ],
        bulletCandidates=(
            [
                VaultBulletCandidateInput(
                    text=details[0],
                    storyAngle="guided_capture",
                    sourceType=VaultSourceType.AGENT_INFERENCE,
                    reviewState=VaultReviewState.INFERRED,
                    draftEligible=False,
                    supportingFactClientKeys=["guided-fact-1"] if details else [],
                    details={"origin": "guided_capture"},
                )
            ]
            if details
            else []
        ),
    )

    return CreateVaultRoleRequest(
        companyName=payload.company_name,
        companyDomain=None,
        companySummary=None,
        title=payload.title,
        startDate=payload.start_date,
        endDate=payload.end_date,
        location=payload.location,
        summary=payload.role_summary,
        roleFacts=[],
        roleBulletCandidates=[],
        projectStories=[project_story],
    )


def build_checkpoint(mode: str, role: VaultRoleRecord) -> StoryCheckpointRecord:
    story = role.project_stories[0] if role.project_stories else None
    facts = story.facts if story else role.role_facts
    missing_signals: list[str] = []

    if story and not story.stack_summary:
        missing_signals.append("stack specificity")
    if story and not story.impact_summary:
        missing_signals.append("impact metrics")
    if len(facts) < 3:
        missing_signals.append("concrete implementation details")

    next_question = (
        "What concrete scale, metric, or architecture detail is still missing?"
        if missing_signals
        else "This story is coherent enough for review. Confirm what should stay or be corrected."
    )

    return StoryCheckpointRecord(
        roleTitle=role.title,
        storyName=story.name if story else role.title,
        totalFacts=len(facts),
        draftEligibleFacts=sum(1 for item in facts if item.draft_eligible),
        pendingReviewFacts=sum(
            1
            for item in facts
            if item.review_state
            in {VaultReviewState.INFERRED, VaultReviewState.USER_STATED}
        ),
        suggestedNextQuestion=next_question,
        missingSignals=missing_signals,
    )


def build_ingestion_response(
    mode: str, role: VaultRoleRecord
) -> VaultIngestionResponse:
    return VaultIngestionResponse(
        mode=mode,
        role=role,
        checkpoint=build_checkpoint(mode, role),
    )


def extract_statements(raw_text: str) -> list[str]:
    return [
        normalize_statement(chunk)
        for chunk in SENTENCE_SPLIT_RE.split(raw_text)
        if normalize_statement(chunk)
    ]


def normalize_statement(value: str) -> str:
    return " ".join(value.strip().split())
