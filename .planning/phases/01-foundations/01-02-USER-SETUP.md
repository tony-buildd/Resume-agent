# Phase 01-02 User Setup

## Required External Configuration

To verify the authentication and persistence foundation end to end, configure these values in the repo root `.env` file:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/resume_agent
```

## Clerk

1. Create a Clerk application.
2. Enable the sign-in and sign-up flows used by the app.
3. Copy the publishable key into `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`.
4. Copy the secret key into `CLERK_SECRET_KEY`.

## Postgres

1. Provision a reachable Postgres database.
2. Update `DATABASE_URL` with the real credentials.
3. Start the API once so SQLAlchemy can create the phase-one tables.

## Verification Commands

Run these after the environment variables are configured:

```bash
pnpm dev:web
PYTHONPATH=apps/api ./.venv/bin/uvicorn app.main:app --reload --app-dir apps/api
```

Then verify:

1. `/sign-in` and `/sign-up` render through Clerk.
2. `/workspace` redirects unauthenticated users to sign-in.
3. `POST /api/sessions` creates a session for the signed-in user.
4. `GET /api/sessions/{session_id}` returns the same user-scoped session envelope.
