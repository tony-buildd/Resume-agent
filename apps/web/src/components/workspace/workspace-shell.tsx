import Link from "next/link";

import type { StoryCheckpointRecord, VaultRoleRecord } from "@/lib/api/vault";
import type { SessionEnvelope } from "@/lib/api/sessions";

import { ArtifactPanel, selectActiveArtifact } from "./artifact-panel";
import { TracePanel } from "./trace-panel";

type VaultPromptSummary = {
  title: string;
  summary: string;
  prompt: string;
};

type WorkspaceShellProps = {
  session: SessionEnvelope;
  vaultRoles: VaultRoleRecord[];
  workspaceMode: "resume" | "vault";
  vaultPrompt: VaultPromptSummary | null;
  vaultCheckpoint: StoryCheckpointRecord | null;
  preferredArtifactId?: string | null;
};

const statusStyles: Record<string, string> = {
  interrupted: "border-amber-200 bg-amber-50 text-amber-900",
  running: "border-sky-200 bg-sky-50 text-sky-900",
  complete: "border-emerald-200 bg-emerald-50 text-emerald-900",
  draft: "border-slate-200 bg-slate-100 text-slate-700",
};

export function WorkspaceShell({
  session,
  vaultRoles,
  workspaceMode,
  vaultPrompt,
  vaultCheckpoint,
  preferredArtifactId,
}: WorkspaceShellProps) {
  const isVaultWorkspace =
    workspaceMode === "vault" || session.stage.key.startsWith("vault_");
  const activeArtifact = selectActiveArtifact(
    session.artifacts,
    session.stage.key,
    preferredArtifactId,
  );
  const surfaceMode = determineSurfaceMode(session);
  const workspaceSignals = buildWorkspaceSignals(session);
  const statusClass =
    statusStyles[session.status] ??
    "border-slate-200 bg-slate-100 text-slate-700";

  return (
    <section className="grid gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(340px,0.95fr)]">
      <article className="overflow-hidden rounded-[34px] border border-slate-200/80 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,255,0.96))] p-6 shadow-[0_28px_90px_-48px_rgba(15,23,42,0.55)] sm:p-7">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-2xl" aria-live="polite">
            <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">
              Guided workspace
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-[2.15rem]">
              {session.stage.label}
            </h2>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-[15px]">
              {session.stage.summary}
            </p>
          </div>

          <div className="flex flex-col items-start gap-2">
            <span
              className={`rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] ${statusClass}`}
            >
              {session.status}
            </span>
            <code className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] text-slate-600">
              {session.id}
            </code>
          </div>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
          <section className="rounded-[28px] border border-slate-200/90 bg-slate-950 p-5 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.26em] text-slate-400">
              Active conversation turn
            </p>
            <div className="mt-4 space-y-4">
              <div className="rounded-[24px] border border-white/10 bg-white/5 px-4 py-4">
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">
                  System focus
                </p>
                <p className="mt-2 text-sm leading-7 text-slate-100">
                  {activeArtifact?.summary ?? session.stage.summary}
                </p>
              </div>

              {isVaultWorkspace ? (
                vaultCheckpoint ? (
                  <div className="rounded-[24px] border border-cyan-500/30 bg-cyan-400/10 px-4 py-4">
                    <p className="text-[11px] uppercase tracking-[0.18em] text-cyan-200">
                      Checkpoint ready
                    </p>
                    <p className="mt-2 text-base font-semibold text-white">
                      {vaultCheckpoint.storyName}
                    </p>
                    <p className="mt-2 text-sm leading-7 text-cyan-50/90">
                      {vaultCheckpoint.suggestedNextQuestion}
                    </p>
                  </div>
                ) : vaultPrompt ? (
                  <div className="rounded-[24px] border border-cyan-500/30 bg-cyan-400/10 px-4 py-4">
                    <p className="text-[11px] uppercase tracking-[0.18em] text-cyan-200">
                      Current prompt
                    </p>
                    <p className="mt-2 text-base font-semibold text-white">
                      {vaultPrompt.title}
                    </p>
                    <p className="mt-3 text-sm leading-7 text-cyan-50/90">
                      {vaultPrompt.prompt}
                    </p>
                  </div>
                ) : null
              ) : (
                <div className="rounded-[24px] border border-white/10 bg-white/5 px-4 py-4">
                  <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">
                    Current step
                  </p>
                  <p className="mt-2 text-sm leading-7 text-slate-100">
                    {readPrimaryPrompt(activeArtifact) ??
                      "The active artifact panel on the right shows the current review surface."}
                  </p>
                </div>
              )}
            </div>
          </section>

          <section className="rounded-[28px] border border-slate-200 bg-white/90 p-5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">
              Session map
            </p>
            <div className="mt-4 rounded-[20px] border border-slate-200 bg-slate-50 px-4 py-4">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Surface mode
              </p>
              <p className="mt-2 text-sm font-semibold text-slate-950">
                {surfaceMode.label}
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {surfaceMode.description}
              </p>
            </div>
            <ol
              className="mt-4 flex list-none flex-wrap gap-2 p-0"
              aria-label="Session stage history"
            >
              {session.stageHistory.map((stageKey, index) => (
                <li
                  key={`${stageKey}-${index}`}
                  aria-current={stageKey === session.stage.key ? "step" : undefined}
                  className={`rounded-full px-3 py-2 text-[11px] font-medium uppercase tracking-[0.18em] ${
                    stageKey === session.stage.key
                      ? "bg-slate-950 text-white"
                      : "border border-slate-200 bg-slate-50 text-slate-600"
                  }`}
                >
                  {stageKey}
                </li>
              ))}
            </ol>

            <dl className="mt-5 grid grid-cols-3 gap-3">
              <MetricCard
                label="Interrupt"
                value={session.stage.interruptReason}
              />
              <MetricCard
                label="Artifacts"
                value={String(session.artifactCount)}
              />
              <MetricCard
                label="Trace"
                value={String(session.traceEventCount)}
              />
            </dl>

            {(session.interruptionType || session.replanFromStage) && (
              <div className="mt-4 flex flex-wrap gap-2">
                {session.interruptionType ? (
                  <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-amber-900">
                    {session.interruptionType}
                  </span>
                ) : null}
                {session.replanFromStage ? (
                  <span className="rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-sky-900">
                    rerun from {session.replanFromStage}
                  </span>
                ) : null}
              </div>
            )}
          </section>
        </div>

        {workspaceSignals.length > 0 ? (
          <section className="mt-6 rounded-[28px] border border-slate-200 bg-white p-5 shadow-[0_18px_45px_-36px_rgba(15,23,42,0.35)]">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Runtime signals
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Progressive control surfaces stay compact by surfacing only the active route, risk, budget, and evaluation signals.
                </p>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-[11px] font-medium text-slate-600">
                {workspaceSignals.length} active
              </span>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              {workspaceSignals.map((signal) => (
                <article
                  key={signal.label}
                  className="rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-4"
                >
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                    {signal.label}
                  </p>
                  <p className="mt-2 text-sm font-semibold text-slate-950">
                    {signal.value}
                  </p>
                  <ul className="mt-3 space-y-1 text-sm leading-6 text-slate-600">
                    {signal.notes.map((note, index) => (
                      <li key={`${signal.label}-${index}`}>• {note}</li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          </section>
        ) : null}

        <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1.15fr)_minmax(240px,0.85fr)]">
          <TracePanel events={session.traceEvents} />

          <section className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-[0_18px_45px_-36px_rgba(15,23,42,0.35)]">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-950">
                Career vault
              </h3>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-[11px] font-medium text-slate-600">
                {vaultRoles.length} roles
              </span>
            </div>
            <div className="mt-4 space-y-3">
              {vaultRoles.length > 0 ? (
                vaultRoles.slice(0, 3).map((role) => (
                  <article
                    key={role.id}
                    className="rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-4"
                  >
                    <p className="text-sm font-semibold text-slate-950">
                      {role.title}
                    </p>
                    <p className="mt-1 text-sm text-slate-600">
                      {role.company.name}
                    </p>
                    <p className="mt-3 text-sm leading-6 text-slate-600">
                      {role.summary ?? "No summary yet."}
                    </p>
                  </article>
                ))
              ) : (
                <article className="rounded-[22px] border border-dashed border-slate-300 bg-slate-50 px-4 py-4 text-sm leading-7 text-slate-600">
                  No canonical roles stored yet. Use vault mode to capture one
                  story thread at a time.
                </article>
              )}
            </div>
          </section>
        </div>
      </article>

      <aside className="space-y-6">
        <ArtifactPanel
          artifact={activeArtifact}
          fallbackSummary={session.stage.summary}
          traceCount={session.traceEventCount}
          artifacts={session.artifacts}
          stageKey={session.stage.key}
          sessionId={session.id}
          workspaceMode={workspaceMode}
          surfaceMode={surfaceMode.key}
        />

        <section className="rounded-[30px] border border-slate-200/80 bg-white/96 p-6 shadow-[0_24px_80px_-42px_rgba(15,23,42,0.35)]">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-950">
              Artifact stream
            </h3>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-[11px] font-medium text-slate-600">
              {session.artifactCount}
            </span>
          </div>
          <div className="mt-4 space-y-3" aria-label="Artifact history">
            {session.artifacts
              .slice()
              .reverse()
              .map((artifact) => (
                <Link
                  key={artifact.id}
                  href={buildArtifactHref({
                    sessionId: session.id,
                    workspaceMode,
                    artifactId: artifact.id,
                  })}
                  className={`rounded-[22px] border px-4 py-4 ${
                    artifact.id === activeArtifact?.id
                      ? "border-slate-950 bg-slate-950 text-white"
                      : "border-slate-200 bg-slate-50 text-slate-900"
                  } block transition hover:-translate-y-[1px] hover:shadow-[0_16px_30px_-26px_rgba(15,23,42,0.45)]`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold">{artifact.title}</p>
                    <span
                      className={`rounded-full px-2 py-1 text-[10px] font-medium uppercase tracking-[0.18em] ${
                        artifact.id === activeArtifact?.id
                          ? "bg-white/10 text-white"
                          : "bg-white text-slate-500"
                      }`}
                    >
                      {artifact.status}
                    </span>
                  </div>
                  <p
                    className={`mt-2 text-sm leading-6 ${
                      artifact.id === activeArtifact?.id
                        ? "text-slate-100"
                        : "text-slate-600"
                    }`}
                  >
                    {artifact.summary}
                  </p>
                  <p
                    className={`mt-3 text-[11px] uppercase tracking-[0.18em] ${
                      artifact.id === activeArtifact?.id
                        ? "text-slate-300"
                        : "text-slate-500"
                    }`}
                  >
                    {artifact.kind}
                  </p>
                </Link>
              ))}
          </div>
        </section>
      </aside>
    </section>
  );
}

function determineSurfaceMode(session: SessionEnvelope) {
  const signalCount = [
    session.memoryRiskSummary,
    session.contextBudgetSummary,
    session.capabilityRouteSummary,
    session.trajectoryEvaluationSummary,
  ].filter(Boolean).length;

  if (session.stage.key === "complete" || signalCount >= 3) {
    return {
      key: "full" as const,
      label: "Full inspection",
      description:
        "Expose the full evidence, routing, and evaluation surface because the session has enough state to justify deeper review.",
    };
  }

  if (
    session.stage.key === "career_intake" ||
    session.stage.key === "blueprint_review" ||
    session.stage.key === "draft_review" ||
    signalCount >= 1
  ) {
    return {
      key: "sidecar" as const,
      label: "Sidecar review",
      description:
        "Keep the conversation central while exposing targeted controls and high-signal summaries beside the active artifact.",
    };
  }

  return {
    key: "micro" as const,
    label: "Micro intervention",
    description:
      "Keep the workspace light until the run accumulates enough evidence or risk to justify deeper controls.",
  };
}

function buildWorkspaceSignals(session: SessionEnvelope) {
  const signals: Array<{ label: string; value: string; notes: string[] }> = [];

  if (session.memoryRiskSummary) {
    signals.push({
      label: "Memory risk",
      value: `${session.memoryRiskSummary.quarantinedItems} quarantined / ${session.memoryRiskSummary.highRiskItems} high risk`,
      notes: session.memoryRiskSummary.notes,
    });
  }

  if (session.contextBudgetSummary) {
    signals.push({
      label: "Context budget",
      value: `${session.contextBudgetSummary.tokenBudget} tokens`,
      notes: session.contextBudgetSummary.notes,
    });
  }

  if (session.capabilityRouteSummary) {
    signals.push({
      label: "Capability route",
      value:
        session.capabilityRouteSummary.selectedCapability ?? "No route selected",
      notes: session.capabilityRouteSummary.notes,
    });
  }

  if (session.trajectoryEvaluationSummary) {
    signals.push({
      label: "Trajectory evaluation",
      value: [
        session.trajectoryEvaluationSummary.questionQuality,
        session.trajectoryEvaluationSummary.actionEfficiency,
        session.trajectoryEvaluationSummary.revisionEfficiency,
      ]
        .filter(Boolean)
        .join(" / "),
      notes: session.trajectoryEvaluationSummary.notes,
    });
  }

  return signals;
}

function buildArtifactHref({
  sessionId,
  workspaceMode,
  artifactId,
}: {
  sessionId: string;
  workspaceMode: "resume" | "vault";
  artifactId: string;
}) {
  const params = new URLSearchParams({ sessionId, artifactId });
  if (workspaceMode === "vault") {
    params.set("mode", "vault");
  }
  return `/workspace?${params.toString()}`;
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[20px] border border-slate-200 bg-slate-50 px-4 py-4">
      <dt className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        {label}
      </dt>
      <dd className="mt-2 text-sm font-semibold text-slate-950">{value}</dd>
    </div>
  );
}

function readPrimaryPrompt(
  artifact: SessionEnvelope["artifacts"][number] | null,
) {
  if (!artifact) {
    return null;
  }

  return typeof artifact.payload.prompt === "string"
    ? artifact.payload.prompt
    : null;
}
