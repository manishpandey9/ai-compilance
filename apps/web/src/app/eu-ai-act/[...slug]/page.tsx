import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { JsonLd } from "@/components/seo/json-ld";
import { MarkdownContent } from "@/components/seo/markdown-content";
import { SiteFooter } from "@/components/layout/footer";
import { ButtonLink } from "@/components/ui/button";
import { fetchPage } from "@/lib/api";
import { cn } from "@/lib/cn";
import { focusRingLight } from "@/lib/focus";
import { SITE } from "@/lib/site";

type Props = { params: Promise<{ slug: string[] }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const page = await fetchPage(slug.join("/"));
  if (!page) return { title: "Not found" };

  return {
    title: page.title,
    description: page.meta_description,
    alternates: { canonical: page.canonical_url || `${SITE.url}/eu-ai-act/${page.slug}` },
    openGraph: {
      title: page.title,
      description: page.meta_description,
      type: "article",
    },
  };
}

export default async function SEOPage({ params }: Props) {
  const { slug } = await params;
  const path = slug.join("/");
  const page = await fetchPage(path);
  if (!page) notFound();

  return (
    <div className="flex min-h-screen flex-col bg-white text-zinc-900">
      <JsonLd data={page.structured_data} />
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-baseline justify-between px-6 py-5">
          <Link
            href="/"
            className={cn("text-[0.95rem] font-semibold tracking-tight text-zinc-900 hover:text-zinc-700", focusRingLight)}
          >
            {SITE.name}
          </Link>
          <nav className="flex gap-8 text-[0.8125rem]" aria-label="Main">
            <Link
              href="/eu-ai-act/compliance-checker"
              className={cn("text-zinc-600 hover:text-zinc-900", focusRingLight)}
            >
              Questionnaire
            </Link>
            <Link
              href="/pricing"
              className={cn("text-zinc-600 hover:text-zinc-900", focusRingLight)}
            >
              Pricing
            </Link>
          </nav>
        </div>
      </header>
      <main id="main-content" className="flex-1">
        <article className="mx-auto max-w-3xl px-6 py-12">
          <h1 className="text-headline text-zinc-900">{page.title}</h1>
          {page.last_reviewed_at && (
            <p className="text-mono-ui mt-3 text-sm text-zinc-500">
              Last reviewed {new Date(page.last_reviewed_at).toLocaleDateString()}
              {page.rule_version != null && ` · Rule set v${page.rule_version}`}
            </p>
          )}
          <div className="mt-8">
            <MarkdownContent content={page.content_md} />
          </div>
          <div className="mt-16 border-t border-zinc-200 pt-12">
            <h2 className="text-lg font-semibold tracking-tight text-zinc-900">
              Run this for your product
            </h2>
            <p className="mt-2 max-w-lg text-sm leading-relaxed text-zinc-600">
              Five to ten minutes. Risk tier and obligations with article references.
            </p>
            <ButtonLink
              href="/eu-ai-act/compliance-checker"
              surface="light"
              size="lg"
              className="mt-6"
            >
              Start questionnaire
            </ButtonLink>
          </div>
        </article>
      </main>
      <SiteFooter variant="light" />
    </div>
  );
}
