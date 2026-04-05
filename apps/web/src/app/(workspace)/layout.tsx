import { UserButton } from "@clerk/nextjs";

import { requireUser } from "@/lib/auth";

export default async function WorkspaceLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  await requireUser();

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#eef2ff_0%,#f8fafc_55%,#ffffff_100%)]">
      <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Resume Agent
            </p>
            <h1 className="mt-1 text-lg font-semibold text-slate-950">
              Authenticated workspace shell
            </h1>
          </div>
          <UserButton />
        </div>
      </header>
      <div className="mx-auto max-w-6xl px-6 py-8">{children}</div>
    </div>
  );
}
