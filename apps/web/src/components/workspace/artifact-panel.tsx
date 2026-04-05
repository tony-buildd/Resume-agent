import type { RuntimeArtifact, StageKey } from "@/lib/api/sessions";


type ArtifactPanelProps = {
  artifact: RuntimeArtifact | null;
  fallbackSummary: string;
  traceCount: number;
};

const stageArtifactPriority: Partial<Record<StageKey, string[]>> = {
  vault_seed_import: ["vault-question"],
  vault_role_interview: ["vault-question"],
  vault_story_checkpoint: ["vault-checkpoint", "vault-role-record"],
  jd_intake: ["question"],
  jd_analysis_review: ["jd-analysis", "research-summary"],
  career_intake: ["interrogation-question", "session-context"],
  blueprint_review: ["blueprint", "session-context"],
  draft_review: ["draft-package", "evaluation-scorecard"],
  complete: ["draft-package", "evaluation-scorecard", "blueprint"],
};

export function ArtifactPanel({
  artifact,
  fallbackSummary,
  traceCount,
}: ArtifactPanelProps) {
  return (
    <section className="rounded-[30px] border border-slate-200/80 bg-white/96 p-6 shadow-[0_24px_80px_-42px_rgba(15,23,42,0.4)]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">
            Context panel
          </p>
          <h3 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
            {artifact?.title ?? "No active artifact selected"}
          </h3>
        </div>
        <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.2em] text-slate-600">
          {artifact?.kind ?? `${traceCount} traces`}
        </span>
      </div>

      <p className="mt-3 text-sm leading-7 text-slate-600">
        {artifact?.summary ?? fallbackSummary}
      </p>

      <div className="mt-5 rounded-[24px] border border-slate-200 bg-slate-50/90 p-4">
        {artifact ? <ArtifactPayload artifact={artifact} /> : <EmptyPanel />}
      </div>
    </section>
  );
}


export function selectActiveArtifact(
  artifacts: RuntimeArtifact[],
  stageKey: StageKey,
): RuntimeArtifact | null {
  const priorities = stageArtifactPriority[stageKey] ?? [];
  for (const kind of priorities) {
    const artifact = [...artifacts].reverse().find((item) => item.kind === kind);
    if (artifact) {
      return artifact;
    }
  }

  return artifacts.at(-1) ?? null;
}


function ArtifactPayload({ artifact }: { artifact: RuntimeArtifact }) {
  switch (artifact.kind) {
    case "jd-analysis":
      return <JDAnalysisPayload artifact={artifact} />;
    case "research-summary":
      return <ResearchSummaryPayload artifact={artifact} />;
    case "interrogation-question":
    case "question":
    case "vault-question":
      return <PromptPayload artifact={artifact} />;
    case "blueprint":
      return <BlueprintPayload artifact={artifact} />;
    case "draft-package":
      return <DraftPackagePayload artifact={artifact} />;
    case "evaluation-scorecard":
      return <ScorecardPayload artifact={artifact} />;
    default:
      return <GenericPayload artifact={artifact} />;
  }
}


function JDAnalysisPayload({ artifact }: { artifact: RuntimeArtifact }) {
  const analysis = readObject(artifact.payload.analysis);
  const requirements = readStringArray(analysis?.topRequirements);
  const repeatingTerms = readStringArray(analysis?.repeatingTerms);

  return (
    <div className="space-y-4">
      <MetricRow
        label="Primary focus"
        value={readString(analysis?.primaryFocus) ?? "Unavailable"}
      />
      <MetricRow
        label="Engineering archetype"
        value={readString(analysis?.engineeringArchetype) ?? "Unavailable"}
      />
      <TagList label="Top requirements" values={requirements} />
      <TagList label="Repeating terms" values={repeatingTerms} tone="slate" />
    </div>
  );
}


function ResearchSummaryPayload({ artifact }: { artifact: RuntimeArtifact }) {
  const research = readObject(artifact.payload.research);
  return (
    <div className="space-y-4">
      <MetricRow
        label="Strategic summary"
        value={readString(research?.strategicSummary) ?? "Unavailable"}
      />
      <TagList
        label="Market signals"
        values={readStringArray(research?.marketSignals)}
        tone="cyan"
      />
      <TagList
        label="Source notes"
        values={readStringArray(research?.sourceNotes)}
        tone="amber"
      />
    </div>
  );
}


function PromptPayload({ artifact }: { artifact: RuntimeArtifact }) {
  return (
    <div className="space-y-4">
      <blockquote className="rounded-[20px] border border-slate-200 bg-white px-4 py-3 text-sm leading-7 text-slate-800">
        {readString(artifact.payload.prompt) ?? "Prompt unavailable."}
      </blockquote>
      {typeof artifact.payload.whyItMatters === "string" ? (
        <MetricRow label="Why it matters" value={artifact.payload.whyItMatters} />
      ) : null}
    </div>
  );
}


function BlueprintPayload({ artifact }: { artifact: RuntimeArtifact }) {
  const blueprint = readObject(artifact.payload.blueprint);
  const selectedRoles = Array.isArray(blueprint?.selectedRoles)
    ? blueprint.selectedRoles
    : [];
  return (
    <div className="space-y-4">
      <MetricRow
        label="Narrative angle"
        value={readString(blueprint?.narrativeAngle) ?? "Unavailable"}
      />
      <TagList
        label="Skills focus"
        values={readStringArray(blueprint?.skillsFocus)}
        tone="emerald"
      />
      <div className="space-y-3">
        {selectedRoles.slice(0, 2).map((role, index) => {
          const roleData = readObject(role);
          const bullets = Array.isArray(roleData?.selectedBullets)
            ? roleData.selectedBullets
            : [];
          return (
            <article
              key={`${readString(roleData?.roleId) ?? "role"}-${index}`}
              className="rounded-[20px] border border-slate-200 bg-white px-4 py-4"
            >
              <p className="text-sm font-semibold text-slate-950">
                {readString(roleData?.roleTitle) ?? "Role"} ·{" "}
                {readString(roleData?.companyName) ?? "Company"}
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {readString(roleData?.whySelected) ?? "Selection rationale unavailable."}
              </p>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
                {bullets.slice(0, 3).map((bullet, bulletIndex) => {
                  const bulletData = readObject(bullet);
                  return (
                    <li key={`${index}-${bulletIndex}`} className="rounded-2xl bg-slate-50 px-3 py-2">
                      {readString(bulletData?.text) ?? "Bullet unavailable"}
                    </li>
                  );
                })}
              </ul>
            </article>
          );
        })}
      </div>
    </div>
  );
}


function DraftPackagePayload({ artifact }: { artifact: RuntimeArtifact }) {
  const markdown = readString(artifact.payload.markdownResume);
  const talkingPoints = readStringArrayFromObjects(artifact.payload.talkingPoints, "prompt");
  return (
    <div className="space-y-4">
      <div className="rounded-[20px] border border-slate-200 bg-white px-4 py-4">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
          Resume preview
        </p>
        <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-xs leading-6 text-slate-800">
          {markdown ?? "Markdown draft unavailable."}
        </pre>
      </div>
      <TagList label="Talking points" values={talkingPoints} tone="amber" />
    </div>
  );
}


function ScorecardPayload({ artifact }: { artifact: RuntimeArtifact }) {
  const metrics = [
    ["Fit", readObject(artifact.payload.fit)],
    ["Evidence", readObject(artifact.payload.evidenceSupport)],
    ["Specificity", readObject(artifact.payload.specificity)],
    ["Risk", readObject(artifact.payload.overstatementRisk)],
  ] as const;

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        {metrics.map(([label, value]) => (
          <article
            key={label}
            className="rounded-[20px] border border-slate-200 bg-white px-4 py-4"
          >
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              {label}
            </p>
            <p className="mt-2 text-2xl font-semibold text-slate-950">
              {readNumber(value?.score) ?? "-"}
              <span className="ml-1 text-sm font-medium text-slate-500">/5</span>
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {readString(value?.rationale) ?? "No rationale available."}
            </p>
          </article>
        ))}
      </div>
      <MetricRow
        label="Revision summary"
        value={readString(artifact.payload.revisionSummary) ?? "No summary available."}
      />
    </div>
  );
}


function GenericPayload({ artifact }: { artifact: RuntimeArtifact }) {
  return (
    <div className="grid gap-3">
      {Object.entries(artifact.payload).map(([key, value]) => (
        <div
          key={key}
          className="rounded-[18px] border border-slate-200 bg-white px-4 py-3"
        >
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            {key}
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {renderValue(value)}
          </p>
        </div>
      ))}
    </div>
  );
}


function EmptyPanel() {
  return (
    <div className="rounded-[18px] border border-dashed border-slate-300 bg-white px-4 py-5 text-sm leading-7 text-slate-600">
      The contextual artifact panel will populate automatically when the active stage produces a typed artifact.
    </div>
  );
}


function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[18px] border border-slate-200 bg-white px-4 py-3">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-sm leading-6 text-slate-800">{value}</p>
    </div>
  );
}


function TagList({
  label,
  values,
  tone = "emerald",
}: {
  label: string;
  values: string[];
  tone?: "emerald" | "cyan" | "amber" | "slate";
}) {
  const tones = {
    emerald: "border-emerald-200 bg-emerald-50 text-emerald-900",
    cyan: "border-cyan-200 bg-cyan-50 text-cyan-900",
    amber: "border-amber-200 bg-amber-50 text-amber-900",
    slate: "border-slate-200 bg-slate-100 text-slate-700",
  };
  return (
    <div className="rounded-[18px] border border-slate-200 bg-white px-4 py-3">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        {label}
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {values.length > 0 ? (
          values.map((value) => (
            <span
              key={value}
              className={`rounded-full border px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] ${tones[tone]}`}
            >
              {value}
            </span>
          ))
        ) : (
          <span className="text-sm text-slate-500">No items yet.</span>
        )}
      </div>
    </div>
  );
}


function readObject(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}


function readString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}


function readNumber(value: unknown): number | null {
  return typeof value === "number" ? value : null;
}


function readStringArray(value: unknown): string[] {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === "string")
    : [];
}


function readStringArrayFromObjects(value: unknown, key: string): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((item) => readObject(item)?.[key])
    .filter((item): item is string => typeof item === "string");
}


function renderValue(value: unknown): string {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => renderValue(item)).join(", ");
  }
  if (value && typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }
  return "Unavailable";
}
