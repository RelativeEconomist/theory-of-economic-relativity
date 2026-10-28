import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";

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

export const collections = { theory, foundations, faq };
