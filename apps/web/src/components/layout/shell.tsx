import Link from "next/link";
import type { ReactNode } from "react";

import { cn } from "@/lib/cn";
import { focusRing, focusRingLight } from "@/lib/focus";
import { SITE } from "@/lib/site";

type MarketingHeaderProps = {
  variant?: "dark" | "light";
};

export function MarketingHeader({ variant = "dark" }: MarketingHeaderProps) {
  const isDark = variant === "dark";
  const ring = isDark ? focusRing : focusRingLight;

  return (
    <header
      className={cn(
        "border-b",
        isDark ? "border-zinc-800 bg-[var(--canvas-dark)]" : "border-zinc-200 bg-white",
      )}
    >
      <div className="mx-auto flex max-w-5xl items-baseline justify-between px-6 py-5">
        <Link
          href="/"
          className={cn(
            "text-[0.95rem] font-semibold tracking-tight",
            isDark ? "text-zinc-100 hover:text-white" : "text-zinc-900 hover:text-zinc-700",
            ring,
          )}
        >
          {SITE.name}
        </Link>
        <nav className="flex gap-8 text-[0.8125rem]" aria-label="Main">
          <Link
            href="/eu-ai-act/compliance-checker"
            className={cn(
              isDark ? "text-zinc-500 hover:text-zinc-200" : "text-zinc-600 hover:text-zinc-900",
              ring,
            )}
          >
            Questionnaire
          </Link>
          <Link
            href="/pricing"
            className={cn(
              isDark ? "text-zinc-500 hover:text-zinc-200" : "text-zinc-600 hover:text-zinc-900",
              ring,
            )}
          >
            Pricing
          </Link>
        </nav>
      </div>
    </header>
  );
}

type AppShellProps = {
  children: ReactNode;
  header?: ReactNode;
  footer?: ReactNode;
  className?: string;
  variant?: "dark" | "light";
};

export function AppShell({ children, header, footer, className, variant = "dark" }: AppShellProps) {
  return (
    <div
      className={cn(
        "flex min-h-screen flex-col",
        variant === "dark"
          ? "bg-[var(--canvas-dark)] text-[var(--text-primary)]"
          : "bg-white text-[var(--text-on-light)]",
        className,
      )}
    >
      {header}
      <div className="flex-1">{children}</div>
      {footer}
    </div>
  );
}

type PageContainerProps = {
  children: ReactNode;
  width?: "marketing" | "form" | "content";
  className?: string;
};

export function PageContainer({ children, width = "marketing", className }: PageContainerProps) {
  const maxW =
    width === "form" ? "max-w-xl" : width === "content" ? "max-w-2xl" : "max-w-5xl";

  return <div className={cn("mx-auto px-6", maxW, className)}>{children}</div>;
}

type BackLinkProps = {
  href: string;
  children: ReactNode;
  variant?: "dark" | "light";
};

export function BackLink({ href, children, variant = "dark" }: BackLinkProps) {
  const ring = variant === "dark" ? focusRing : focusRingLight;

  return (
    <Link
      href={href}
      className={cn(
        "text-sm",
        variant === "dark" ? "text-zinc-500 hover:text-zinc-200" : "text-zinc-600 hover:text-zinc-900",
        ring,
      )}
    >
      {children}
    </Link>
  );
}
