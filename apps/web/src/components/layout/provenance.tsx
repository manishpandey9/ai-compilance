import type { ReactNode } from "react";

/** Mono provenance line — not the emerald uppercase eyebrow trope */
export function Provenance({ children }: { children: ReactNode }) {
  return <p className="text-mono-ui mb-8 text-slate-500">{children}</p>;
}

export function SectionRule() {
  return <hr className="border-0 border-t border-slate-800" />;
}
