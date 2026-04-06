type DiffViewProps = {
  beforeLabel: string;
  afterLabel: string;
  beforeItems: string[];
  afterItems: string[];
};

export function DiffView({
  beforeLabel,
  afterLabel,
  beforeItems,
  afterItems,
}: DiffViewProps) {
  return (
    <section className="grid gap-3 lg:grid-cols-2">
      <DiffColumn
        label={beforeLabel}
        items={beforeItems}
        tone="before"
        emptyMessage="No source material available yet."
      />
      <DiffColumn
        label={afterLabel}
        items={afterItems}
        tone="after"
        emptyMessage="No generated output available yet."
      />
    </section>
  );
}

function DiffColumn({
  label,
  items,
  tone,
  emptyMessage,
}: {
  label: string;
  items: string[];
  tone: "before" | "after";
  emptyMessage: string;
}) {
  const toneClass =
    tone === "before"
      ? "border-slate-200 bg-slate-100/80 text-slate-800"
      : "border-emerald-200 bg-emerald-50 text-emerald-950";

  return (
    <article className={`rounded-[20px] border px-4 py-4 ${toneClass}`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] opacity-70">
        {label}
      </p>
      <div className="mt-3 space-y-2">
        {items.length > 0 ? (
          items.map((item, index) => (
            <p
              key={`${label}-${index}`}
              className="rounded-[16px] bg-white/70 px-3 py-2 text-sm leading-6"
            >
              {item}
            </p>
          ))
        ) : (
          <p className="text-sm leading-6 opacity-75">{emptyMessage}</p>
        )}
      </div>
    </article>
  );
}
