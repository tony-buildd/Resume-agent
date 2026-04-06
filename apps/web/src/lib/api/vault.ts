import "server-only";

import { auth, currentUser } from "@clerk/nextjs/server";

import type { SessionEnvelope } from "@/lib/api/sessions";

export interface VaultFactRecord {
  id: string;
  kind: string;
  statement: string;
  evidence: string | null;
  sourceType: string;
  reviewState: string;
  draftEligible: boolean;
  details: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface VaultBulletCandidateRecord {
  id: string;
  text: string;
  storyAngle: string | null;
  sourceType: string;
  reviewState: string;
  draftEligible: boolean;
  supportingFactIds: string[];
  details: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface VaultProjectStoryRecord {
  id: string;
  name: string;
  summary: string | null;
  stackSummary: string | null;
  impactSummary: string | null;
  sourceType: string;
  reviewState: string;
  draftEligible: boolean;
  details: Record<string, unknown>;
  facts: VaultFactRecord[];
  bulletCandidates: VaultBulletCandidateRecord[];
  createdAt: string;
  updatedAt: string;
}

export interface VaultCompanyRecord {
  id: string;
  name: string;
  domain: string | null;
  summary: string | null;
  details: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface VaultRoleRecord {
  id: string;
  title: string;
  startDate: string | null;
  endDate: string | null;
  location: string | null;
  employmentType: string | null;
  summary: string | null;
  details: Record<string, unknown>;
  company: VaultCompanyRecord;
  roleFacts: VaultFactRecord[];
  roleBulletCandidates: VaultBulletCandidateRecord[];
  projectStories: VaultProjectStoryRecord[];
  createdAt: string;
  updatedAt: string;
}

export interface StoryCheckpointRecord {
  roleTitle: string;
  storyName: string;
  totalFacts: number;
  draftEligibleFacts: number;
  pendingReviewFacts: number;
  suggestedNextQuestion: string;
  missingSignals: string[];
}

export interface VaultIngestionResponse {
  mode: string;
  role: VaultRoleRecord;
  checkpoint: StoryCheckpointRecord;
}

export interface VaultSemanticMatchRecord {
  id: string;
  document: string;
  metadata: Record<string, unknown>;
  distance: number | null;
}

export interface VaultRetrievalResponse {
  query: string | null;
  draftSafeRoles: VaultRoleRecord[];
  questioningSafeRoles: VaultRoleRecord[];
  semanticMatches: VaultSemanticMatchRecord[];
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

export async function listVaultRoles(): Promise<VaultRoleRecord[]> {
  return apiFetch<VaultRoleRecord[]>("/api/vault/roles");
}

export async function createVaultInterviewSession(input?: {
  companyName?: string;
  title?: string;
  storyName?: string;
  roleSummary?: string;
  stackSummary?: string;
  impactSummary?: string;
}): Promise<SessionEnvelope> {
  return apiFetch<SessionEnvelope>("/api/vault/interview-sessions", {
    method: "POST",
    body: JSON.stringify({
      companyName: input?.companyName ?? "Tesla",
      title: input?.title ?? "Software Engineer",
      storyName: input?.storyName ?? "Invoice validation flow",
      roleSummary: input?.roleSummary ?? "Focused on automation systems",
      stackSummary: input?.stackSummary ?? "Python, LLM, internal APIs",
      impactSummary: input?.impactSummary ?? "Pending validation",
    }),
  });
}

export async function retrieveVaultContext(input?: {
  query?: string;
  limit?: number;
  includeSemantic?: boolean;
}): Promise<VaultRetrievalResponse> {
  return apiFetch<VaultRetrievalResponse>("/api/vault/retrieval", {
    method: "POST",
    body: JSON.stringify({
      query: input?.query ?? null,
      limit: input?.limit ?? 5,
      includeSemantic: input?.includeSemantic ?? true,
    }),
  });
}
