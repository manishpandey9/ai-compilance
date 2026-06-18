import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Assessment",
  description: "EU AI Act classification questionnaire.",
};

export default function AssessmentLayout({ children }: { children: React.ReactNode }) {
  return children;
}
