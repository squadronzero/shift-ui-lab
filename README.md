# SHIFT UI lab

Design previews of the SHIFT website for Team Squadron Zero's feedback. **Not the official site, and
not for judging.** The official site is https://squadronzero.github.io/squadron-zero/.

Preview link: https://squadronzero.github.io/shift-ui-lab/

## How it works

- A UI idea lives on a branch of the app repo `squadronzero/squadron-zero`, named `ui/lab-<name>`
  (for example `ui/lab-a`). Branches never change the official site: it builds from `main` only.
- **Actions → Preview → Run workflow** here, with 1 to 3 branch names separated by spaces (for
  example `main ui/lab-a ui/lab-b`). After about 5 minutes the preview link lists each one, so the
  team can open them on phones side by side.
- Each run replaces the previous preview.

## What the preview uses

- The branch's code as it is.
- The same historical data as the official site (the public release `site-data`).
- A copy of the recent detections the official site serves at build time. No FIRMS key is used,
  and this repo has no secrets at all. If the copy fails its check, recent detections show
  "not available", as they would on the official site.

## Safety

- This repo only reads public things from the app repo. It never writes to it.
- Every preview page is titled `[Preview]`, carries a red `PREVIEW · branch · commit` label (the ✕
  hides it on that page only, and it comes back every time a page is opened), and is set to `noindex` with a `robots.txt` that blocks indexing.

## From preview to the official site

A chosen design reaches the official site only by the normal review flow in the app repo: a pull
request from its `ui/lab-*` branch into `main`, the tutor checks, then "merge". The baseline check
(`python docs/preflight/verify_baseline.py`) must still print UNCHANGED, so UI work stays out of
`web/src/lib`, `pipeline/` and `config/`.

## Files

- `.github/workflows/preview.yml`: the build and deploy.
- `scripts/lab.py`: checks branch names and marks pages as previews. Tests:
  `python3 scripts/test_lab.py`.
