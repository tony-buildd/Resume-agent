import { submitWorkspaceReview } from "@/app/(workspace)/workspace/actions";
import type { StageKey } from "@/lib/api/sessions";

type ReviewActionsProps = {
  stageKey: StageKey;
  sessionId: string;
  workspaceMode: "resume" | "vault";
};

export function ReviewActions({
  stageKey,
  sessionId,
  workspaceMode,
}: ReviewActionsProps) {
  const actions = buildActions(stageKey);

  if (actions.length === 0) {
    return null;
  }

  return (
    <section className="mt-5 rounded-[24px] border border-slate-200 bg-white px-4 py-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            Review actions
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Advance the active stage directly from this panel.
          </p>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        {actions.map((action) => (
          <form key={action.value} action={submitWorkspaceReview}>
            <input type="hidden" name="sessionId" value={sessionId} />
            <input type="hidden" name="mode" value={workspaceMode} />
            <input type="hidden" name="reviewAction" value={action.value} />
            <button
              type="submit"
              aria-label={action.label}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                action.tone === "primary"
                  ? "bg-slate-950 text-white hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2"
                  : action.tone === "accent"
                    ? "bg-amber-100 text-amber-950 hover:bg-amber-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-300 focus-visible:ring-offset-2"
                    : "border border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-300 focus-visible:ring-offset-2"
              }`}
            >
              {action.label}
            </button>
          </form>
        ))}
      </div>
    </section>
  );
}

function buildActions(stageKey: StageKey) {
  switch (stageKey) {
    case "jd_analysis_review":
      return [
        {
          value: "approve-jd-analysis",
          label: "Approve analysis",
          tone: "primary" as const,
        },
      ];
    case "vault_story_checkpoint":
      return [
        {
          value: "approve-checkpoint",
          label: "Approve checkpoint",
          tone: "primary" as const,
        },
      ];
    case "blueprint_review":
      return [
        {
          value: "approve-blueprint",
          label: "Approve blueprint",
          tone: "primary" as const,
        },
      ];
    case "draft_review":
      return [
        {
          value: "accept-draft-review",
          label: "Accept draft",
          tone: "primary" as const,
        },
        {
          value: "request-revision",
          label: "Request revision",
          tone: "accent" as const,
        },
      ];
    default:
      return [];
  }
}
