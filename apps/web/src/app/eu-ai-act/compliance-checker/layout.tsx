import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Questionnaire",
  description: "Five to ten minute EU AI Act classification with article references.",
};

export default function ComplianceCheckerLayout({ children }: { children: React.ReactNode }) {
  return children;
}
