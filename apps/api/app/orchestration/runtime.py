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
from app.orchestration.contracts import (
    AdvanceSessionResponse,
    InterruptReason,
    RuntimeArtifact,
    RuntimeStage,
    RuntimeTraceEvent,
    SessionEnvelope,
    StageKey,
    StageStatus,
)


STAGE_LABELS: dict[StageKey, str] = {
    StageKey.BOOTSTRAP: "Bootstrap",
    StageKey.JD_INTAKE: "Job Description Intake",
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
    runtime.setdefault("stage_history", [runtime["current_stage"]])
    runtime.setdefault("answers", {})
    runtime.setdefault("transitions", [])
    runtime.setdefault("blueprint_artifact_id", None)
    runtime.setdefault("updated_at", utc_now().isoformat())
    snapshot["runtime"] = runtime
    record.state_snapshot = snapshot
    return runtime


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
) -> None:
    record.stage = stage.value
    runtime["current_stage"] = stage.value
    runtime["stage_status"] = status.value
    runtime["interrupt_reason"] = interrupt_reason.value
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


def advance_session(
    db: Session,
    record: SessionRecord,
    *,
    answer: str | None = None,
    approve_blueprint: bool = False,
) -> AdvanceSessionResponse:
    runtime = ensure_runtime_state(record)
    latest_answer = answer.strip() if answer else None
    transition_message = "no-op"

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
            append_trace(
                db,
                record,
                stage=stage,
                message="Captured job description input and advanced to career intake.",
            )
            latest_answer = None
            transition_to(
                record,
                runtime,
                StageKey.CAREER_INTAKE,
                status=StageStatus.RUNNING,
            )
            transition_message = "jd_intake_to_career_intake"
            continue

        if stage is StageKey.CAREER_INTAKE:
            upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="question",
                status=ArtifactStatus.CANONICAL,
                title="Provide raw experience details",
                summary="The orchestrator is waiting for the user's raw experience context before blueprinting.",
                payload={
                    "prompt": "Share the raw accomplishments, projects, stack, and scope for the most relevant experience.",
                    "responseKey": "experienceDetails",
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

            runtime["answers"]["experienceDetails"] = latest_answer
            append_trace(
                db,
                record,
                stage=stage,
                message="Captured experience details and prepared a blueprint review artifact.",
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
            blueprint = upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="blueprint",
                status=ArtifactStatus.CANDIDATE,
                title="Phase-one narrative blueprint",
                summary="A skeletal blueprint built from the captured JD and experience data, ready for approval.",
                payload={
                    "sections": ["header", "skills", "experience", "projects"],
                    "story": "Match the strongest available experience to the role before drafting.",
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
            upsert_stage_artifact(
                db,
                record,
                stage=stage,
                kind="resume-draft",
                status=ArtifactStatus.CANDIDATE,
                title="Phase-one draft placeholder",
                summary="The foundation runtime can now persist a resumable draft artifact for later phases to replace.",
                payload={
                    "format": "markdown",
                    "status": "placeholder",
                },
            )
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

    db.flush()
    return AdvanceSessionResponse(
        transition=transition_message,
        interrupted=record.status == SessionStatus.INTERRUPTED,
        envelope=build_session_envelope(record),
    )


def build_stage(record: SessionRecord) -> RuntimeStage:
    runtime = ensure_runtime_state(record)
    stage_key = StageKey(runtime["current_stage"])
    stage_status = StageStatus(runtime["stage_status"])
    interrupt_reason = InterruptReason(runtime["interrupt_reason"])
    summary_map = {
        StageKey.BOOTSTRAP: "Preparing the session runtime.",
        StageKey.JD_INTAKE: "Waiting for or processing the target job description.",
        StageKey.CAREER_INTAKE: "Waiting for or processing raw user experience context.",
        StageKey.BLUEPRINT_REVIEW: "Preparing or awaiting approval of the narrative blueprint.",
        StageKey.DRAFT_REVIEW: "Draft artifact is ready for review or completion.",
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


def build_session_envelope(record: SessionRecord, clerk_user_id: str | None = None) -> SessionEnvelope:
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
        artifactCount=len(ordered_artifacts),
        traceEventCount=len(ordered_events),
        artifacts=[build_runtime_artifact(artifact) for artifact in ordered_artifacts],
        traceEvents=[build_runtime_event(event) for event in ordered_events],
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )
