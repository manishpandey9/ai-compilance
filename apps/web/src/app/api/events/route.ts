const MAX_EVENT_LENGTH = 80;
const MAX_VALUE_LENGTH = 240;

function safeString(value: unknown, maxLength = MAX_VALUE_LENGTH): string | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  return trimmed.slice(0, maxLength);
}

function safeProperties(value: unknown): Record<string, string | number | boolean | null> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  const properties: Record<string, string | number | boolean | null> = {};
  for (const [key, raw] of Object.entries(value as Record<string, unknown>)) {
    if (/email|name|token|secret|password|url/i.test(key)) continue;
    if (typeof raw === "string") {
      properties[key] = raw.slice(0, MAX_VALUE_LENGTH);
    } else if (typeof raw === "number" || typeof raw === "boolean" || raw === null) {
      properties[key] = raw;
    }
  }
  return properties;
}

function safeReferrer(value: string | null): string | null {
  if (!value) return null;
  try {
    const url = new URL(value);
    return `${url.origin}${url.pathname}`.slice(0, MAX_VALUE_LENGTH);
  } catch {
    return safeString(value);
  }
}

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as {
    event?: unknown;
    path?: unknown;
    properties?: unknown;
  } | null;
  const event = safeString(body?.event, MAX_EVENT_LENGTH);
  if (!event) {
    return Response.json({ ok: false, error: "invalid_event" }, { status: 400 });
  }

  console.log(
    JSON.stringify({
      type: "analytics_event",
      event,
      path: safeString(body?.path),
      properties: safeProperties(body?.properties),
      referrer: safeReferrer(request.headers.get("referer")),
      userAgent: safeString(request.headers.get("user-agent")),
      timestamp: new Date().toISOString(),
    }),
  );

  return Response.json({ ok: true });
}
