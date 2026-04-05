import "server-only";

import { auth } from "@clerk/nextjs/server";

export const WORKSPACE_ROUTE = "/workspace";

export async function getAuthState() {
  const state = await auth();

  return {
    isAuthenticated: Boolean(state.userId),
    userId: state.userId,
    sessionId: state.sessionId,
  };
}

export async function requireUser() {
  const state = await auth();

  if (!state.userId) {
    return state.redirectToSignIn({
      returnBackUrl: WORKSPACE_ROUTE,
    });
  }

  return state;
}
