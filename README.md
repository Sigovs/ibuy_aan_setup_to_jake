# iBuy Luxury Cars — AAN build (handoff for JR)

The finished iBuy redesign, rebuilt on the **AAN dealer-site stack** so it drops
straight into the theme you build in. This is a **static design handoff** — HTML,
CSS and presentational JS only. No backend, no data wiring (the live theme already
has the forms / inventory / garage logic; you attach the design to it).

Open **`index.html`** in a browser to preview, or serve the folder:
`python3 -m http.server 8080` → http://localhost:8080

---

## 1. The three pages
| File | What it is |
|---|---|
| `index.html` | Homepage — hero + valuation form, US-map network, nationwide-transport, process, what-we-buy, reviews, footer |
| `about.html` | About page — also the **template** for any info page |
| `make-audi.html` | "Sell my Audi" page — the **template** for the 28 make pages (swap make name + photos) |

## 2. The stack (do not substitute)
- **Bootstrap 4.0.0**, **jQuery 3.7.1**, **Owl Carousel 2.3.4** — already compiled into
  `vendor/theme.css` + shipped in `vendor/js/` (load order jQuery → Popper → Bootstrap → Owl).
- Theming is **compile-time SCSS**, never CSS variables. (The only CSS `--vars` in the
  build are runtime values the map canvas reads — clearly commented in `custom.scss`.)

## 3. Where the brand lives — ONE file
**`scss/kit/aan-theme-kit.scss`** is the per-dealer file. Edit these blocks to re-skin:
- **Fonts** — iBuy uses Antonio (display) / Inter Tight (body) / Instrument Serif (accent) /
  JetBrains Mono (mono). The faces are **self-hosted** in `vendor/fonts/` and declared in
  `scss/_fonts.scss` (in the real theme these move into `fonts.scss`).
- **Colours** — dark base, one red accent `#DE192A` (primary + accent). Flipped from the
  kit's light default (BLOCK 2c) — iBuy is dark-first.
- **Type ramp / buttons / spacing** — squared Antonio buttons (`$btn-radius: 0`), etc.

## 4. How to build the CSS
`scss/custom.scss` → `css/custom.css`. Compile with Dart Sass:
```bash
# recommended (any OS with Node):
npx sass --load-path=scss/kit scss/custom.scss css/custom.css
# or the AAN bundled compiler (needs macOS 14+ / Windows):
#   sass --load-path=scss/kit scss/custom.scss css/custom.css
```
> Note: the AAN bundled dart-sass binary needs macOS 14+. This build was compiled with
> the Node build of Dart Sass (works on any macOS). Both produce identical CSS.

The HTML links `vendor/theme.css` first, then `css/custom.css` (custom wins). `custom.scss`
deliberately **overrides the kit's light defaults** to iBuy's dark theme via ID-qualified
rules (`#header`, `#footer`) — expected practice per the kit spec.

## 5. File map
```
index.html · about.html · make-audi.html   ← pages (kit classes + #header/#footer hooks + .container)
css/custom.css                             ← compiled (do not hand-edit; edit the SCSS)
scss/custom.scss                           ← the iBuy design, token-driven
scss/kit/aan-theme-kit.scss                ← per-dealer brand file (edit to re-skin)
scss/_fonts.scss                           ← @font-face (self-hosted)
vendor/theme.css · owl.*.css · js/*.js     ← AAN base (Bootstrap4 + theme + Owl + jQuery)
vendor/fonts/*.woff2                        ← self-hosted faces
js/home.js                                 ← homepage JS (US-map canvas, reveals, counters, animations)
assets/img/…                               ← photography
```

## 6. Conventions you'll recognise
- **Kit classes**: `.btn-1` (primary red), `.btn-3` (ghost), `.eyebrow`, `.aan-section--light`
  (the cream sections), Bootstrap `.container` for width.
- **Structural hooks**: `#header`, `#footer` target the real templates.
- **Light / dark sections**: dark is the default ground; a section gets `.aan-section--light`
  to become the warm-bone light theme (AA-verified). (This is component-level overrides, not
  CSS-var theming — dealer theming stays in `aan-theme-kit.scss`.)
- **Presentational JS** is wrapped `jQuery(function($){ … })` (the live site runs jQuery in
  noConflict mode). `js/home.js` is 3 ES modules flattened into one plain script.

## 7. Design, don't build (open items for the dev)
Static design only — attach it to the real theme's logic. Client-supplied before go-live:
real deal figures, Kansas City address, valuation-form + newsletter endpoints, hero video,
vector logo. Vehicle imagery here is real photography; never fabricate `/imagetag/` URLs.

---
Design source of truth (vanilla, for reference): Sigovs/ibuy → branch `handoff`.
