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
    case "add-requirement":
      return {
        interruptionType: "add_requirement" as const,
        interruptionNote: "User requested an additional requirement to be reflected.",
      };
    case "revise-requirement":
      return {
        interruptionType: "revise_requirement" as const,
        interruptionNote: "User requested the requirement framing to change.",
      };
    case "retract-requirement":
      return {
        interruptionType: "retract_requirement" as const,
        interruptionNote: "User requested a previously implied requirement to be removed.",
      };
    case "approve-blueprint":
      return { approveBlueprint: true };
    case "clarify-fact":
      return {
        interruptionType: "clarify_fact" as const,
        interruptionNote: "User requested a tighter evidence check before continuing.",
      };
    case "risk-flag":
      return {
        interruptionType: "risk_flag" as const,
        interruptionNote: "User marked the current evidence or phrasing as risky.",
      };
    case "narrow-narrative":
      return {
        interruptionType: "revise_requirement" as const,
        interruptionNote: "User requested a narrower narrative scope for the draft.",
      };
    case "broaden-narrative":
      return {
        interruptionType: "revise_requirement" as const,
        interruptionNote: "User requested a broader narrative scope for the draft.",
      };
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
