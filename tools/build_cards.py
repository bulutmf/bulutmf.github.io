"""Make the link preview image of every post, and point each post at its image.

Run it from the repo root after adding a post or changing a title:

    python3 tools/build_cards.py            # every post
    python3 tools/build_cards.py jev-thoughts   # one post, by file name without .html

For each post card in blog.html it draws a 1200 x 630 image (title, an optional one-line subtitle, the tags or a small copy of
the post's chart, the site name) and saves it as images/cards/<post>.png. It then makes sure the post's <head> names that image, so a link
pasted into LinkedIn, X or Slack shows it as a large card.

The image is drawn by Google Chrome running without a window, so Chrome must be installed. Standard library only.
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from build_site import ROOT, SITE, posts, read, write

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "images" / "cards"
WIDTH, HEIGHT = 1200, 630

PAGE = """<!doctype html>
<meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@400;500&display=block">
<style>
  html, body {{ margin: 0; width: {width}px; height: {height}px; overflow: hidden; }}
  body {{ box-sizing: border-box; padding: 84px 80px 64px; background: #f8fafc; color: #171c22;
         font-family: "Atkinson Hyperlegible", Helvetica, Arial, sans-serif; display: flex; flex-direction: column; }}
  .rule {{ width: 96px; height: 8px; background: #0e7c86; }}
  h1 {{ margin: 36px 0 0; font-size: {size}px; line-height: 1.08; font-weight: 700; letter-spacing: -0.01em;
        max-width: 1040px; text-wrap: balance; }}
  .sub {{ margin: 26px 0 0; font-size: 32px; line-height: 1.35; color: #5c6670; max-width: 900px; text-wrap: balance; }}
  .foot {{ margin-top: auto; display: flex; align-items: flex-end; justify-content: space-between; gap: 40px; }}
  .tags, .site {{ font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; font-size: 26px; }}
  .tags {{ color: #0e7c86; display: flex; flex-wrap: wrap; gap: 4px 28px; }}
  .site {{ color: #5c6670; white-space: nowrap; }}
  svg {{ display: block; }}
</style>
<div class="rule"></div>
<h1>{title}</h1>
{subtitle}
<div class="foot">{left}<div class="site">Fatih Bulut · bulutmf.github.io</div></div>
"""


def title_size(title: str) -> int:
    for limit, size in ((24, 88), (36, 76), (52, 66), (70, 58)):
        if len(title) <= limit:
            return size
    return 50


def subtitle_of(page: str) -> str:
    """The first sentence of the post's subtitle, when it has one."""
    match = re.search(r'<p class="post-deck">(.*?)</p>', page, re.S)
    if not match:
        return ""
    text = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
    first = re.match(r".*?[.?!](?=\s|$)", text)
    return first.group(0) if first else text


def bars_of(page: str) -> str:
    """A small copy of the post's bar chart, when it has one: pairs of bars in the chart's two colours."""
    heights = [(kind, float(h)) for kind, h in re.findall(r'<rect class="bar-(a|b)"[^>]*height="([\d.]+)" rx=', page)]
    if len(heights) < 4:
        return ""
    top = max(h for _, h in heights)
    out, x = [], 0
    for index, (kind, value) in enumerate(heights):
        h = round(value / top * 100)
        out.append(f'<rect x="{x}" y="{100 - h}" width="34" height="{h}" rx="4" fill="{"#2a78d6" if kind == "a" else "#eb6834"}"/>')
        x += 42 if index % 2 == 0 else 88
    return (f'<svg width="{x - 54}" height="102" viewBox="0 0 {x - 54} 102">{"".join(out)}'
            f'<rect x="0" y="100" width="{x - 54}" height="2" fill="#dbe3ec"/></svg>')


def draw(post: dict, work: Path) -> Path:
    page, _ = read(ROOT / post["href"])
    sub = subtitle_of(page)
    left = bars_of(page) or '<div class="tags">' + "".join(f"<span>{html.escape(tag)}</span>" for tag in post["tags"]) + "</div>"
    card = work / "card.html"
    # a hyphenated word such as "Weight-Space" stays on one line
    title = " ".join(f'<span style="white-space: nowrap">{html.escape(word)}</span>' if "-" in word else html.escape(word)
                     for word in post["title"].split())
    card.write_text(PAGE.format(width=WIDTH, height=HEIGHT, size=title_size(post["title"]), title=title,
                                subtitle=f'<p class="sub">{html.escape(sub)}</p>' if sub else "", left=left), encoding="utf-8")
    target = OUT / (Path(post["href"]).stem + ".png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={WIDTH},{HEIGHT}", "--virtual-time-budget=8000", f"--user-data-dir={work / 'profile'}",
                    f"--screenshot={target}", card.as_uri()], check=True, capture_output=True, timeout=120)
    assert target.exists() and target.stat().st_size > 5000, f"{target} was not drawn"
    return target


def point_at(post: dict) -> None:
    """Make the post's <head> name its card. Safe to run again: earlier image tags are replaced."""
    path = ROOT / post["href"]
    page, newline = read(path)
    page = re.sub(r'\n\s*<meta property="og:image[^>]*>', "", page)
    url = f'{SITE}/images/cards/{path.stem}.png'
    tags = (f'\n  <meta property="og:image" content="{url}">'
            f'\n  <meta property="og:image:width" content="{WIDTH}">'
            f'\n  <meta property="og:image:height" content="{HEIGHT}">'
            f'\n  <meta property="og:image:alt" content="{html.escape(post["title"])}">')
    anchor = re.search(r'\n\s*<meta property="og:url"[^>]*>', page) or re.search(r'\n\s*<meta property="og:type"[^>]*>', page)
    assert anchor, f"{path.name}: no og:url or og:type tag to put the image tags after"
    page = page[:anchor.end()] + tags + page[anchor.end():]
    page = page.replace('<meta name="twitter:card" content="summary">', '<meta name="twitter:card" content="summary_large_image">')
    write(path, page, newline)


def main() -> None:
    wanted = set(sys.argv[1:])
    items = [p for p in posts() if not wanted or Path(p["href"]).stem in wanted]
    assert items, f"no post matches {sorted(wanted)}"
    assert Path(CHROME).exists(), f"Google Chrome was not found at {CHROME}"
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for post in items:
            target = draw(post, Path(tmp))
            point_at(post)
            print(f"{target.relative_to(ROOT)}  {target.stat().st_size // 1024} KB")
    print(f"{len(items)} cards drawn; each post now names its card")


if __name__ == "__main__":
    main()
