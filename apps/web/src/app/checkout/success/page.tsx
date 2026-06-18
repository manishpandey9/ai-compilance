import type { Metadata } from "next";
import { Suspense } from "react";

import { AppShell, PageContainer } from "@/components/layout/shell";

import CheckoutSuccessInner from "./CheckoutSuccessInner";

export const metadata: Metadata = {
  title: "Checkout complete",
  description: "Your EU AI Act compliance documents are being prepared.",
};

export default function CheckoutSuccessPage() {
  return (
    <Suspense
      fallback={
        <AppShell>
          <PageContainer width="form" className="py-20 text-center">
            <p className="text-zinc-400">Loading…</p>
          </PageContainer>
        </AppShell>
      }
    >
      <CheckoutSuccessInner />
    </Suspense>
  );
}
