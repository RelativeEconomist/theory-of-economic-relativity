# Theory of Economic Relativity — website

This project is a minimal, conversion-focused website theme for startup
founders, independent entrepreneurs, and founder-led advisory businesses. It
ships as a fully static Astro site with typed configuration, MDX publishing, a
light/dark design system, and carefully scoped motion.

> Important: every company, client mark, biography, testimonial, price, metric,
> and case-study result in the demo is fictional. Replace demo content before
> publishing. No third-party photography or brand logo is included.

## Stack

- Astro 7.1.4
- TypeScript in strict mode
- Typed MDX modules loaded with `import.meta.glob`
- Tailwind CSS 4 (via Vite) plus a reusable CSS token system
- GSAP + ScrollTrigger for reveal choreography
- Lenis for smooth scrolling
- Motion for menu and theme-toggle interactions
- anime.js for the hero micro-introduction
- Three.js for the responsive hero orbit
- Astro Sitemap and RSS

The site has no CMS, database, analytics, cookie banner, or form backend by
default. This keeps the theme portable and fast. Add only the services your
project actually needs.

## Quick start

Requirements: Node.js 22.12 or newer and npm 10 or newer.

```bash
npm install
npm run dev
```

Open `http://localhost:4321`.

Before shipping a customized build:

```bash
npm run check
npm run build
npm run preview
```

## The fastest way to customize this site

### 1. Update the global business details

Edit `src/config/site.ts`. This is the primary control panel for:

- site and company names;
- description and production URL;
- example contact address;
- navigation;
- social links;
- case-study cards;
- testimonials.

Also update the `site` value in `astro.config.mjs`. The production URL is used for
canonical tags, the sitemap, RSS, and social metadata.

### 2. Change the colors and type

The complete design system begins at the top of `src/styles/global.css`.

```css
:root {
  --bg: #f5f5f5;
  --surface: #ffffff;
  --ink: #121410;
  --accent: #d9ff43;
  --violet: #8b78ff;
  --orange: #ff6b35;
}
```

Dark-mode tokens live directly below the light tokens in
`html[data-theme="dark"]`. Always review both sets when changing a brand color.
The theme uses system fonts by default, avoiding font-license and performance
issues. To add a licensed font, self-host WOFF2 files in `public/fonts/`, declare
them with `@font-face`, then update `--font-sans` or `--font-display`.

### 3. Replace the logo

The header/footer mark is `src/components/ui/Logo.astro`. The browser icon is
`public/favicon.svg`, and the social share image is
`public/images/og-cover.svg`. These graphics are original to this project and
use no third-party trademark.

If you replace SVG files, keep an accessible text label or `aria-label`, and do
not remove the link back to the homepage from the main logo component.

### 4. Edit pages and homepage sections

Homepage order is controlled in `src/pages/index.astro`. Sections live in
`src/components/home/`, so buyers can reorder or remove a section with a single
component line.

```astro
<Hero />
<ProofBar />
<Problem />
<Services />
<CaseStudies />
<Process />
<Testimonial />
<Journal />
```

Standalone pages are in `src/pages/`. Search the project for `fictional`,
`illustrative`, `placeholder`, `demo`, and `example` before launch. These markers
intentionally make sample claims easy to find.

### 5. Publish a blog post

Add an `.md` or `.mdx` file to `src/posts/`:

```mdx
---
title: "A clear, specific article title"
description: "One sentence used on cards and in search metadata."
publishedAt: 2026-08-02
category: "Positioning"
author: "Your Name"
readingTime: "6 min read"
featured: false
draft: false
---

Write the article in Markdown or MDX here.
```

The typed metadata contract and loader are defined in `src/data/blog.ts`. Set `draft: true` to
exclude a post from the index, homepage, routes, and RSS feed. Only one post
should normally use `featured: true`.

### 6. Configure the contact experience

The default contact form does not send data to a server. It validates in the
browser and opens a pre-filled email draft to the address in
`src/config/site.ts`. This makes the template work without a backend and avoids
implying that submissions are stored.

For production, connect the form to a provider or your own endpoint and update:

- the submit handler in `src/pages/contact.astro`;
- the privacy policy;
- any required consent copy;
- spam protection and server-side validation;
- the Content Security Policy on your host.

Never place private API keys in Astro client scripts or `PUBLIC_` environment
variables.

### 7. Check SEO and discovery files

Before publishing, replace `https://www.theoryofeconomicrelativity.com` in:

- `astro.config.mjs`;
- `src/config/site.ts`;
- `public/robots.txt`;
- `public/llms.txt` as needed.

Astro generates `sitemap-index.xml`. RSS is available at `/rss.xml`. Every page
inherits canonical, Open Graph, Twitter card, favicon, and schema metadata from
`src/layouts/BaseLayout.astro`. Give important pages a unique title and
description through the layout props.

The privacy and terms pages are layout examples, not legal advice. Replace them
with documents reviewed for your business, location, hosting, analytics, and
third-party services.

## Motion and performance

The motion personality is deliberately premium: controlled ease, short UI
feedback, and one attention event at a time.

- Global reveal animation: `src/layouts/BaseLayout.astro`
- Header/menu interaction: `src/components/Header.astro`
- Hero WebGL and introduction: `src/components/home/Hero.astro`

All major animation is disabled when a visitor prefers reduced motion. The
Three.js renderer caps device pixel ratio more aggressively on small screens.
If you remove the WebGL hero, delete the canvas script and the `three`
dependency. If you remove smooth scrolling, delete the Lenis initialization and
the `lenis` dependency.

Avoid animating layout-heavy properties such as width, height, top, or left.
Prefer transform and opacity. Retest on a real mid-range phone after adding any
large media or script.

## Responsive and accessibility checklist

Before release, verify:

- 320 px, 375 px, 768 px, 1024 px, and a wide desktop viewport;
- light and dark mode on every page;
- keyboard focus order and visible focus rings;
- mobile menu open, close, Escape, link click, and resize behavior;
- minimum 48 px navigation and form controls;
- no horizontal overflow;
- all replacement images have useful alternative text;
- heading order remains logical after moving sections;
- color contrast remains WCAG AA after changing tokens;
- the contact flow works on iOS and Android;
- reduced-motion mode shows all content without hidden reveal states.

The mobile menu uses an opaque `var(--bg)` background by design. Do not change it
to a transparent background without verifying text contrast over every page.

## Deployment

`npm run build` creates a static `dist/` directory. It can be deployed to any
static host, including Cloudflare Pages, Netlify, Vercel, GitHub Pages, or a
traditional web server. Default settings:

- build command: `npm run build`
- publish directory: `dist`
- Node.js version: 22 or newer

No adapter is required for the included static form behavior. Add the appropriate
Astro adapter only if you introduce server-rendered routes.

## Project map

```text
public/                 Static SEO files and original SVG assets
src/components/        Shared navigation, footer, UI, and homepage sections
src/config/site.ts      Primary business details and shared demo data
src/posts/              MDX articles`n`src/data/blog.ts         Typed MDX metadata loader
src/layouts/            Global metadata, structure, Lenis, and GSAP
src/pages/              All routes
src/styles/global.css   Design tokens, typography, accessibility, utilities
```

## Licensing

Copyright © 2026 Relative Economist. See `LICENSE`. Dependencies
keep their own licenses; see `THIRD_PARTY_NOTICES.md` and the license files
installed under `node_modules/`.

GSAP's standard package can be used in ordinary websites under its current
terms, but review GreenSock's current licensing before using paid plugins or
building a product that competes with a site-building service. Do not
redistribute dependency source or premium assets outside their license terms.

## Support notes

When requesting support, include the Node version, npm version, the command that
failed, the complete terminal error, and whether the unmodified site builds.
Keep a clean copy of the base release so custom changes can be compared without
overwriting your work.
