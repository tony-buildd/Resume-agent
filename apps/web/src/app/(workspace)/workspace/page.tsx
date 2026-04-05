import { auth } from "@clerk/nextjs/server";

export default async function WorkspacePage() {
  const { userId, sessionId } = await auth();

  return (
    <section className="grid gap-5 lg:grid-cols-[1.25fr_0.95fr]">
      <article className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.45)]">
        <h2 className="text-lg font-semibold text-slate-950">
          Protected workspace route
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
          This route is now protected by Clerk middleware and a server-side
          auth check in the workspace layout. Future phases will replace this
          placeholder with the conversation thread, artifact panels, and trace
          views.
        </p>
        <dl className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
            <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              User ID
            </dt>
            <dd className="mt-2 break-all text-sm text-slate-900">{userId}</dd>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
            <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Session ID
            </dt>
            <dd className="mt-2 break-all text-sm text-slate-900">
              {sessionId ?? "pending"}
            </dd>
          </div>
        </dl>
      </article>

      <aside className="rounded-[28px] border border-slate-200 bg-slate-950 p-6 text-slate-50 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.65)]">
        <h2 className="text-lg font-semibold">Phase 1 auth boundary</h2>
        <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-300">
          <li>Route protection lives in `src/proxy.ts`.</li>
          <li>Server-side auth helpers live in `src/lib/auth.ts`.</li>
          <li>
            The workspace layout enforces authentication before protected UI
            renders.
          </li>
        </ul>
      </aside>
    </section>
  );
}
