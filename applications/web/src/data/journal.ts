import { getCollection, type CollectionEntry } from "astro:content";

export type JournalArticle = CollectionEntry<"journal">;

/**
 * Journal articles, newest first. Drafts are included only by `astro dev`,
 * for previewing; production builds neither list nor route them. Undated
 * drafts sort first.
 */
export async function getJournalArticles(): Promise<JournalArticle[]> {
  const articles = await getCollection("journal", ({ data }) => import.meta.env.DEV || !data.draft);
  const time = (article: JournalArticle) => article.data.publishedAt?.valueOf() ?? Infinity;
  return articles.sort((a, b) => time(b) - time(a));
}

export const articleUrl = (article: JournalArticle) => `/journal/${article.id}/`;

/** A draft may not have a title yet; only `astro dev` ever shows one. */
export const articleTitle = (article: JournalArticle) => article.data.title ?? `Untitled draft (${article.id})`;

export const formatDate = (date: Date) =>
  date.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
