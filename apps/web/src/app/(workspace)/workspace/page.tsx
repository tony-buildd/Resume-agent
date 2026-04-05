import { redirect } from "next/navigation";

import { createSession, getSession } from "@/lib/api/sessions";


type WorkspacePageProps = {
  searchParams: Promise<{
    sessionId?: string;
  }>;
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
  const { sessionId } = await searchParams;

  try {
    if (!sessionId) {
      const created = await createSession();
      redirect(`/workspace?sessionId=${created.id}`);
    }

    const session = await getSession(sessionId);
    const statusClass =
      statusStyles[session.status] ?? "bg-slate-200 text-slate-800";

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
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown workspace error";

    return (
      <section className="rounded-[28px] border border-rose-200 bg-rose-50 p-6 text-rose-950 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.25)]">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-rose-700">
          Workspace unavailable
        </p>
        <h2 className="mt-3 text-2xl font-semibold tracking-tight">
          API-backed session state is not reachable yet
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-rose-900/80">
          {message}
        </p>
        <p className="mt-4 text-sm leading-7 text-rose-900/80">
          Finish the external setup by adding Clerk keys, setting
          `RESUME_AGENT_API_URL` if needed, and pointing `DATABASE_URL` at a
          reachable Postgres instance.
        </p>
      </section>
    );
  }
}
