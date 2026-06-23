# Simon Hamra — Portfolio

My personal website. It shows who I am, the data projects I built at Boston
University, my CV, and how to reach me. Built with [Quarto](https://quarto.org)
and a custom dark theme.

**Live site:** https://simonhamra.github.io/AD688-Portfolio-Website/

## What is inside

| Page | File | What it is |
|---|---|---|
| Home | `index.qmd` | Hero, the three selected projects, quick stats |
| About | `about.qmd` | My story, from marketing to machine learning |
| Projects | `projects.qmd` | Three case studies built on Lightcast job data |
| CV | `cv.qmd` | Summary plus a downloadable PDF |
| Contact | `contact.qmd` | Email and links |

The three projects come from my AD688 course at BU. They use the Lightcast job
postings data with PySpark, Spark SQL, and machine learning.

## Design

- Dark theme only, near black background, `Geist Mono` everywhere.
- One accent: indigo `#4F46E5` with a cyan `#22D3EE` data glow. No pink.
- The hero chart and all project charts are built from the real Lightcast data
  in `make_charts.py`.
- `theme.scss` sets the Bootstrap defaults, `styles.css` holds the components.

## Build it locally

```bash
quarto preview      # live preview while editing
quarto render       # build the static site into _site/
```

The site does not run any code at build time. The charts and the CV PDF are
pre-built and committed, so rendering only needs Quarto.

Rebuild the assets only if you change them:

```bash
python make_charts.py                       # charts -> assets/charts/
quarto render _cv-source.qmd --to typst     # CV PDF source -> move to assets/cv/
```

## Deploy to GitHub Pages

Two ways:

1. **GitHub Actions (recommended).** The workflow in
   `.github/workflows/publish.yml` builds and deploys on every push to `main`.
   In the repo, go to **Settings → Pages → Build and deployment → Source:
   GitHub Actions**. That is all.

2. **One command.** From my machine:
   ```bash
   quarto publish gh-pages
   ```
