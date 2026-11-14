export const siteConfig = {
  name: "Theory of Economic Relativity",
  company: "Theory of Economic Relativity",
  title: "Theory of Economic Relativity",
  description: "An open, testable framework for economic decision-making, interaction, and outcomes.",
  url: "https://www.theoryofeconomicrelativity.com",
  author: "Relative Economist",
  bookingUrl: "/contact/",
  version: __TER_VERSION__,
  nav: [
    { label: "Home", href: "/", external: false },
    { label: "Learn", href: "/learn/", external: false },
    { label: "Theory", href: "/theory/", external: false },
    { label: "Journal", href: "/journal/", external: false },
    { label: "Participate", href: "/participate/", external: false },
    {
      label: "GitHub",
      href: "https://github.com/RelativeEconomist/theory-of-economic-relativity",
      external: true,
    },
  ],
  // Rendered as icon links in the shared footer. Each `icon` must match a key
  // in the icon map in src/components/ui/SocialLinks.astro.
  social: [
    { label: "YouTube", href: "https://www.youtube.com/@TheoryofEconomicRelativity", icon: "youtube" },
    { label: "Reddit", href: "https://www.reddit.com/user/a-relative-economist/", icon: "reddit" },
    { label: "Bluesky", href: "https://bsky.app/profile/relativeeconomist.bsky.social", icon: "bluesky" },
    { label: "Medium", href: "https://medium.com/@relativeeconomist", icon: "medium" },
  ],
} as const;
