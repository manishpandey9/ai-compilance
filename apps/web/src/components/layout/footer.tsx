import Link from "next/link";

import { cn } from "@/lib/cn";
import { focusRing, focusRingLight } from "@/lib/focus";
import { SITE } from "@/lib/site";

type SiteFooterProps = {
  variant?: "dark" | "light";
};

export function SiteFooter({ variant = "dark" }: SiteFooterProps) {
  const isDark = variant === "dark";
  const ring = isDark ? focusRing : focusRingLight;

  return (
    <footer
      className={cn(
        "border-t text-sm",
        isDark ? "border-zinc-800 text-zinc-500" : "border-zinc-200 text-zinc-600",
      )}
    >
      <div className="mx-auto flex max-w-5xl flex-col gap-6 px-6 py-10 sm:flex-row sm:items-start sm:justify-between">
        <p className="max-w-xs leading-relaxed">
          Not legal advice. Classification uses a versioned rule engine, not an LLM.
        </p>
        <nav className="flex flex-wrap gap-x-6 gap-y-2" aria-label="Footer">
          <Link href="/eu-ai-act/compliance-checker" className={cn("hover:underline", ring)}>
            Questionnaire
          </Link>
          <Link href="/pricing" className={cn("hover:underline", ring)}>
            Pricing
          </Link>
          <Link href="/eu-ai-act/hr-tech/resume-screening" className={cn("hover:underline", ring)}>
            Guides
          </Link>
        </nav>
      </div>
      <p
        className={cn(
          "mx-auto max-w-5xl border-t px-6 py-4 text-xs",
          isDark ? "border-zinc-800 text-zinc-600" : "border-zinc-200 text-zinc-500",
        )}
      >
        © {new Date().getFullYear()} {SITE.name}
      </p>
    </footer>
  );
}
