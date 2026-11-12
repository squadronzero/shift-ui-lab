"""SHIFT UI lab helpers (no network, standard library only).

  python3 scripts/lab.py refs "main ui/lab-a"          -> one "ref slug" line per branch, or exit 2
  python3 scripts/lab.py mark DIST/index.html --ref R --sha S --live URL
  python3 scripts/lab.py index SITE_DIR --live URL --built "ref slug sha" ...

The preview is never the official site: every page is marked (title, a label the viewer can hide,
noindex) and the root page says where the official site is.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

MAX_REFS = 3                       # one site holds every variant: about 180 MB each, Pages allows 1 GB
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,59}$")
MARK = "<!-- shift-ui-lab -->"


def slug(ref: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", ref.lower()).strip("-")


def parse_refs(text: str) -> list[tuple[str, str]]:
    refs = text.replace(",", " ").split()
    if not refs:
        raise ValueError("give at least one branch")
    if len(refs) > MAX_REFS:
        raise ValueError(f"at most {MAX_REFS} branches per preview")
    out, seen = [], set()
    for r in refs:
        if not REF_RE.match(r) or ".." in r or r.endswith((".lock", "/")):
            raise ValueError(f"not a branch name: {r!r}")
        s = slug(r)
        if s in seen:
            raise ValueError(f"two branches give the same folder name: {s}")
        seen.add(s)
        out.append((r, s))
    return out


def label_html(ref: str, sha: str, live: str) -> str:
    r, s, l = html.escape(ref), html.escape(sha), html.escape(live, quote=True)
    return f"""{MARK}
<div id="lab-flag" role="note" title="Design preview, not the official SHIFT site ({l})" style="position:fixed;top:6px;right:6px;z-index:2147483647;display:flex;gap:2px;align-items:center;white-space:nowrap;padding:3px 3px 3px 10px;border-radius:999px;background:#7a1f1f;color:#fff;font:600 11px/1.2 system-ui,sans-serif;box-shadow:0 1px 4px rgba(0,0,0,.45)">
<span>PREVIEW &middot; {r} &middot; {s}</span>
<button type="button" aria-label="Hide the preview label" style="all:unset;cursor:pointer;min-width:28px;min-height:28px;display:grid;place-items:center;border-radius:999px">&#x2715;</button>
</div>
<script>(function(){{var f=document.getElementById('lab-flag');
f.querySelector('button').onclick=function(){{f.remove();}};}})();</script>
"""


def mark(index: Path, ref: str, sha: str, live: str) -> None:
    text = index.read_text(encoding="utf-8")
    if MARK in text:
        raise SystemExit(f"{index} is already marked")
    if text.count("</head>") != 1 or text.count("</body>") != 1 or "<title>" not in text:
        raise SystemExit(f"{index}: unexpected page shape")
    text = text.replace("<title>", "<title>[Preview] ", 1)
    text = text.replace("</head>", '  <meta name="robots" content="noindex, nofollow" />\n  </head>', 1)
    text = text.replace("</body>", label_html(ref, sha, live) + "  </body>", 1)
    index.write_text(text, encoding="utf-8")


def index_page(site: Path, live: str, built: list[tuple[str, str, str]]) -> None:
    rows = "\n".join(
        f'<li><a href="./{html.escape(s)}/">{html.escape(r)}</a> <small>commit {html.escape(h)}</small></li>'
        for r, s, h in built)
    l = html.escape(live, quote=True)
    site.joinpath("index.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex, nofollow" /><title>SHIFT UI lab (preview)</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:40rem;margin:2rem auto;padding:0 1rem;color:#17283a}}
li{{margin:.6rem 0}}a{{font-weight:600}}.note{{background:#fbeaea;border-left:4px solid #7a1f1f;padding:.6rem .9rem}}</style></head>
<body><h1>SHIFT UI lab</h1>
<p class="note">Design previews for team feedback. These are <strong>not</strong> the official SHIFT site and are not
for judging. The official site is <a href="{l}">{l}</a>.</p>
<h2>Variants in this preview</h2><ul>
{rows}
</ul><p><small>All variants use the same data: the official site data release and a copy of the
official site's recent detections at build time.</small></p></body></html>
""", encoding="utf-8")
    site.joinpath("robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("refs"); a.add_argument("text")
    m = sub.add_parser("mark"); m.add_argument("index", type=Path)
    m.add_argument("--ref", required=True); m.add_argument("--sha", required=True); m.add_argument("--live", required=True)
    i = sub.add_parser("index"); i.add_argument("site", type=Path); i.add_argument("--live", required=True)
    i.add_argument("--built", nargs="+", required=True, help='"ref slug sha" per variant')
    args = p.parse_args(argv)
    if args.cmd == "refs":
        try:
            for r, s in parse_refs(args.text):
                print(r, s)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    elif args.cmd == "mark":
        mark(args.index, args.ref, args.sha, args.live)
    else:
        index_page(args.site, args.live, [tuple(b.split()) for b in args.built])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
