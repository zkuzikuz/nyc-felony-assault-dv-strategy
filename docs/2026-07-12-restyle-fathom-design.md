# Essay page: restyle to zarrenkuzma.com idiom + Fathom — design (2026-07-12)

## Decisions

- The page (site/, live at zarrenkuzma.com/nyc-felony-assault-crisis/) adopts the home page's minimal Inter idiom: tokens --bg #fcfcfc / --ink #18181b / --muted #71717a / --hair #d4d4d8 / --rule #e4e4e7, measure 40rem, all-Inter (Newsreader dropped), hairline link treatments (border-bottom for prose/citations, underline+offset for topbar/footer). Drop cap and accent colors removed from page chrome.
- Charts are deliberately untouched: chart-theme.js palette (orange/magenta/navy), chart JS, JSONs, and PNG fallbacks stay as-is. Chart styling is self-contained in JS; page CSS cannot affect rendered SVGs.
- CSS/JS contract: `.chart-03-grid` gap MUST stay 1.5rem (chart-03.js hardcodes 24px in panel-width math) and the grid collapses at 640px viewport (aligns with the JS's 600px figure-width threshold).
- The chart-07 ($650M beds) figure was removed: figure block, script tag, and files (js/chart-07.js, assets/charts/07-beds.png, data/chart-07.json). The $650M paragraph remains.
- Fathom (site YPUMKBBD): embed in head; delegated click tracker before </body> fires `NYC Essay: <hostname minus leading www.>` for every link click, guarded to no-op when window.fathom is absent. Expected names: zarrenkuzma.com (topbar site-mark, now a link home), data.cityofnewyork.us, vitalcitynyc.org, criminaljustice.ny.gov, fbi.gov, counciloncj.org, sciencedirect.com, pubmed.ncbi.nlm.nih.gov, nyc.gov, claude.com, github.com.
- Title shortened to "NYC's Felony-Assault Crisis | Zarren Kuzma" and `<main>` demoted to `<div class="body">` to satisfy html-validate (og/twitter titles keep the full headline).

## Deploy

- `bash tools/deploy.sh`: html-validate gate, uploads site/index.html + site/styles.css to the server dir via curl FTPS, then best-effort `DELE` of the three chart-07 orphans (failures tolerated; orphans are unreferenced). Credentials in gitignored `.deploy.env` (same host as zarrenkuzma-com, DEPLOY_URL points at the nyc-felony-assault-crisis/ subdirectory).

## Verification

- jsdom harness (scratchpad-only): static checks (no Newsreader/gtag/chart-07/old palette), DOM checks (PNG fallbacks present pre-enhancement, site-mark link), click events with stubbed fathom (exact names incl. www-strip), no-throw guard with fathom absent.
- Live checks post-deploy; owner verifies visuals + dashboard from OFF the home network (it DNS-blocks cdn.usefathom.com).
