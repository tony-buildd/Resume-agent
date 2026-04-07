import Link from "next/link";

import { UserButton } from "@clerk/nextjs";

import { getAuthState } from "@/lib/auth";

export default async function Home() {
  const { isAuthenticated } = await getAuthState();

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#f4f6fb_0%,#eef2ff_48%,#ffffff_100%)] px-6 py-10 text-slate-950">
      <div className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-[28px] border border-slate-200/80 bg-white/90 px-6 py-5 shadow-[0_24px_60px_-32px_rgba(15,23,42,0.35)] backdrop-blur">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
            Phase 1 Foundations
          </p>
          <div className="mt-3 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div className="max-w-3xl">
              <h1 className="text-3xl font-semibold tracking-tight text-slate-950 md:text-4xl">
                Resume Agent workspace shell
              </h1>
              <p className="mt-3 text-sm leading-7 text-slate-600 md:text-base">
                This app shell is the starting point for a chat-first resume
                orchestration product. Later phases will add auth, the career
                vault, session artifacts, research traces, and evaluator-driven
                resume revisions.
              </p>
            </div>
            <div className="flex items-center gap-3">
              {!isAuthenticated ? (
                <div className="flex flex-wrap gap-3">
                  <Link
                    href="/sign-in"
                    className="rounded-full bg-slate-950 px-4 py-3 text-sm font-medium text-slate-50"
                  >
                    Sign in
                  </Link>
                  <Link
                    href="/sign-up"
                    className="rounded-full border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-900"
                  >
                    Create account
                  </Link>
                </div>
              ) : (
                <>
                  <Link
                    href="/workspace"
                    className="rounded-full bg-slate-950 px-4 py-3 text-sm font-medium text-slate-50"
                  >
                    Open workspace
                  </Link>
                  <div className="rounded-full border border-slate-200 bg-white p-2">
                    <UserButton />
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        <section className="grid gap-5 lg:grid-cols-[1.35fr_0.9fr]">
          <article className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.45)]">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-950">
                Planned workspace areas
              </h2>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                scaffold only
              </span>
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              {[
                "Conversation thread",
                "JD analysis panel",
                "Career vault panel",
                "Trace and artifact review",
              ].map((item) => (
                <div
                  key={item}
                  className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4"
                >
                  <p className="text-sm font-medium text-slate-900">{item}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    Placeholder surface reserved for future phases.
                  </p>
                </div>
              ))}
            </div>
          </article>

          <aside className="rounded-[28px] border border-slate-200 bg-slate-950 p-6 text-slate-50 shadow-[0_24px_60px_-36px_rgba(15,23,42,0.65)]">
            <h2 className="text-lg font-semibold">Foundation checklist</h2>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-300">
              <li>1. Normalize the repo into a web + API workspace</li>
              <li>2. Add protected workspace routing and user ownership</li>
              <li>3. Persist sessions, artifacts, and trace events</li>
              <li>4. Expose a typed orchestration shell</li>
            </ul>
          </aside>
        </section>
      </div>
    </main>
  );
}
