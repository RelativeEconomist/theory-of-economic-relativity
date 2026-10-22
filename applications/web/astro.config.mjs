import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig } from "astro/config";
import { loadEnv } from "vite";
import { unified } from "@astrojs/markdown-remark";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import tailwindcss from "@tailwindcss/vite";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { remarkRewriteRepoLinks } from "./src/config/remark-repo-links.ts";

// Resolved from this file's own location (not process.cwd()), so these
// paths are correct regardless of the directory `astro dev`/`astro build`
// is invoked from. From applications/web/, the repo root is `../..`.
const repoRootUrl = new URL("../..", import.meta.url);
const repoRoot = fileURLToPath(repoRootUrl);
const projectRoot = fileURLToPath(new URL(".", import.meta.url));
const theoryFile = fileURLToPath(new URL("theory/academic.md", repoRootUrl));
const contributingFile = fileURLToPath(new URL("CONTRIBUTING.md", repoRootUrl));
const foundationsFile = fileURLToPath(new URL("research/foundations-and-references.md", repoRootUrl));
const faqFile = fileURLToPath(new URL("research/faq.md", repoRootUrl));
const versionFile = fileURLToPath(new URL("VERSION", repoRootUrl));
// Read once here (this file's own path is stable, unlike a bundled src
// module's at build time) and inlined via `define` below, so the version
// string is never duplicated and the root VERSION file stays canonical.
const terVersion = readFileSync(versionFile, "utf-8").trim();

// run-scenario.ts falls back to the local simulator at 127.0.0.1:8000 for
// development. A production build must name the API explicitly, so it
// fails here instead of shipping that fallback.
const requireTerApiUrlForBuild = {
  name: "require-ter-api-url",
  hooks: {
    "astro:config:setup": ({ command }) => {
      if (command !== "build") return;

      const env = loadEnv("production", projectRoot, "PUBLIC_");

      if (!env.PUBLIC_TER_API_URL?.trim()) {
        throw new Error(
          "PUBLIC_TER_API_URL must be set for production builds " +
            "(e.g. https://api.theoryofeconomicrelativity.com).",
        );
      }
    },
  },
};

export default defineConfig({
  site: "https://www.theoryofeconomicrelativity.com",
  devToolbar: { enabled: false },
  integrations: [requireTerApiUrlForBuild, mdx(), sitemap()],
  markdown: {
    processor: unified({
      remarkPlugins: [
        remarkMath,
        // Registered once, with every rule, rather than once per file --
        // see the comment on remarkRewriteRepoLinks for why repeating this
        // same attacher with different options per call would silently
        // collapse into a single (wrong) rule under unified's plugin
        // deduplication.
        [
          remarkRewriteRepoLinks,
          [
            { sourceFile: theoryFile, relativeTo: "theory" },
            { sourceFile: contributingFile, relativeTo: "" },
            { sourceFile: foundationsFile, relativeTo: "research" },
            { sourceFile: faqFile, relativeTo: "research" },
          ],
        ],
      ],
      rehypePlugins: [rehypeKatex],
    }),
  },
  vite: {
    plugins: [tailwindcss()],
    define: {
      __TER_VERSION__: JSON.stringify(terVersion),
    },
    server: {
      fs: {
        // Explicitly allow the repo root so theory/academic.md and
        // CONTRIBUTING.md, which live outside applications/web/, can be
        // read by the dev server (in addition to the project root itself).
        allow: [projectRoot, repoRoot],
      },
    },
  },
  build: {
    inlineStylesheets: "auto",
  },
  prefetch: {
    prefetchAll: true,
    defaultStrategy: "viewport",
  },
});
