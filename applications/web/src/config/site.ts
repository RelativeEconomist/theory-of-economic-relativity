export const siteConfig = {
  name: "Theory of Economic Relativity",
  company: "Theory of Economic Relativity",
  title: "Theory of Economic Relativity — A testable framework for economic decision-making",
  description:
    "Theory of Economic Relativity (TER) is an open, testable architecture for economic decision-making, interaction, and outcomes, tested through executable replication tests.",
  url: "https://www.theoryofeconomicrelativity.com",
  author: "Relative Economist",
  bookingUrl: "/contact/",
  version: __TER_VERSION__,
  nav: [
    { label: "Home", href: "/", external: false },
    { label: "Learn", href: "/learn/", external: false },
    { label: "Theory", href: "/theory/", external: false },
    { label: "Contribute", href: "/contribute/", external: false },
    {
      label: "GitHub",
      href: "https://github.com/RelativeEconomist/theory-of-economic-relativity",
      external: true,
    },
  ],
} as const;
