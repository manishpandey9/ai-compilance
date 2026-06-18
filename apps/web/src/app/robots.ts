import type { MetadataRoute } from "next";

const WEB_BASE = process.env.NEXT_PUBLIC_WEB_URL ?? "http://localhost:3000";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/" },
    sitemap: `${WEB_BASE}/sitemap.xml`,
  };
}
