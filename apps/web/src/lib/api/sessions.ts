import "server-only";

import { auth, currentUser } from "@clerk/nextjs/server";

export type StageKey =
  | "bootstrap"
  | "vault_seed_import"
  | "vault_role_interview"
  | "vault_story_checkpoint"
  | "jd_intake"
  | "jd_analysis_review"
  | "career_intake"
  | "blueprint_review"
  | "draft_review"
  | "complete";

export type StageStatus = "pending" | "running" | "interrupted" | "complete";

export interface RuntimeStage {
  key: StageKey;
  label: string;
  status: StageStatus;
  summary: string;
  interruptReason: string;
  canResume: boolean;
  updatedAt: string;
}

export interface RuntimeArtifact {
  id: string;
  kind: string;
  status: string;
  title: string;
  summary: string;
  payload: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface RuntimeTraceEvent {
  id: string;
  stage: StageKey;
  level: string;
  message: string;
  payload: Record<string, unknown>;
  createdAt: string;
}

export interface SessionEnvelope {
  id: string;
  userId: string;
  clerkUserId: string;
  title: string | null;
  status: string;
  stage: RuntimeStage;
  stageHistory: StageKey[];
  artifactCount: number;
  traceEventCount: number;
  artifacts: RuntimeArtifact[];
  traceEvents: RuntimeTraceEvent[];
  createdAt: string;
  updatedAt: string;
}

export interface AdvanceSessionResponse {
  transition: string;
  interrupted: boolean;
  envelope: SessionEnvelope;
}

export interface AdvanceSessionPayload {
  answer?: string;
  approveJdAnalysis?: boolean;
  approveBlueprint?: boolean;
  approveCheckpoint?: boolean;
  acceptDraftReview?: boolean;
  requestRevision?: boolean;
}

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

function getApiBaseUrl() {
  return (
    process.env.RESUME_AGENT_API_URL ??
    process.env.NEXT_PUBLIC_RESUME_AGENT_API_URL ??
    DEFAULT_API_BASE_URL
  );
}

async function buildAuthHeaders() {
  const { userId } = await auth();
  const user = await currentUser();

  if (!userId) {
    throw new Error("Authenticated session required before calling the API.");
  }

  return {
    "Content-Type": "application/json",
    "X-Clerk-User-Id": userId,
    "X-Clerk-User-Email": user?.primaryEmailAddress?.emailAddress ?? "",
  };
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      ...(await buildAuthHeaders()),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API request failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as T;
}

export async function createSession(
  title = "Workspace bootstrap",
): Promise<SessionEnvelope> {
  return apiFetch<SessionEnvelope>("/api/sessions", {
    method: "POST",
    body: JSON.stringify({
      title,
      stage: "bootstrap",
    }),
  });
}

export async function getSession(sessionId: string): Promise<SessionEnvelope> {
  return apiFetch<SessionEnvelope>(`/api/sessions/${sessionId}`);
}

export async function advanceSession(
  sessionId: string,
  payload: AdvanceSessionPayload,
): Promise<AdvanceSessionResponse> {
  return apiFetch<AdvanceSessionResponse>(
    `/api/sessions/${sessionId}/advance`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}
