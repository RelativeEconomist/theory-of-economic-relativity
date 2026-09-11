import path from "node:path";

export interface RemarkRewriteRepoLinksRule {
  /** Absolute path to the canonical source file this rule applies to. */
  sourceFile: string;
  /**
   * Directory this file's relative links resolve against, relative to the
   * repo root (posix-style, no leading/trailing slash). Use "" for the repo
   * root itself.
   */
  relativeTo: string;
}

const REPO_BLOB_BASE =
  "https://github.com/RelativeEconomist/theory-of-economic-relativity/blob/main";

// Matches any "scheme:" prefix (http:, https:, mailto:, tel:, ...) so every
// absolute-URL form is left untouched, not just http/https/mailto.
const ABSOLUTE_URL_PATTERN = /^[a-z][a-z0-9+.-]*:/i;

function isRewritable(url: string): boolean {
  if (!url || url.startsWith("#")) return false;
  if (ABSOLUTE_URL_PATTERN.test(url)) return false;
  return true;
}

interface MdastNode {
  type: string;
  url?: string;
  children?: MdastNode[];
}

function visit(node: MdastNode, callback: (node: MdastNode) => void): void {
  callback(node);
  for (const child of node.children ?? []) {
    visit(child, callback);
  }
}

/**
 * Rewrites relative links found in any of several specific canonical
 * Markdown source files so they resolve to that file's location on GitHub
 * instead of a website-relative (and therefore nonexistent) route.
 *
 * Takes one array of rules -- rather than being registered once per file
 * via separate `[remarkRewriteRepoLinks, options]` calls -- because unified's
 * `Processor.use()` keys plugin registration on the *function reference*: if
 * the same attacher function is passed to `.use()` more than once, unified
 * does not create independent transformer instances. It merges every call's
 * options into one shared object and instantiates the attacher only once,
 * with whichever options were merged in last -- silently discarding every
 * rule but the last-registered one. Registering this plugin exactly once,
 * with the full list of rules, avoids that collision entirely.
 *
 * Matched purely by comparing the file actually being rendered against each
 * rule's `sourceFile` -- since these documents are rendered straight from
 * their real path on disk (see src/content.config.ts), not a copy, this
 * leaves every other file (e.g. blog posts) completely untouched.
 */
export function remarkRewriteRepoLinks(rules: RemarkRewriteRepoLinksRule[]) {
  const resolvedRules = rules.map(({ sourceFile, relativeTo }) => ({
    targetPath: path.resolve(sourceFile),
    relativeTo,
  }));

  return (tree: MdastNode, file: { path?: string }) => {
    const filePath = file.path ? path.resolve(file.path) : undefined;
    const rule = resolvedRules.find((candidate) => candidate.targetPath === filePath);
    if (!rule) return;

    visit(tree, (node) => {
      if (node.type !== "link" || typeof node.url !== "string" || !isRewritable(node.url)) {
        return;
      }

      const repoRelativePath = path.posix.normalize(path.posix.join(rule.relativeTo, node.url));
      node.url = `${REPO_BLOB_BASE}/${repoRelativePath}`;
    });
  };
}
