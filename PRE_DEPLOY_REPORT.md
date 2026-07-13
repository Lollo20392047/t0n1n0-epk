# Pre-deploy report

Date: 2026-07-12

## Result

Technical status: **ready for a Vercel preview deployment**.

## Automated checks

- 68/68 headless Chromium checks passed.
- Viewports tested: 320×568, 390×844, 1440×900, 2560×1440.
- No JavaScript errors, console errors, failed initial requests, or horizontal overflow.
- Mobile menu open/close, Escape key, anchor navigation, print action, skip link, reduced-motion behavior, and no-JavaScript fallback passed.
- All local assets, metadata, internal anchors, IDs, and `target="_blank"` protections passed.
- Print CSS exposes every animated section.
- Dependency-free static smoke test included in `tests/smoke_test.py` and run automatically through GitHub Actions.

## Fixes completed

- Added the missing downloadable SVG assets.
- Added favicon, social preview image, robots file, custom 404 page, and Vercel configuration.
- Added security headers and long-term asset caching.
- Added progressive enhancement for disabled JavaScript and unsupported IntersectionObserver.
- Added reduced-motion handling for CSS and canvas animation.
- Improved keyboard and mobile-menu accessibility.
- Removed an unverified exact BPM claim from the artist facts.

## Remaining launch checks

- Confirm the exact wording/dates of ModaLisboa, Rashomon / Zalib, and “Beatport Top 6”.
- After the final domain is assigned, add its canonical URL and absolute Open Graph URL.
- Verify the Beatport and Instagram destinations manually in the Vercel preview; automated access to those services may be blocked by their anti-bot controls.
