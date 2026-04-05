import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,#f4f6fb_0%,#eef2ff_48%,#ffffff_100%)] px-6 py-10">
      <SignUp />
    </main>
  );
}
