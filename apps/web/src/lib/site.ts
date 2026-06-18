export const SITE = {
  name: "AI Act Navigator",
  title: "AI Act Navigator",
  description:
    "EU AI Act risk classification and document packs for AI vendors. Rule engine with article references, not a chatbot legal opinion.",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
} as const;
