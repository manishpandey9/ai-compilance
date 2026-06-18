"use client";

import { FormEvent, useState } from "react";

import { SiteFooter } from "@/components/layout/footer";
import { AppShell, MarketingHeader, PageContainer } from "@/components/layout/shell";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/input";

import { api } from "@/lib/api";

export default function AdminPage() {
  const [key, setKey] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [preview, setPreview] = useState<unknown>(null);

  async function onPreview(e: FormEvent) {
    e.preventDefault();
    setMessage(null);
    try {
      const res = await api.adminPreviewRules(key);
      setPreview(res);
      setMessage(res.all_pass ? "All fixtures pass" : "Some fixtures failed");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Preview failed");
    }
  }

  async function onRegenerate() {
    setMessage(null);
    try {
      const res = await api.adminRegenerateSeo(key);
      setMessage(`Queued ${res.queued_pages} pages for regeneration`);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Regenerate failed");
    }
  }

  return (
    <AppShell variant="light" header={<MarketingHeader variant="light" />} footer={<SiteFooter variant="light" />}>
      <PageContainer width="form" className="py-16">
        <main id="main-content">
          <h1 className="text-headline text-zinc-900">Admin</h1>
          <p className="mt-2 text-sm text-zinc-600">Rule fixture preview and pSEO regeneration.</p>

          <form onSubmit={onPreview} className="mt-10 space-y-6 border-t border-zinc-200 pt-10" aria-label="Admin actions">
            <Field label="Admin API key" surface="light">
              <Input
                type="password"
                surface="light"
                placeholder="Admin API key"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                autoComplete="off"
              />
            </Field>
            <div className="flex flex-wrap gap-3">
              <Button type="submit" surface="light">Preview rules</Button>
              <Button type="button" variant="secondary" surface="light" onClick={onRegenerate}>
                Regenerate SEO pages
              </Button>
            </div>
          </form>
          {message && (
            <p className="mt-4 text-sm text-zinc-700" role="status">
              {message}
            </p>
          )}
          {preview != null && (
            <pre className="text-mono-ui mt-8 overflow-auto border-t border-zinc-200 pt-8 text-xs leading-relaxed text-zinc-600">
              {JSON.stringify(preview, null, 2)}
            </pre>
          )}
        </main>
      </PageContainer>
    </AppShell>
  );
}
