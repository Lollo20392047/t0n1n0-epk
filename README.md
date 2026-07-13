# T0N1N0 — Electronic Press Kit

Static, dependency-free EPK for T0N1N0.

The visual system is built around binary contrast: a black/white display
wordmark, a cursor-reactive abstract portal, falling binary type, a native
scroll-driven 0 → 1 sequence, and a stacked T0 / N1 / N0 mark. Touch swipes
scrub the same sequence, while motion automatically reduces when requested by
the device.

Production: <https://t0n1n0-epk.vercel.app/>

## Local preview

```bash
python3 -m http.server 4173
```

Open `http://localhost:4173`.

## Checks

```bash
python3 tests/smoke_test.py
```

## Vercel

Import the repository with the **Other** framework preset. The site is served
directly from the repository root, so no build command, install command, output
directory, environment variables, or custom Root Directory are required.

## Editorial checks

Before promoting new copy, confirm the wording and dates for ModaLisboa,
Rashomon / Zalib, and the Beatport Top 6 credit.
