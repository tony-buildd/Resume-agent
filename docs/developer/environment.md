# Environment

The repo uses a single root `.env` file for local development.

Copy from `.env.example`:

```bash
cp .env.example .env
```

## Required Variables

### Clerk

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

Purpose:
- frontend auth UI
- authenticated workspace access
- user identity propagation into the backend

Where to get them:
- Clerk dashboard
- application -> API Keys

### Backend API URL

```env
RESUME_AGENT_API_URL=http://127.0.0.1:8000
```

Purpose:
- tells the web app how to reach the FastAPI backend during local development

### Database

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
```

Purpose:
- canonical persistence for users, sessions, artifacts, traces, and vault data

Notes:
- Neon connection strings usually need only the prefix changed from `postgresql://` to `postgresql+psycopg://`
- SSL/query parameters from the provider can stay on the URL

## Optional Variables

### OpenAI

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.4
OPENAI_REASONING_EFFORT=medium
```

Purpose:
- live JD analysis and research generation

Behavior if missing or unavailable:
- the backend falls back to deterministic heuristics instead of crashing the resume flow

## Local Safety Rules

- Never commit `.env`
- Never paste real keys into tracked docs
- Keep `.env.example` as placeholders only

## Recommended Local Providers

- Auth: Clerk
- Database: Neon Postgres
- LLM provider: OpenAI

Those are the current repo defaults and align with the implemented stack.
