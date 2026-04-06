"use server";

import { redirect } from "next/navigation";

import { advanceSession } from "@/lib/api/sessions";

export async function submitWorkspaceReview(formData: FormData) {
  const sessionId = String(formData.get("sessionId") ?? "").trim();
  const mode = String(formData.get("mode") ?? "resume").trim();
  const action = String(formData.get("reviewAction") ?? "").trim();

  if (!sessionId || !action) {
    return;
  }

  const payload = buildAdvancePayload(action);
  if (!payload) {
    return;
  }

  await advanceSession(sessionId, payload);

  const params = new URLSearchParams({ sessionId });
  if (mode === "vault") {
    params.set("mode", "vault");
  }
  redirect(`/workspace?${params.toString()}`);
}

function buildAdvancePayload(action: string) {
  switch (action) {
    case "approve-jd-analysis":
      return { approveJdAnalysis: true };
    case "approve-blueprint":
      return { approveBlueprint: true };
    case "accept-draft-review":
      return { acceptDraftReview: true };
    case "request-revision":
      return { requestRevision: true };
    case "approve-checkpoint":
      return { approveCheckpoint: true };
    default:
      return null;
  }
}
