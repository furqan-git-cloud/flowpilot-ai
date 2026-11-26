"use client";

import { FormEvent, useState } from "react";
import type { SupabaseClient } from "@supabase/supabase-js";

type Props = {
  client: SupabaseClient;
};

export function AuthPanel({ client }: Props) {
  const [mode, setMode] = useState<"sign_in" | "sign_up">("sign_in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      if (mode === "sign_in") {
        const { error } = await client.auth.signInWithPassword({ email, password });
        if (error) throw error;
      } else {
        const { data, error } = await client.auth.signUp({ email, password });
        if (error) throw error;
        if (!data.session) {
          setMessage("Check your email to confirm your account, then sign in.");
        }
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Authentication failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="auth-title">
        <div className="brand auth-brand"><span className="brand-mark">F</span>FlowPilot AI</div>
        <p className="eyebrow">Private workspace access</p>
        <h1 id="auth-title">{mode === "sign_in" ? "Sign in to FlowPilot" : "Create your account"}</h1>
        <p className="auth-description">Your workspaces and customer data are private to your account.</p>
        <form className="auth-form" onSubmit={submit}>
          <label htmlFor="auth-email">Email</label>
          <input
            autoComplete="email"
            id="auth-email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <label htmlFor="auth-password">Password</label>
          <input
            autoComplete={mode === "sign_in" ? "current-password" : "new-password"}
            id="auth-password"
            type="password"
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          {message && <p className="auth-feedback" role="status">{message}</p>}
          <button className="primary" type="submit" disabled={busy}>
            {busy ? "Please wait…" : mode === "sign_in" ? "Sign in" : "Create account"}
          </button>
        </form>
        <button
          className="auth-toggle"
          type="button"
          onClick={() => {
            setMode(mode === "sign_in" ? "sign_up" : "sign_in");
            setMessage("");
          }}
        >
          {mode === "sign_in" ? "Need an account? Sign up" : "Already have an account? Sign in"}
        </button>
      </section>
    </main>
  );
}
