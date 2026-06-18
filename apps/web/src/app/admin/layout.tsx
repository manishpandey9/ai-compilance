import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Admin console",
  description: "Internal admin tools for rule preview and pSEO regeneration.",
  robots: { index: false, follow: false },
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return children;
}
