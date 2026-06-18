import { focusRing } from "@/lib/focus";

export function SkipLink() {
  return (
    <a
      href="#main-content"
      className={`sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-zinc-950 ${focusRing}`}
    >
      Skip to main content
    </a>
  );
}
