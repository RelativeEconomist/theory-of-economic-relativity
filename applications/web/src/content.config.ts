import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

// These collections read the canonical Markdown directly from the repo
// root at build/dev time. Nothing is copied into applications/web/, and
// neither source file is modified -- `base` just points the loader at
// their real location on disk (relative to this project's root).
const theory = defineCollection({
  loader: glob({ pattern: "academic.md", base: "../../theory" }),
});

const foundations = defineCollection({
  loader: glob({ pattern: "foundations-and-references.md", base: "../../research" }),
});

const faq = defineCollection({
  loader: glob({ pattern: "faq.md", base: "../../research" }),
});

// Journal articles are website content, so they live in this project.
// An article's URL is /journal/<file name>/: renaming a published file
// breaks its permanent URL.
const journal = defineCollection({
  loader: glob({ pattern: "*.md", base: "./src/content/journal" }),
  schema: ({ image }) => {
    const published = z.object({
      draft: z.literal(false).default(false),
      title: z.string().min(1),
      description: z.string().min(1),
      author: z.string().min(1),
      publishedAt: z.coerce.date(),
      updatedAt: z.coerce.date().optional(),
      cover: z.object({ src: image(), alt: z.string().min(1) }).optional(),
    });
    // A draft may be missing anything it still awaits; it is never built
    // for production, so the published requirements apply once it is not.
    const draft = published.partial().extend({ draft: z.literal(true) });
    return z.union([published, draft]);
  },
});

export const collections = { theory, foundations, faq, journal };
