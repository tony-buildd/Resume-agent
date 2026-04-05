import { redirect } from "next/navigation";

import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import { createSession, getSession } from "@/lib/api/sessions";
import {
  createVaultInterviewSession,
  listVaultRoles,
  type StoryCheckpointRecord,
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
      vaultRoles: Awaited<ReturnType<typeof listVaultRoles>>;
      workspaceMode: WorkspaceMode;
    }
  | {
      kind: "error";
      message: string;
    };


export default async function WorkspacePage({
  searchParams,
}: WorkspacePageProps) {
  const { mode, sessionId } = await searchParams;
  const workspaceState = await loadWorkspaceState(
    sessionId,
    parseWorkspaceMode(mode),
  );

  if (workspaceState.kind === "error") {
    return (
      <section className="rounded-[30px] border border-rose-200 bg-rose-50 p-6 text-rose-950 shadow-[0_24px_80px_-48px_rgba(15,23,42,0.25)]">
        <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-rose-700">
          Workspace unavailable
        </p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight">
          The session workspace could not load
        </h2>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-rose-900/80">
          {workspaceState.message}
        </p>
        <p className="mt-4 text-sm leading-7 text-rose-900/80">
          Verify Clerk env vars, `RESUME_AGENT_API_URL`, and `DATABASE_URL`, then
          reload the workspace.
        </p>
      </section>
    );
  }

  const { session, vaultRoles, workspaceMode } = workspaceState;

  return (
    <WorkspaceShell
      session={session}
      vaultRoles={vaultRoles}
      workspaceMode={workspaceMode}
      vaultPrompt={readVaultPrompt(session.artifacts)}
      vaultCheckpoint={readVaultCheckpoint(session.artifacts)}
    />
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
