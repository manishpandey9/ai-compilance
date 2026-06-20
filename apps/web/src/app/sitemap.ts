import type { MetadataRoute } from "next";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
const WEB_BASE = process.env.NEXT_PUBLIC_WEB_URL ?? "http://localhost:3000";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: WEB_BASE, lastModified: new Date() },
    { url: `${WEB_BASE}/eu-ai-act/compliance-checker`, lastModified: new Date() },
    { url: `${WEB_BASE}/pricing`, lastModified: new Date() },
  ];

  try {
    const res = await fetch(`${API_BASE}/pages?limit=100`, { next: { revalidate: 3600 } });
    if (!res.ok) return staticRoutes;
    const json = (await res.json()) as { data: { slug: string; index_supported?: boolean }[] };
    return [
      ...staticRoutes,
      ...json.data
        .filter((p) => p.index_supported !== false)
        .map((p) => ({
          url: `${WEB_BASE}/eu-ai-act/${p.slug}`,
          lastModified: new Date(),
        })),
    ];
  } catch {
    return staticRoutes;
  }
}
