# CSS policy

- Put shared styling in `config/theme.py` or the shared component package.
- Use existing tokens for colors, type, spacing, surfaces, and layout.
- Do not use `nth-child()` hacks or deep DOM selectors.
- Do not add gradients, decorative shadows, large/rounded radii, or arbitrary colors.
- Keep radius zero/near-zero and surfaces restrained.
- Fix shared behavior once before adding page-specific CSS.
- If a page-specific selector is unavoidable, document why and test all pages for regressions.

