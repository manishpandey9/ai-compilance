"use client";

type AnalyticsValue = string | number | boolean | null | undefined;
type AnalyticsProperties = Record<string, AnalyticsValue>;

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
    posthog?: {
      capture?: (event: string, properties?: AnalyticsProperties) => void;
    };
  }
}

function cleanProperties(properties: AnalyticsProperties = {}): Record<string, string | number | boolean | null> {
  const safe: Record<string, string | number | boolean | null> = {};
  for (const [key, value] of Object.entries(properties)) {
    if (value === undefined) continue;
    if (/email|name|token|secret|password|url/i.test(key)) continue;
    safe[key] = value;
  }
  return safe;
}

export function trackEvent(event: string, properties: AnalyticsProperties = {}) {
  if (typeof window === "undefined") return;
  const safeProperties = cleanProperties(properties);

  window.gtag?.("event", event, safeProperties);
  window.posthog?.capture?.(event, safeProperties);

  const payload = JSON.stringify({
    event,
    properties: safeProperties,
    path: window.location.pathname,
  });

  if (navigator.sendBeacon) {
    navigator.sendBeacon("/api/events", new Blob([payload], { type: "application/json" }));
    return;
  }

  void fetch("/api/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload,
    keepalive: true,
  }).catch(() => undefined);
}
