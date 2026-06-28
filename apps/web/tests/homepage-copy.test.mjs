import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const homepageSource = await readFile(new URL("../src/app/page.tsx", import.meta.url), "utf8");
const footerSource = await readFile(
  new URL("../src/components/layout/footer.tsx", import.meta.url),
  "utf8",
);

test("homepage uses customer-facing copy instead of implementation notes", () => {
  assert.ok(homepageSource.includes("View HR screening example"));
  assert.ok(homepageSource.includes("Leave with a plain-English risk result"));
  assert.ok(homepageSource.includes("Download the first documents a customer or counsel will ask for"));

  assert.ok(!homepageSource.includes("Example: resume screening"));
  assert.ok(!homepageSource.includes("Classification runs on a published rule set"));
  assert.ok(!homepageSource.includes("Current rule-backed coverage"));
  assert.ok(!homepageSource.includes("Paid tiers add editable first drafts"));
  assert.ok(!homepageSource.includes("review territory"));
});

test("footer disclaimer avoids implementation jargon", () => {
  assert.ok(footerSource.includes("Information only, not legal advice."));
  assert.ok(!footerSource.includes("versioned rule engine"));
  assert.ok(!footerSource.includes("not an LLM"));
});
