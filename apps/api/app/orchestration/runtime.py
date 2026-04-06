from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    ArtifactRecord,
    ArtifactStatus,
    EventLevel,
    SessionRecord,
    SessionStatus,
    TraceEventRecord,
)
from pydantic import BaseModel

from app.orchestration.blueprint import build_narrative_blueprint
from app.orchestration.contracts import (
    AdvanceSessionResponse,
    CapabilityRouteSummaryRecord,
    ContextBudgetSummaryRecord,
    EvaluationScorecardRecord,
    InterrogationPromptRecord,
    InterruptionType,
    JDAnalysisRecord,
    MemoryRiskSummaryRecord,
    NarrativeBlueprintRecord,
    InterruptReason,
    ResearchSummaryRecord,
    RuntimeArtifact,
    RuntimeStage,
    RuntimeTraceEvent,
    SessionEnvelope,
    StageKey,
    StageStatus,
    TrajectoryEvaluationSummaryRecord,
)
from app.orchestration.drafting import build_resume_package
from app.orchestration.evaluation import evaluate_resume_package
from app.orchestration.interrogation import (
    build_canonical_session_context,
    build_interrogation_prompt,
)
from app.orchestration.research import generate_jd_analysis_bundle
from app.vault.contracts import GuidedRoleCaptureRequest, StoryCheckpointRecord
from app.vault.ingestion import build_guided_capture_request, extract_statements
from app.vault.service import create_vault_role_tree, serialize_vault_role

STAGE_LABELS: dict[StageKey, str] = {
    StageKey.BOOTSTRAP: "Bootstrap",
    StageKey.VAULT_SEED_IMPORT: "Vault Seed Import",
    StageKey.VAULT_ROLE_INTERVIEW: "Vault Role Interview",
    StageKey.VAULT_STORY_CHECKPOINT: "Vault Story Checkpoint",
    StageKey.JD_INTAKE: "Job Description Intake",
    StageKey.JD_ANALYSIS_REVIEW: "JD Analysis Review",
    StageKey.CAREER_INTAKE: "Career Intake",
    StageKey.BLUEPRINT_REVIEW: "Blueprint Review",
    StageKey.DRAFT_REVIEW: "Draft Review",
    StageKey.COMPLETE: "Complete",
}


def utc_now() -> datetime:
    return datetime.now(UTC)


def ensure_runtime_state(record: SessionRecord) -> dict[str, Any]:
    snapshot = dict(record.state_snapshot or {})
    runtime = dict(snapshot.get("runtime") or {})
    runtime.setdefault("current_stage", record.stage or StageKey.BOOTSTRAP.value)
    runtime.setdefault("stage_status", StageStatus.PENDING.value)
    runtime.setdefault("interrupt_reason", InterruptReason.NONE.value)
    runtime.setdefault("interruption_type", None)
    runtime.setdefault("replan_from_stage", None)
    runtime.setdefault("stage_history", [runtime["current_stage"]])
    runtime.setdefault("answers", {})
    runtime.setdefault("canonical_session_context", {})
    runtime.setdefault("transitions", [])
    runtime.setdefault("memory_risk_summary", None)
    runtime.setdefault("context_budget_summary", None)
    runtime.setdefault("capability_route_summary", None)
    runtime.setdefault("trajectory_evaluation_summary", None)
    runtime.setdefault("jd_analysis_artifact_id", None)
    runtime.setdefault("research_summary_artifact_id", None)
    runtime.setdefault("blueprint_artifact_id", None)
    runtime.setdefault("draft_package_artifact_id", None)
    runtime.setdefault("evaluation_artifact_id", None)
    runtime.setdefault("flow", "resume_session")
    runtime.setdefault("updated_at", utc_now().isoformat())
    snapshot["runtime"] = runtime
    record.state_snapshot = snapshot
    return runtime


def persist_runtime_state(record: SessionRecord, runtime: dict[str, Any]) -> None:
    snapshot = dict(record.state_snapshot or {})
    snapshot["runtime"] = runtime
    record.state_snapshot = snapshot


def append_trace(
    db: Session,
    record: SessionRecord,
    *,
    stage: StageKey,
    message: str,
    payload: dict[str, Any] | None = None,
    level: EventLevel = EventLevel.INFO,
) -> TraceEventRecord:
    event = TraceEventRecord(
        session_id=record.id,
        stage=stage.value,
        level=level,
        message=message,
        payload=payload or {},
    )
    db.add(event)
    record.trace_events.append(event)
    return event


def find_stage_artifact(
    record: SessionRecord,
    *,
    stage: StageKey,
    kind: str,
) -> ArtifactRecord | None:
    for artifact in record.artifacts:
        if artifact.kind != kind:
            continue
        if artifact.payload.get("stageKey") == stage.value:
            return artifact
    return None


def upsert_stage_artifact(
    db: Session,
    record: SessionRecord,
    *,
    stage: StageKey,
    kind: str,
    status: ArtifactStatus,
    title: str,
    summary: str,
    payload: dict[str, Any] | None = None,
) -> ArtifactRecord:
    artifact = find_stage_artifact(record, stage=stage, kind=kind)

    merged_payload = {
        "stageKey": stage.value,
        "stageLabel": STAGE_LABELS[stage],
    }
    if payload:
        merged_payload.update(payload)

    if artifact is None:
        artifact = ArtifactRecord(
            session_id=record.id,
            kind=kind,
            status=status,
            payload=merged_payload,
        )
        db.add(artifact)
        record.artifacts.append(artifact)
    else:
        artifact.status = status
        artifact.payload = merged_payload

    artifact.payload["title"] = title
    artifact.payload["summary"] = summary
    return artifact


def transition_to(
    record: SessionRecord,
    runtime: dict[str, Any],
    stage: StageKey,
    *,
    status: StageStatus,
    interrupt_reason: InterruptReason = InterruptReason.NONE,
    interruption_type: InterruptionType | None = None,
    replan_from_stage: StageKey | None = None,
    preserve_replan_context: bool = False,
) -> None:
    record.stage = stage.value
    runtime["current_stage"] = stage.value
    runtime["stage_status"] = status.value
    runtime["interrupt_reason"] = interrupt_reason.value
    if preserve_replan_context:
        runtime.setdefault("interruption_type", None)
        runtime.setdefault("replan_from_stage", None)
    else:
        runtime["interruption_type"] = (
            interruption_type.value if interruption_type else None
        )
        runtime["replan_from_stage"] = (
            replan_from_stage.value if replan_from_stage else None
        )
    runtime["updated_at"] = utc_now().isoformat()

    if not runtime["stage_history"] or runtime["stage_history"][-1] != stage.value:
        runtime["stage_history"].append(stage.value)


def interrupt_session(
    db: Session,
    record: SessionRecord,
    runtime: dict[str, Any],
    *,
    stage: StageKey,
    reason: InterruptReason,
    message: str,
) -> str:
    transition_to(
        record,
        runtime,
        stage,
        status=StageStatus.INTERRUPTED,
        interrupt_reason=reason,
        preserve_replan_context=True,
    )
    record.status = SessionStatus.INTERRUPTED
    append_trace(
        db,
        record,
        stage=stage,
        message=message,
        payload={"interruptReason": reason.value},
    )
    return message


def determine_replan_stage(
    *,
    current_stage: StageKey,
    interruption_type: InterruptionType,
    suggested_stage: StageKey | None = None,
) -> StageKey:
    if suggested_stage is not None:
        return suggested_stage

    if interruption_type in {
        InterruptionType.ADD_REQUIREMENT,
        InterruptionType.REVISE_REQUIREMENT,
        InterruptionType.RETRACT_REQUIREMENT,
    }:
        if current_stage in {StageKey.BOOTSTRAP, StageKey.JD_INTAKE}:
            return StageKey.JD_ANALYSIS_REVIEW
        return StageKey.BLUEPRINT_REVIEW

    if interruption_type in {
        InterruptionType.CLARIFY_FACT,
        InterruptionType.RISK_FLAG,
    }:
        if current_stage in {
            StageKey.BOOTSTRAP,
            StageKey.JD_INTAKE,
            StageKey.JD_ANALYSIS_REVIEW,
        }:
            return StageKey.CAREER_INTAKE
        return StageKey.CAREER_INTAKE

    return StageKey.DRAFT_REVIEW


def request_runtime_replan(
    db: Session,
    record: SessionRecord,
    runtime: dict[str, Any],
    *,
    interruption_type: InterruptionType,
    note: str | None,
    source_stage: StageKey,
    suggested_stage: StageKey | None = None,
) -> str:
    replan_target = determine_replan_stage(
        current_stage=source_stage,
        interruption_type=interruption_type,
        suggested_stage=suggested_stage,
    )
    record.status = SessionStatus.RUNNING
    runtime["updated_at"] = utc_now().isoformat()

    upsert_stage_artifact(
        db,
        record,
        stage=replan_target,
        kind="interruption-request",
        status=ArtifactStatus.CANONICAL,
        title=f"Runtime replan: {interruption_type.value}",
        summary=(
            "A runtime interruption requested a targeted rerun from the earliest affected stage."
        ),
        payload={
            "sourceStage": source_stage.value,
            "interruptionType": interruption_type.value,
            "replanFromStage": replan_target.value,
            "note": note,
        },
    )
    append_trace(
        db,
        record,
        stage=source_stage,
        message="Runtime interruption requested a targeted rerun from the earliest affected stage.",
        payload={
            "interruptionType": interruption_type.value,
            "replanFromStage": replan_target.value,
            "note": note,
        },
    )
    transition_to(
        record,
        runtime,
        replan_target,
        status=StageStatus.RUNNING,
        interruption_type=interruption_type,
        replan_from_stage=replan_target,
    )
    return f"{source_stage.value}_to_{replan_target.value}"


def mark_blueprint_approved(record: SessionRecord, runtime: dict[str, Any]) -> None:
    blueprint_id = runtime.get("blueprint_artifact_id")
    if not blueprint_id:
        return

    for artifact in record.artifacts:
        if artifact.id == blueprint_id:
            artifact.status = ArtifactStatus.APPROVED
            artifact.payload = {
                **artifact.payload,
                "approvalState": "approved",
            }
            return


def mark_artifact_approved(record: SessionRecord, artifact_id: str | None) -> None:
    if not artifact_id:
        return

    for artifact in record.artifacts:
        if artifact.id == artifact_id:
            artifact.status = ArtifactStatus.APPROVED
            artifact.payload = {
                **artifact.payload,
                "approvalState": "approved",
            }
            return


def mark_stage_artifact_approved(
    record: SessionRecord,
    *,
    stage: StageKey,
    kind: str,
) -> None:
    artifact = find_stage_artifact(record, stage=stage, kind=kind)
    if artifact is None:
        return

    artifact.status = ArtifactStatus.APPROVED
    artifact.payload = {
        **artifact.payload,
        "approvalState": "approved",
    }


def mark_jd_analysis_approved(record: SessionRecord, runtime: dict[str, Any]) -> None:
    mark_stage_artifact_approved(
        record,
        stage=StageKey.JD_ANALYSIS_REVIEW,
        kind="jd-analysis",
    )
    mark_stage_artifact_approved(
        record,
        stage=StageKey.JD_ANALYSIS_REVIEW,
        kind="research-summary",
    )


def mark_vault_checkpoint_approved(
    record: SessionRecord, runtime: dict[str, Any]
) -> None:
    checkpoint_id = runtime.get("vault_checkpoint_artifact_id")
    if not checkpoint_id:
        return

    for artifact in record.artifacts:
        if artifact.id == checkpoint_id:
            artifact.status = ArtifactStatus.APPROVED
            artifact.payload = {
                **artifact.payload,
                "approvalState": "approved",
            }
    return


def serialize_model_payload(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(by_alias=True, mode="json")


def parse_jd_analysis(runtime: dict[str, Any]) -> JDAnalysisRecord:
    payload = runtime.get("job_constraint_profile") or {}
    return JDAnalysisRecord.model_validate(payload)


def parse_research_summary(runtime: dict[str, Any]) -> ResearchSummaryRecord:
    payload = runtime.get("research_summary") or {}
    return ResearchSummaryRecord.model_validate(payload)


def parse_narrative_blueprint(runtime: dict[str, Any]) -> NarrativeBlueprintRecord:
    payload = runtime.get("narrative_blueprint") or {}
    return NarrativeBlueprintRecord.model_validate(payload)


def parse_evaluation_scorecard(runtime: dict[str, Any]) -> EvaluationScorecardRecord:
    payload = runtime.get("evaluation_scorecard") or {}
    return EvaluationScorecardRecord.model_validate(payload)


def build_vault_guided_request(runtime: dict[str, Any]) -> GuidedRoleCaptureRequest:
    return GuidedRoleCaptureRequest(
        companyName=str(runtime["vault_company_name"]),
        title=str(runtime["vault_role_title"]),
        roleSummary=runtime.get("vault_role_summary"),
        storyName=str(runtime["vault_story_name"]),
        rawDetails=str(runtime["answers"].get("vaultRoleDetails", "")),
        stackSummary=runtime.get("vault_stack_summary"),
        impactSummary=runtime.get("vault_impact_summary"),
    )


def run_vault_ingestion_flow(
    db: Session,
    record: SessionRecord,
    runtime: dict[str, Any],
    *,
    latest_answer: str | None,
    approve_checkpoint: bool,
) -> tuple[str, str | None]:
    transition_message = "no-op"

    while True:
        stage = StageKey(runtime["current_stage"])

        if stage is StageKey.BOOTSTRAP:
            record.status = SessionStatus.RUNNING
            append_trace(
                db,
                record,
                stage=StageKey.BOOTSTRAP,
                message="Vault ingestion session started and advanced to seed import.",
                payload={"flow": "vault_ingestion"},
            )
            transition_to(
                record,
                runtime,
                StageKey.VAULT_SEED_IMPORT,
                status=StageStatus.RUNNING,
            )
            transition_message = "bootstrap_to_vault_seed_import"
            continue

        if stage is StageKey.VAULT_SEED_IMPORT:
            upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="vault-question",
                status=ArtifactStatus.CANONICAL,
                title="Add seed material or skip",
                summary="Paste existing resume, portfolio, or profile text for this role, or type 'skip' to go straight to the focused interview.",
                payload={
                    "prompt": "Paste seed material for this role, or type 'skip'.",
                    "responseKey": "vaultSeed",
                },
            )
            if not latest_answer:
                transition_message = interrupt_session(
                    db,
                    record,
                    runtime,
                    stage=stage,
                    reason=InterruptReason.AWAITING_VAULT_SEED,
                    message="Paused for optional vault seed material.",
                )
                break

            runtime["answers"]["vaultSeed"] = latest_answer
            append_trace(
                db,
                record,
                stage=stage,
                message="Captured vault seed input and advanced to the focused role interview.",
            )
            latest_answer = None
            transition_to(
                record,
                runtime,
                StageKey.VAULT_ROLE_INTERVIEW,
                status=StageStatus.RUNNING,
            )
            transition_message = "vault_seed_import_to_vault_role_interview"
            continue

        if stage is StageKey.VAULT_ROLE_INTERVIEW:
            role_title = runtime.get("vault_role_title", "this role")
            story_name = runtime.get("vault_story_name", "this story")
            upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="vault-question",
                status=ArtifactStatus.CANONICAL,
                title="Capture one role or project thread",
                summary=f"Stay within {role_title} and focus only on the {story_name} thread so the vault stores one coherent story at a time.",
                payload={
                    "prompt": f"For {role_title}, describe the {story_name} thread only: what you built, the stack, and what changed.",
                    "responseKey": "vaultRoleDetails",
                },
            )
            if not latest_answer:
                transition_message = interrupt_session(
                    db,
                    record,
                    runtime,
                    stage=stage,
                    reason=InterruptReason.AWAITING_VAULT_ROLE_DETAILS,
                    message="Paused for focused vault role details.",
                )
                break

            runtime["answers"]["vaultRoleDetails"] = latest_answer
            detail_statements = extract_statements(latest_answer)
            checkpoint = StoryCheckpointRecord(
                roleTitle=str(runtime.get("vault_role_title", "Untitled role")),
                storyName=str(runtime.get("vault_story_name", "Untitled story")),
                totalFacts=len(detail_statements),
                draftEligibleFacts=len(detail_statements),
                pendingReviewFacts=len(detail_statements),
                suggestedNextQuestion=(
                    "What concrete scale, metric, or architecture detail is still missing?"
                    if len(detail_statements) < 3
                    else "This story is coherent enough for review. Confirm what should stay or be corrected."
                ),
                missingSignals=(
                    ["concrete implementation details"]
                    if len(detail_statements) < 3
                    else []
                ),
            )
            checkpoint_artifact = upsert_stage_artifact(
                db,
                record,
                stage=StageKey.VAULT_STORY_CHECKPOINT,
                kind="vault-checkpoint",
                status=ArtifactStatus.CANDIDATE,
                title=f"Review {checkpoint.story_name}",
                summary="A coherent role/story capture is ready for review before it becomes canonical vault memory.",
                payload={
                    "approvalState": "pending",
                    "rolePreview": {
                        "companyName": runtime.get("vault_company_name"),
                        "title": runtime.get("vault_role_title"),
                        "storyName": runtime.get("vault_story_name"),
                        "detailPreview": detail_statements[:5],
                    },
                    "checkpoint": checkpoint.model_dump(by_alias=True, mode="json"),
                },
            )
            runtime["vault_checkpoint_artifact_id"] = checkpoint_artifact.id
            append_trace(
                db,
                record,
                stage=stage,
                message="Captured focused role details and prepared a vault checkpoint review artifact.",
            )
            latest_answer = None
            transition_to(
                record,
                runtime,
                StageKey.VAULT_STORY_CHECKPOINT,
                status=StageStatus.RUNNING,
            )
            transition_message = "vault_role_interview_to_vault_story_checkpoint"
            continue

        if stage is StageKey.VAULT_STORY_CHECKPOINT:
            if not approve_checkpoint:
                transition_message = interrupt_session(
                    db,
                    record,
                    runtime,
                    stage=stage,
                    reason=InterruptReason.AWAITING_VAULT_CHECKPOINT_APPROVAL,
                    message="Paused for vault story checkpoint approval.",
                )
                break

            guided_request = build_vault_guided_request(runtime)
            role_record = create_vault_role_tree(
                db,
                user=record.user,
                payload=build_guided_capture_request(guided_request),
            )
            persisted_role = serialize_vault_role(role_record)
            mark_vault_checkpoint_approved(record, runtime)
            upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="vault-role-record",
                status=ArtifactStatus.CANONICAL,
                title=f"Stored {persisted_role.title}",
                summary="The reviewed role/story capture is now canonical vault memory.",
                payload={"role": persisted_role.model_dump(by_alias=True, mode="json")},
            )
            append_trace(
                db,
                record,
                stage=stage,
                message="Vault checkpoint approved and persisted to canonical vault storage.",
            )
            transition_to(
                record,
                runtime,
                StageKey.COMPLETE,
                status=StageStatus.COMPLETE,
            )
            record.status = SessionStatus.COMPLETE
            transition_message = "vault_story_checkpoint_to_complete"
            break

        break

    return transition_message, latest_answer


def advance_session(
    db: Session,
    record: SessionRecord,
    *,
    answer: str | None = None,
    approve_jd_analysis: bool = False,
    approve_blueprint: bool = False,
    approve_checkpoint: bool = False,
    accept_draft_review: bool = False,
    request_revision: bool = False,
    interruption_type: InterruptionType | None = None,
    interruption_note: str | None = None,
) -> AdvanceSessionResponse:
    runtime = ensure_runtime_state(record)
    latest_answer = answer.strip() if answer else None
    transition_message = "no-op"

    if runtime["flow"] == "vault_ingestion":
        transition_message, latest_answer = run_vault_ingestion_flow(
            db,
            record,
            runtime,
            latest_answer=latest_answer,
            approve_checkpoint=approve_checkpoint,
        )
        persist_runtime_state(record, runtime)
        db.flush()
        return AdvanceSessionResponse(
            transition=transition_message,
            interrupted=record.status == SessionStatus.INTERRUPTED,
            envelope=build_session_envelope(record),
        )

    if interruption_type is not None:
        transition_message = request_runtime_replan(
            db,
            record,
            runtime,
            interruption_type=interruption_type,
            note=interruption_note or latest_answer,
            source_stage=StageKey(runtime["current_stage"]),
        )
        latest_answer = None

    while True:
        stage = StageKey(runtime["current_stage"])

        if stage is StageKey.BOOTSTRAP:
            record.status = SessionStatus.RUNNING
            append_trace(
                db,
                record,
                stage=StageKey.BOOTSTRAP,
                message="Session bootstrap started and advanced into the first intake boundary.",
            )
            transition_to(
                record,
                runtime,
                StageKey.JD_INTAKE,
                status=StageStatus.RUNNING,
            )
            transition_message = "bootstrap_to_jd_intake"
            continue

        if stage is StageKey.JD_INTAKE:
            upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="question",
                status=ArtifactStatus.CANONICAL,
                title="Provide the target job description",
                summary="The orchestrator is waiting for the raw job description before it can analyze the role.",
                payload={
                    "prompt": "Paste the job description or company role text.",
                    "responseKey": "jobDescription",
                },
            )
            if not latest_answer:
                transition_message = interrupt_session(
                    db,
                    record,
                    runtime,
                    stage=stage,
                    reason=InterruptReason.AWAITING_JOB_DESCRIPTION,
                    message="Paused for the user's job description input.",
                )
                break

            runtime["answers"]["jobDescription"] = latest_answer
            analysis, research = generate_jd_analysis_bundle(latest_answer)
            runtime["job_constraint_profile"] = serialize_model_payload(analysis)
            runtime["research_summary"] = serialize_model_payload(research)

            jd_analysis = upsert_stage_artifact(
                db,
                record,
                stage=StageKey.JD_ANALYSIS_REVIEW,
                kind="jd-analysis",
                status=ArtifactStatus.CANDIDATE,
                title="Structured JD analysis",
                summary="The job description has been parsed into requirements, archetype, and success signals for approval.",
                payload={
                    "approvalState": "pending",
                    "analysis": runtime["job_constraint_profile"],
                },
            )
            research_summary = upsert_stage_artifact(
                db,
                record,
                stage=StageKey.JD_ANALYSIS_REVIEW,
                kind="research-summary",
                status=ArtifactStatus.CANDIDATE,
                title="Role and company strategy summary",
                summary="Cited research findings and a concise strategy summary for how the resume should shift.",
                payload={
                    "approvalState": "pending",
                    "research": runtime["research_summary"],
                },
            )
            runtime["jd_analysis_artifact_id"] = jd_analysis.id
            runtime["research_summary_artifact_id"] = research_summary.id
            append_trace(
                db,
                record,
                stage=stage,
                message="Captured job description input and prepared JD analysis and research artifacts.",
            )
            latest_answer = None
            transition_to(
                record,
                runtime,
                StageKey.JD_ANALYSIS_REVIEW,
                status=StageStatus.RUNNING,
            )
            transition_message = "jd_intake_to_jd_analysis_review"
            continue

        if stage is StageKey.JD_ANALYSIS_REVIEW:
            if not approve_jd_analysis:
                transition_message = interrupt_session(
                    db,
                    record,
                    runtime,
                    stage=stage,
                    reason=InterruptReason.AWAITING_JD_ANALYSIS_APPROVAL,
                    message="Paused for JD analysis and research approval.",
                )
                break

            mark_jd_analysis_approved(record, runtime)
            append_trace(
                db,
                record,
                stage=stage,
                message="JD analysis approved and advanced to career intake.",
            )
            transition_to(
                record,
                runtime,
                StageKey.CAREER_INTAKE,
                status=StageStatus.RUNNING,
            )
            transition_message = "jd_analysis_review_to_career_intake"
            continue

        if stage is StageKey.CAREER_INTAKE:
            jd_analysis = parse_jd_analysis(runtime)
            research_summary = parse_research_summary(runtime)
            interrogation_prompt = build_interrogation_prompt(
                db,
                user=record.user,
                analysis=jd_analysis,
                research=research_summary,
            )
            upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="interrogation-question",
                status=ArtifactStatus.CANONICAL,
                title=f"Fill the gap for {interrogation_prompt.target_requirement}",
                summary=interrogation_prompt.why_it_matters,
                payload={
                    "prompt": interrogation_prompt.prompt,
                    "responseKey": interrogation_prompt.response_key,
                    "targetRequirement": interrogation_prompt.target_requirement,
                    "whyItMatters": interrogation_prompt.why_it_matters,
                    "supportingSignals": interrogation_prompt.supporting_signals,
                    "evidenceGap": interrogation_prompt.evidence_gap,
                },
            )
            if not latest_answer:
                transition_message = interrupt_session(
                    db,
                    record,
                    runtime,
                    stage=stage,
                    reason=InterruptReason.AWAITING_EXPERIENCE_DETAILS,
                    message="Paused for the user's raw experience details.",
                )
                break

            runtime["answers"][interrogation_prompt.response_key] = latest_answer
            runtime["canonical_session_context"] = build_canonical_session_context(
                runtime,
                prompt=interrogation_prompt,
                answer=latest_answer,
            )
            upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="session-context",
                status=ArtifactStatus.CANONICAL,
                title="Canonical session context",
                summary="Approved JD context and user-provided gap answers that downstream stages should treat as canonical session state.",
                payload={
                    "canonicalContext": runtime["canonical_session_context"],
                },
            )
            append_trace(
                db,
                record,
                stage=stage,
                message=(
                    "Captured the highest-impact interrogation answer and persisted it as canonical session context."
                ),
            )
            latest_answer = None
            transition_to(
                record,
                runtime,
                StageKey.BLUEPRINT_REVIEW,
                status=StageStatus.RUNNING,
            )
            transition_message = "career_intake_to_blueprint_review"
            continue

        if stage is StageKey.BLUEPRINT_REVIEW:
            jd_analysis = parse_jd_analysis(runtime)
            research_summary = parse_research_summary(runtime)
            blueprint_record = build_narrative_blueprint(
                db,
                user=record.user,
                analysis=jd_analysis,
                research=research_summary,
                canonical_context=runtime["canonical_session_context"],
            )
            runtime["narrative_blueprint"] = serialize_model_payload(blueprint_record)
            blueprint = upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="blueprint",
                status=ArtifactStatus.CANDIDATE,
                title="Phase-three narrative blueprint",
                summary="A one-page narrative blueprint built from approved JD context and draft-safe vault evidence.",
                payload={
                    "blueprint": runtime["narrative_blueprint"],
                    "approvalState": "pending",
                },
            )
            runtime["blueprint_artifact_id"] = blueprint.id

            if not approve_blueprint:
                transition_message = interrupt_session(
                    db,
                    record,
                    runtime,
                    stage=stage,
                    reason=InterruptReason.AWAITING_BLUEPRINT_APPROVAL,
                    message="Paused for blueprint approval before drafting.",
                )
                break

            mark_blueprint_approved(record, runtime)
            append_trace(
                db,
                record,
                stage=stage,
                message="Blueprint approved and advanced to the draft review stage.",
            )
            transition_to(
                record,
                runtime,
                StageKey.DRAFT_REVIEW,
                status=StageStatus.RUNNING,
            )
            transition_message = "blueprint_review_to_draft_review"
            continue

        if stage is StageKey.DRAFT_REVIEW:
            blueprint = parse_narrative_blueprint(runtime)
            package_record = build_resume_package(
                blueprint=blueprint,
                analysis=parse_jd_analysis(runtime),
                research=parse_research_summary(runtime),
                email_address=record.user.email_address,
            )
            runtime["draft_package"] = serialize_model_payload(package_record)
            draft_package = upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="draft-package",
                status=ArtifactStatus.CANDIDATE,
                title="Tailored resume draft package",
                summary="Markdown resume plus interview talking points and concern-handling notes generated from the approved blueprint.",
                payload=runtime["draft_package"],
            )
            runtime["draft_package_artifact_id"] = draft_package.id
            scorecard_record = evaluate_resume_package(
                blueprint=blueprint,
                package=package_record,
                analysis=parse_jd_analysis(runtime),
            )
            runtime["evaluation_scorecard"] = serialize_model_payload(scorecard_record)
            scorecard_artifact = upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="evaluation-scorecard",
                status=ArtifactStatus.CANDIDATE,
                title="Draft evaluation scorecard",
                summary="Fit, evidence support, specificity, and overstatement risk for the current draft package.",
                payload=runtime["evaluation_scorecard"],
            )
            runtime["evaluation_artifact_id"] = scorecard_artifact.id
            if request_revision:
                rerun_target = parse_evaluation_scorecard(runtime).revision_target_stage
                if rerun_target is StageKey.DRAFT_REVIEW:
                    rerun_target = StageKey.BLUEPRINT_REVIEW
                transition_message = request_runtime_replan(
                    db,
                    record,
                    runtime,
                    interruption_type=InterruptionType.REQUEST_REVISION,
                    note="Draft review requested a targeted rerun.",
                    source_stage=stage,
                    suggested_stage=rerun_target,
                )
                continue

            if not accept_draft_review:
                transition_message = interrupt_session(
                    db,
                    record,
                    runtime,
                    stage=stage,
                    reason=InterruptReason.AWAITING_DRAFT_REVIEW,
                    message="Paused for draft review acceptance or targeted revision.",
                )
                break

            transition_to(
                record,
                runtime,
                StageKey.COMPLETE,
                status=StageStatus.COMPLETE,
            )
            record.status = SessionStatus.COMPLETE
            append_trace(
                db,
                record,
                stage=StageKey.COMPLETE,
                message="Runtime reached the phase-one completion boundary.",
            )
            transition_message = "draft_review_to_complete"
            break

        if stage is StageKey.COMPLETE:
            record.status = SessionStatus.COMPLETE
            transition_message = "already_complete"
            break

    persist_runtime_state(record, runtime)
    db.flush()
    return AdvanceSessionResponse(
        transition=transition_message,
        interrupted=record.status == SessionStatus.INTERRUPTED,
        envelope=build_session_envelope(record),
    )


def build_stage(record: SessionRecord) -> RuntimeStage:
    runtime = ensure_runtime_state(record)
    stage_key = StageKey(record.stage or runtime["current_stage"])
    status_map = {
        SessionStatus.DRAFT: StageStatus.PENDING,
        SessionStatus.RUNNING: StageStatus.RUNNING,
        SessionStatus.INTERRUPTED: StageStatus.INTERRUPTED,
        SessionStatus.COMPLETE: StageStatus.COMPLETE,
    }
    stage_status = status_map[record.status]
    interrupt_reason = (
        InterruptReason.NONE
        if stage_status is StageStatus.COMPLETE
        else InterruptReason(runtime["interrupt_reason"])
    )
    summary_map = {
        StageKey.BOOTSTRAP: "Preparing the session runtime.",
        StageKey.VAULT_SEED_IMPORT: "Waiting for optional imported seed material for one role or project thread.",
        StageKey.VAULT_ROLE_INTERVIEW: "Waiting for focused role/project details to deepen the vault.",
        StageKey.VAULT_STORY_CHECKPOINT: "A coherent role/story capture is ready for review before persistence.",
        StageKey.JD_INTAKE: "Waiting for or processing the target job description.",
        StageKey.JD_ANALYSIS_REVIEW: "Structured JD analysis and cited research are ready for approval.",
        StageKey.CAREER_INTAKE: "Waiting for or processing raw user experience context.",
        StageKey.BLUEPRINT_REVIEW: "Preparing or awaiting approval of the narrative blueprint.",
        StageKey.DRAFT_REVIEW: "Draft package and evaluation scorecard are ready for acceptance or targeted revision.",
        StageKey.COMPLETE: "The phase-one orchestration shell reached completion.",
    }
    return RuntimeStage(
        key=stage_key,
        label=STAGE_LABELS[stage_key],
        status=stage_status,
        summary=summary_map[stage_key],
        interruptReason=interrupt_reason,
        canResume=stage_status is not StageStatus.COMPLETE,
        updatedAt=datetime.fromisoformat(runtime["updated_at"]),
    )


def build_runtime_artifact(artifact: ArtifactRecord) -> RuntimeArtifact:
    return RuntimeArtifact(
        id=artifact.id,
        kind=artifact.kind,
        status=artifact.status.value,
        title=str(artifact.payload.get("title", artifact.kind)),
        summary=str(artifact.payload.get("summary", "")),
        payload=artifact.payload,
        createdAt=artifact.created_at,
        updatedAt=artifact.updated_at,
    )


def build_runtime_event(event: TraceEventRecord) -> RuntimeTraceEvent:
    return RuntimeTraceEvent(
        id=event.id,
        stage=StageKey(event.stage),
        level=event.level.value,
        message=event.message,
        payload=event.payload,
        createdAt=event.created_at,
    )


def build_session_envelope(
    record: SessionRecord, clerk_user_id: str | None = None
) -> SessionEnvelope:
    runtime = ensure_runtime_state(record)
    ordered_artifacts = sorted(record.artifacts, key=lambda item: item.created_at)
    ordered_events = sorted(record.trace_events, key=lambda item: item.created_at)

    return SessionEnvelope(
        id=record.id,
        userId=record.user_id,
        clerkUserId=clerk_user_id or str(record.user.clerk_user_id),
        title=record.title,
        status=record.status.value,
        stage=build_stage(record),
        stageHistory=[StageKey(stage) for stage in runtime["stage_history"]],
        interruptionType=(
            InterruptionType(runtime["interruption_type"])
            if runtime.get("interruption_type")
            else None
        ),
        replanFromStage=(
            StageKey(runtime["replan_from_stage"])
            if runtime.get("replan_from_stage")
            else None
        ),
        memoryRiskSummary=(
            MemoryRiskSummaryRecord.model_validate(runtime["memory_risk_summary"])
            if runtime.get("memory_risk_summary")
            else None
        ),
        contextBudgetSummary=(
            ContextBudgetSummaryRecord.model_validate(
                runtime["context_budget_summary"]
            )
            if runtime.get("context_budget_summary")
            else None
        ),
        capabilityRouteSummary=(
            CapabilityRouteSummaryRecord.model_validate(
                runtime["capability_route_summary"]
            )
            if runtime.get("capability_route_summary")
            else None
        ),
        trajectoryEvaluationSummary=(
            TrajectoryEvaluationSummaryRecord.model_validate(
                runtime["trajectory_evaluation_summary"]
            )
            if runtime.get("trajectory_evaluation_summary")
            else None
        ),
        artifactCount=len(ordered_artifacts),
        traceEventCount=len(ordered_events),
        artifacts=[build_runtime_artifact(artifact) for artifact in ordered_artifacts],
        traceEvents=[build_runtime_event(event) for event in ordered_events],
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )
