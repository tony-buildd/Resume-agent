import type { RuntimeTraceEvent } from "@/lib/api/sessions";


type TracePanelProps = {
  events: RuntimeTraceEvent[];
};

export function TracePanel({ events }: TracePanelProps) {
  const recent = events.slice(-4).reverse();
  const infoCount = events.filter((event) => event.level === "info").length;
  const warningCount = events.filter((event) => event.level === "warning").length;
  const errorCount = events.filter((event) => event.level === "error").length;

  return (
    <section className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-[0_18px_45px_-36px_rgba(15,23,42,0.35)]">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-950">Trace summary</h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            Read the latest orchestration moves at a glance, then expand for the full event stream.
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-[11px] font-medium text-slate-600">
          {events.length} events
        </span>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <MetricCard label="Info" value={String(infoCount)} tone="slate" />
        <MetricCard label="Warnings" value={String(warningCount)} tone="amber" />
        <MetricCard label="Errors" value={String(errorCount)} tone="rose" />
      </div>

      <div className="mt-4 space-y-3">
        {recent.map((event) => (
          <article
            key={event.id}
            className="rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-4"
          >
            <div className="flex items-center justify-between gap-3">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                {event.stage}
              </p>
              <span className={levelPillClass(event.level)}>{event.level}</span>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-800">{event.message}</p>
          </article>
        ))}
      </div>

      <details className="mt-5 rounded-[24px] border border-slate-200 bg-slate-50/80 px-4 py-4">
        <summary className="cursor-pointer list-none text-sm font-semibold text-slate-900 outline-none marker:hidden focus-visible:ring-2 focus-visible:ring-slate-300">
          Expand debug detail
        </summary>
        <div className="mt-4 space-y-3">
          {events
            .slice()
            .reverse()
            .map((event) => (
              <article
                key={`${event.id}-detail`}
                className="rounded-[20px] border border-slate-200 bg-white px-4 py-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                    {event.stage}
                  </p>
                  <span className="text-[11px] text-slate-500">{event.createdAt}</span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-800">{event.message}</p>
                {Object.keys(event.payload).length > 0 ? (
                  <pre className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-[16px] bg-slate-50 px-3 py-3 text-xs leading-6 text-slate-700">
                    {JSON.stringify(event.payload, null, 2)}
                  </pre>
                ) : null}
              </article>
            ))}
        </div>
      </details>
    </section>
  );
}


function MetricCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "slate" | "amber" | "rose";
}) {
  const toneClass = {
    slate: "border-slate-200 bg-slate-50 text-slate-900",
    amber: "border-amber-200 bg-amber-50 text-amber-950",
    rose: "border-rose-200 bg-rose-50 text-rose-950",
  }[tone];

  return (
    <div className={`rounded-[20px] border px-4 py-4 ${toneClass}`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] opacity-70">
        {label}
      </p>
      <p className="mt-2 text-xl font-semibold">{value}</p>
    </div>
  );
}


function levelPillClass(level: string) {
  if (level === "warning") {
    return "rounded-full bg-amber-100 px-2 py-1 text-[10px] font-medium uppercase tracking-[0.18em] text-amber-900";
  }
  if (level === "error") {
    return "rounded-full bg-rose-100 px-2 py-1 text-[10px] font-medium uppercase tracking-[0.18em] text-rose-900";
  }
  return "rounded-full bg-slate-200 px-2 py-1 text-[10px] font-medium uppercase tracking-[0.18em] text-slate-700";
}
