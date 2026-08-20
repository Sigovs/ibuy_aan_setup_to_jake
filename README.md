# iBuy Luxury Cars — AAN build

The iBuy redesign ported onto the **AAN WordPress dealer stack** so it drops into
the pipeline AAN developers build in.

## Stack (fixed)
- Bootstrap **4.0.0**, jQuery **3.7.1**, Owl Carousel **2.3.4** (compiled into `vendor/theme.css` + `vendor/js/`)
- Theming = compile-time **SCSS tokens** (no CSS custom properties)

## Where the brand lives
- **`scss/kit/aan-theme-kit.scss`** — the ONE per-dealer file. iBuy values: dark base,
  single red accent `#DE192A`, squared Antonio buttons, Antonio/Inter Tight/Instrument
  Serif/JetBrains Mono. Edit here to re-skin.
- **`scss/custom.scss`** — the iBuy design as token-driven overrides on top of the kit
  base (deliberately flips the kit's light defaults to iBuy's dark brand). Compiles to
  `css/custom.css`.

## Build
```
sass --load-path=scss/kit scss/custom.scss css/custom.css
```
(Dev team: drops into the theme as `components/*.scss` + `imports.scss`; tokens go into
`aan-theme-kit.scss`, fonts self-hosted via `fonts.scss` — the mockup names the slots.)

## Pages
- `index.html` — homepage  *(in progress)*
- `about.html` — About / template  *(in progress)*
- `make-audi.html` — make page / template  *(in progress)*

Design source of truth (vanilla): the `redesign` / `handoff` branches of Sigovs/ibuy.
