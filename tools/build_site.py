"""Regenerate the parts of the site that list the blog posts.

Run it from the repo root after adding or editing a post card in blog.html:

    python3 tools/build_site.py

blog.html stays the one place where posts are listed by hand. This script reads its cards and writes:

    feed.xml      the RSS feed
    sitemap.xml   the list of pages, for search engines
    index.html    the "Latest Posts" block on the home page (only the lines between the two marker comments)

It uses the standard library only and keeps each file's line endings as they are.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://bulutmf.github.io"
FEED_TITLE = "Fatih Bulut: Blog"
FEED_DESCRIPTION = "Thoughts on AI, security, LLMs, and more."
LATEST = 3
PAGES = ["", "blog.html", "publications.html"]          # besides the posts
START, END = "<!-- latest-posts:start -->", "<!-- latest-posts:end -->"


def read(path: Path) -> tuple[str, str]:
    """A file's text with \\n line endings, and the line ending it uses on disk."""
    raw = path.read_bytes().decode("utf-8")
    return raw.replace("\r\n", "\n"), ("\r\n" if "\r\n" in raw else "\n")


def write(path: Path, text: str, newline: str = "\n") -> None:
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def posts() -> list[dict]:
    """The post cards of blog.html, newest first (the order they are listed in)."""
    page, _ = read(ROOT / "blog.html")
    found = []
    for card in re.findall(r'<article class="blog-card".*?</article>', page, re.S):
        def one(pattern: str) -> str:
            match = re.search(pattern, card, re.S)
            assert match, f"blog.html: a card is missing {pattern!r}"
            return html.unescape(" ".join(match.group(1).split()))

        found.append({
            "href": one(r'<a href="([^"]+)" class="blog-card-header">'),
            "date": datetime.strptime(one(r'<span class="blog-date">(.*?)</span>'), "%b %d, %Y").replace(tzinfo=timezone.utc),
            "tags": [html.unescape(t) for t in re.findall(r'<span class="blog-tag">(.*?)</span>', card)],
            "title": one(r'<h2 class="blog-card-title">(.*?)</h2>'),
            "excerpt": one(r'<p class="blog-card-excerpt">(.*?)</p>'),
        })
    assert found, "blog.html: no post cards found"
    for post in found:
        assert (ROOT / post["href"]).exists(), f'{post["href"]} is listed in blog.html but the file is missing'
    return found


def feed(items: list[dict]) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
           "  <channel>",
           f"    <title>{escape(FEED_TITLE)}</title>",
           f"    <link>{SITE}/blog.html</link>",
           f"    <description>{escape(FEED_DESCRIPTION)}</description>",
           "    <language>en</language>",
           f'    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>',
           f"    <lastBuildDate>{format_datetime(items[0]['date'])}</lastBuildDate>"]
    for post in items:
        url = f'{SITE}/{post["href"]}'
        out += ["    <item>",
                f"      <title>{escape(post['title'])}</title>",
                f"      <link>{url}</link>",
                f'      <guid isPermaLink="true">{url}</guid>',
                f"      <pubDate>{format_datetime(post['date'])}</pubDate>",
                f"      <description>{escape(post['excerpt'])}</description>"]
        out += [f"      <category>{escape(tag)}</category>" for tag in post["tags"]]
        out += ["    </item>"]
    return "\n".join(out + ["  </channel>", "</rss>", ""])


def sitemap(items: list[dict]) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    out += [f"  <url><loc>{SITE}/{page}</loc></url>" for page in PAGES]
    out += [f'  <url><loc>{SITE}/{post["href"]}</loc><lastmod>{post["date"]:%Y-%m-%d}</lastmod></url>' for post in items]
    return "\n".join(out + ["</urlset>", ""])


def latest_block(items: list[dict], indent: str) -> str:
    rows = []
    for number, post in enumerate(items[:LATEST], 1):
        date = f'{post["date"]:%b} {post["date"].day}, {post["date"].year}'
        rows += [f'{indent}<a class="pub-recent post-recent" href="{html.escape(post["href"])}">',
                 f'{indent}  <span class="pub-recent-num">{number}</span>',
                 f'{indent}  <div class="pub-recent-body">',
                 f'{indent}    <div class="pub-recent-title">{html.escape(post["title"], quote=False)}</div>',
                 f'{indent}    <div class="pub-recent-meta">',
                 f'{indent}      <span class="pub-recent-year">{date}</span>',
                 f'{indent}      <span class="pub-recent-venue">{html.escape(" · ".join(post["tags"]), quote=False)}</span>',
                 f"{indent}    </div>",
                 f"{indent}  </div>",
                 f"{indent}</a>"]
    return "\n".join(rows)


def main() -> None:
    items = posts()
    write(ROOT / "feed.xml", feed(items))
    write(ROOT / "sitemap.xml", sitemap(items))

    home, newline = read(ROOT / "index.html")
    assert home.count(START) == 1 and home.count(END) == 1, "index.html: the latest-posts markers are missing"
    before, rest = home.split(START)
    _, after = rest.split(END)
    indent = before[before.rindex("\n") + 1:]
    write(ROOT / "index.html", f"{before}{START}\n{latest_block(items, indent)}\n{indent}{END}{after}", newline)

    print(f"{len(items)} posts: wrote feed.xml, sitemap.xml and the {LATEST} latest posts on the home page")


if __name__ == "__main__":
    main()
