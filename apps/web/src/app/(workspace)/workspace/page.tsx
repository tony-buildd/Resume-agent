import { redirect } from "next/navigation";

import { createSession, getSession } from "@/lib/api/sessions";
import {
  createVaultInterviewSession,
  listVaultRoles,
  type StoryCheckpointRecord,
  type VaultRoleRecord,
} from "@/lib/api/vault";


type WorkspacePageProps = {
  searchParams: Promise<{
    mode?: string;
    sessionId?: string;
  }>;
};

type WorkspaceMode = "resume" | "vault";

type WorkspaceState =
  | {
      kind: "ready";
      session: Awaited<ReturnType<typeof getSession>>;
      vaultRoles: VaultRoleRecord[];
      workspaceMode: WorkspaceMode;
    }
  | {
      kind: "error";
      message: string;
    };


const statusStyles: Record<string, string> = {
  interrupted: "bg-amber-100 text-amber-900",
  running: "bg-sky-100 text-sky-900",
  complete: "bg-emerald-100 text-emerald-900",
  draft: "bg-slate-200 text-slate-800",
};


export default async function WorkspacePage({
  searchParams,
}: WorkspacePageProps) {
  const { mode, sessionId } = await searchParams;

  const workspaceState = await loadWorkspaceState(sessionId, parseWorkspaceMode(mode));

  if (workspaceState.kind === "error") {
    return (
      <section className="rounded-[28px] border border-rose-200 bg-rose-50 p-6 text-rose-950 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.25)]">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-rose-700">
          Workspace unavailable
        </p>
        <h2 className="mt-3 text-2xl font-semibold tracking-tight">
          API-backed session state is not reachable yet
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-rose-900/80">
          {workspaceState.message}
        </p>
        <p className="mt-4 text-sm leading-7 text-rose-900/80">
          Finish the external setup by adding Clerk keys, setting
          `RESUME_AGENT_API_URL` if needed, and pointing `DATABASE_URL` at a
          reachable Postgres instance.
        </p>
      </section>
    );
  }

  const { session, vaultRoles, workspaceMode } = workspaceState;
  const statusClass =
    statusStyles[session.status] ?? "bg-slate-200 text-slate-800";
  const vaultPrompt = readVaultPrompt(session.artifacts);
  const vaultCheckpoint = readVaultCheckpoint(session.artifacts);
  const isVaultWorkspace =
    workspaceMode === "vault" || session.stage.key.startsWith("vault_");

  return (
    <section className="grid gap-5 lg:grid-cols-[1.3fr_0.95fr]">
      <article className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.45)]">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
              Runtime session
            </p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">
              {session.stage.label}
            </h2>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              {session.stage.summary}
            </p>
            {isVaultWorkspace ? (
              <p className="mt-3 inline-flex rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-900">
                Career vault mode
              </p>
            ) : null}
          </div>
          <div className="flex flex-col items-start gap-2">
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${statusClass}`}
            >
              {session.status}
            </span>
            <code className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600">
              {session.id}
            </code>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Interrupt reason
            </p>
            <p className="mt-2 text-sm text-slate-900">
              {session.stage.interruptReason}
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Artifacts
            </p>
            <p className="mt-2 text-sm text-slate-900">
              {session.artifactCount}
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Trace events
            </p>
            <p className="mt-2 text-sm text-slate-900">
              {session.traceEventCount}
            </p>
          </div>
        </div>

        {isVaultWorkspace ? (
          <section className="mt-6 rounded-[24px] border border-cyan-200 bg-cyan-50/70 p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-700">
                  Vault ingestion surface
                </p>
                <h3 className="mt-2 text-lg font-semibold text-slate-950">
                  Focus one story thread at a time
                </h3>
              </div>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-cyan-800">
                {vaultCheckpoint ? "checkpoint ready" : "awaiting input"}
              </span>
            </div>

            {vaultCheckpoint ? (
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-cyan-200 bg-white px-4 py-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">
                    Story checkpoint
                  </p>
                  <p className="mt-2 text-base font-semibold text-slate-950">
                    {vaultCheckpoint.storyName}
                  </p>
                  <p className="mt-1 text-sm text-slate-600">
                    Role: {vaultCheckpoint.roleTitle}
                  </p>
                  <dl className="mt-4 grid grid-cols-3 gap-3 text-sm text-slate-700">
                    <div>
                      <dt className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                        Facts
                      </dt>
                      <dd className="mt-1 font-semibold text-slate-950">
                        {vaultCheckpoint.totalFacts}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                        Draft ready
                      </dt>
                      <dd className="mt-1 font-semibold text-slate-950">
                        {vaultCheckpoint.draftEligibleFacts}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                        Pending review
                      </dt>
                      <dd className="mt-1 font-semibold text-slate-950">
                        {vaultCheckpoint.pendingReviewFacts}
                      </dd>
                    </div>
                  </dl>
                </div>

                <div className="rounded-2xl border border-cyan-200 bg-white px-4 py-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">
                    Next signal
                  </p>
                  <p className="mt-2 text-sm leading-6 text-slate-700">
                    {vaultCheckpoint.suggestedNextQuestion}
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {vaultCheckpoint.missingSignals.length > 0 ? (
                      vaultCheckpoint.missingSignals.map((signal) => (
                        <span
                          key={signal}
                          className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-amber-900"
                        >
                          {signal}
                        </span>
                      ))
                    ) : (
                      <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-emerald-900">
                        coherent for review
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ) : vaultPrompt ? (
              <article className="mt-4 rounded-2xl border border-cyan-200 bg-white px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">
                  Current vault prompt
                </p>
                <p className="mt-2 text-sm font-semibold text-slate-950">
                  {vaultPrompt.title}
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {vaultPrompt.summary}
                </p>
                <p className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-800">
                  {vaultPrompt.prompt}
                </p>
              </article>
            ) : (
              <p className="mt-4 text-sm leading-6 text-slate-600">
                Start the workspace with <code>?mode=vault</code> to create a
                focused vault interview session, or continue a saved vault
                session with its <code>sessionId</code>.
              </p>
            )}
          </section>
        ) : null}

        <div className="mt-6 rounded-[24px] border border-slate-200 bg-slate-950 p-5 text-slate-50">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
            Stage history
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            {session.stageHistory.map((stageKey) => (
              <span
                key={stageKey}
                className="rounded-full border border-slate-700 px-3 py-2 text-xs uppercase tracking-[0.18em] text-slate-200"
              >
                {stageKey}
              </span>
            ))}
          </div>
        </div>
      </article>

      <aside className="grid gap-5">
        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.35)]">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-950">
              Career vault
            </h3>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              {vaultRoles.length} roles
            </span>
          </div>
          <div className="mt-4 space-y-3">
            {vaultRoles.length > 0 ? (
              vaultRoles.slice(0, 4).map((role) => (
                <article
                  key={role.id}
                  className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-950">
                        {role.title}
                      </p>
                      <p className="mt-1 text-sm text-slate-600">
                        {role.company.name}
                      </p>
                    </div>
                    <span className="rounded-full bg-white px-2 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-slate-500">
                      {role.projectStories.length} stories
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    {role.summary ?? "No role summary yet."}
                  </p>
                </article>
              ))
            ) : (
              <article className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-4">
                <p className="text-sm font-semibold text-slate-900">
                  No canonical roles stored yet
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Use the vault interview flow to capture one project thread,
                  review it, then persist it into the long-term vault.
                </p>
              </article>
            )}
          </div>
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.35)]">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-950">
              Persisted artifacts
            </h3>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              {session.artifactCount}
            </span>
          </div>
          <div className="mt-4 space-y-3">
            {session.artifacts.map((artifact) => (
              <article
                key={artifact.id}
                className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-slate-900">
                    {artifact.title}
                  </p>
                  <span className="rounded-full bg-white px-2 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-slate-500">
                    {artifact.status}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {artifact.summary}
                </p>
                <p className="mt-3 text-xs uppercase tracking-[0.18em] text-slate-500">
                  {artifact.kind}
                </p>
              </article>
            ))}
          </div>
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.35)]">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-950">
              Trace stream
            </h3>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              API-backed
            </span>
          </div>
          <div className="mt-4 space-y-3">
            {session.traceEvents.map((event) => (
              <article
                key={event.id}
                className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                    {event.stage}
                  </p>
                  <span className="text-xs text-slate-500">{event.level}</span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-800">
                  {event.message}
                </p>
              </article>
            ))}
          </div>
        </section>
      </aside>
    </section>
  );
}


function parseWorkspaceMode(mode: string | undefined): WorkspaceMode {
  return mode === "vault" ? "vault" : "resume";
}


async function loadWorkspaceState(
  sessionId: string | undefined,
  workspaceMode: WorkspaceMode,
): Promise<WorkspaceState> {
  try {
    if (!sessionId) {
      const created =
        workspaceMode === "vault"
          ? await createVaultInterviewSession()
          : await createSession();
      const params = new URLSearchParams({ sessionId: created.id });
      if (workspaceMode === "vault") {
        params.set("mode", "vault");
      }
      redirect(`/workspace?${params.toString()}`);
    }

    const [session, vaultRoles] = await Promise.all([
      getSession(sessionId),
      listVaultRoles(),
    ]);

    return {
      kind: "ready",
      session,
      vaultRoles,
      workspaceMode,
    };
  } catch (error) {
    return {
      kind: "error",
      message:
        error instanceof Error ? error.message : "Unknown workspace error",
    };
  }
}


function readVaultPrompt(
  artifacts: Awaited<ReturnType<typeof getSession>>["artifacts"],
) {
  const artifact = artifacts.find((item) => item.kind === "vault-question");

  if (!artifact) {
    return null;
  }

  const prompt =
    typeof artifact.payload.prompt === "string" ? artifact.payload.prompt : null;

  if (!prompt) {
    return null;
  }

  return {
    title: artifact.title,
    summary: artifact.summary,
    prompt,
  };
}


function readVaultCheckpoint(
  artifacts: Awaited<ReturnType<typeof getSession>>["artifacts"],
): StoryCheckpointRecord | null {
  const artifact = artifacts.find((item) => item.kind === "vault-checkpoint");
  const checkpoint = artifact?.payload.checkpoint;

  if (!checkpoint || typeof checkpoint !== "object") {
    return null;
  }

  const candidate = checkpoint as Partial<StoryCheckpointRecord>;

  if (
    typeof candidate.roleTitle !== "string" ||
    typeof candidate.storyName !== "string" ||
    typeof candidate.totalFacts !== "number" ||
    typeof candidate.draftEligibleFacts !== "number" ||
    typeof candidate.pendingReviewFacts !== "number" ||
    typeof candidate.suggestedNextQuestion !== "string" ||
    !Array.isArray(candidate.missingSignals)
  ) {
    return null;
  }

  return {
    roleTitle: candidate.roleTitle,
    storyName: candidate.storyName,
    totalFacts: candidate.totalFacts,
    draftEligibleFacts: candidate.draftEligibleFacts,
    pendingReviewFacts: candidate.pendingReviewFacts,
    suggestedNextQuestion: candidate.suggestedNextQuestion,
    missingSignals: candidate.missingSignals.filter(
      (signal): signal is string => typeof signal === "string",
    ),
  };
}
