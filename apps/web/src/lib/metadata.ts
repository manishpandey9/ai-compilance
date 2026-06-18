import type { Metadata } from "next";

import { SITE } from "@/lib/site";

export const defaultMetadata: Metadata = {
  title: {
    default: SITE.title,
    template: `%s · ${SITE.name}`,
  },
  description: SITE.description,
  metadataBase: new URL(SITE.url),
};
