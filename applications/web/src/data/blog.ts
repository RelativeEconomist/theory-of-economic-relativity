export interface BlogFrontmatter {
  title: string;
  description: string;
  publishedAt: string | Date;
  updatedAt?: string | Date;
  category: string;
  author?: string;
  readingTime: string;
  featured?: boolean;
  draft?: boolean;
}

interface BlogModule {
  frontmatter: BlogFrontmatter;
  default: any;
}

export interface BlogPost extends Omit<BlogFrontmatter, "publishedAt" | "updatedAt"> {
  id: string;
  publishedAt: Date;
  updatedAt?: Date;
  Content: any;
}

const modules = import.meta.glob<BlogModule>("../posts/*.{md,mdx}", { eager: true });

export const blogPosts: BlogPost[] = Object.entries(modules)
  .map(([path, module]) => ({
    ...module.frontmatter,
    id: path.split("/").at(-1)?.replace(/\.(md|mdx)$/, "") ?? "post",
    publishedAt: new Date(module.frontmatter.publishedAt),
    updatedAt: module.frontmatter.updatedAt ? new Date(module.frontmatter.updatedAt) : undefined,
    author: module.frontmatter.author ?? "Avery Morgan",
    featured: module.frontmatter.featured ?? false,
    draft: module.frontmatter.draft ?? false,
    Content: module.default,
  }))
  .filter((post) => !post.draft)
  .sort((a, b) => b.publishedAt.valueOf() - a.publishedAt.valueOf());