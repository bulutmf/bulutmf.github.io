"""Regenerate the parts of the site that are built from lists.

Run it from the repo root after adding or editing a post card in blog.html, a news item in news.html, a row of list.csv,
or PATENT_COUNT in main.js:

    python3 tools/build_site.py

blog.html stays the one place where posts are listed by hand, news.html the one place for news items, and list.csv the one
place for publications. This script writes:

    feed.xml           the RSS feed
    sitemap.xml        the list of pages, for search engines
    llms.txt           a plain-text summary of the site for AI assistants
    index.html         the "From the Blog", "News" and "Recent Publications" columns (the newest 3 of each), and the
                       patent count in the bio and the description tags
    publications.html  the full publication list

Blocks are written only between their two marker comments, so the lists are in the HTML itself: search engines, link
previews and AI assistants see them without running JavaScript. It uses the standard library only and keeps each file's
line endings as they are.
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
RECENT_PUBS = 3
LATEST_NEWS = 3
PAGES = ["", "research.html", "publications.html", "talks.html", "blog.html", "news.html", "projects.html"]  # besides posts
START, END = "<!-- latest-posts:start -->", "<!-- latest-posts:end -->"
PUB_START, PUB_END = "<!-- publications:start -->", "<!-- publications:end -->"
NEWS_START, NEWS_END = "<!-- news:start -->", "<!-- news:end -->"
LINKEDIN = "https://www.linkedin.com/in/fatih-bulut-18ba5511"
SCHOLAR = "https://scholar.google.com/citations?user=aUaOP48AAAAJ"


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


def home_row(indent: str, href: str, meta: str, title: str, external: bool = False) -> list[str]:
    """One row of the home page's lists, the same for posts, news and publications: a small meta line, then the title."""
    target = ' target="_blank" rel="noopener noreferrer"' if external else ""
    return [f'{indent}<a class="home-row" href="{html.escape(href)}"{target}>',
            f'{indent}  <span class="home-row-meta">{meta}</span>',
            f'{indent}  <span class="home-row-title">{title}</span>',
            f"{indent}</a>"]


def latest_block(items: list[dict], indent: str) -> str:
    rows = []
    for post in items[:LATEST]:
        date = f'{post["date"]:%b} {post["date"].day}, {post["date"].year}'
        rows += home_row(indent, post["href"], date, html.escape(post["title"], quote=False))
    return "\n".join(rows)


def publications() -> list[dict]:
    """The rows of list.csv (type;year;authors;title;venue;award), newest first, numbered as the site shows them."""
    text, _ = read(ROOT / "list.csv")
    lines = [line for line in text.strip().split("\n") if line.strip()]
    rows = []
    for index, line in enumerate(lines):
        kind, year, authors, title, venue, award = (line.split(";") + [""] * 6)[:6]
        if title:
            rows.append({"type": kind, "year": year, "authors": authors, "title": title, "venue": venue,
                         "award": award, "number": len(lines) - index})
    assert rows, "list.csv: no publications found"
    return rows


def badge_class(kind: str) -> str:
    return kind.lower().replace(" ", "", 1)


def pub_cards(rows: list[dict], indent: str) -> str:
    """Every publication as a card for publications.html. Venue, title and authors may hold HTML (links), as in list.csv."""
    out = []
    for pub in rows:
        meta = f'<span class="pub-authors">{pub["authors"]}</span>'
        if pub["venue"]:
            meta += f' · <span class="pub-venue">{pub["venue"]}</span>'
        if pub["award"]:
            meta += f'<span class="pub-award"> · \U0001F3C6 {pub["award"]}</span>'
        out += [f'{indent}<article class="pub-card" data-type="{html.escape(pub["type"])}">',
                f'{indent}  <div class="pub-header">',
                f'{indent}    <span class="pub-number">#{pub["number"]}</span>',
                f'{indent}    <span class="pub-badge {badge_class(pub["type"])}">{pub["type"]}</span>',
                f'{indent}    <span class="pub-year">{pub["year"]}</span>',
                f"{indent}  </div>",
                f'{indent}  <div class="pub-title">{pub["title"]}</div>',
                f'{indent}  <div class="pub-meta">{meta}</div>',
                f"{indent}</article>"]
    return "\n".join(out)


def short_venue(pub: dict) -> str:
    """The venue as one short line: "FSE 2026" for "... (FSE) 2026", else its text without link labels, with the year."""
    text = re.sub(r"(\s+-\s+(Arxiv|Spotify|PDF))+\s*$", "", plain(pub["venue"]))
    acronym = re.search(r"\(([A-Z][A-Za-z]*)\)\s*(\d{4})?", text)
    if acronym:
        text = f"{acronym.group(1)} {acronym.group(2) or ''}".strip()
    if not text or len(text) > 40:
        text = pub["type"]
    return text if re.search(r"\b(19|20)\d{2}\b", text) else f"{text} · {pub['year']}"


def recent_pubs(rows: list[dict], indent: str) -> str:
    """The newest publications as rows of the home page, each linking to its paper (the first link in list.csv)."""
    out = []
    for pub in rows[:RECENT_PUBS]:
        link = re.search(r'href="([^"]+)"', pub["venue"])
        href = html.unescape(link.group(1)) if link else "publications.html"
        out += home_row(indent, href, html.escape(short_venue(pub), quote=False), pub["title"], external=bool(link))
    return "\n".join(out)


def replace_between(name: str, start: str, end: str, block) -> None:
    """Rewrite the lines between two marker comments of a page; block(indent) returns the new lines."""
    path = ROOT / name
    text, newline = read(path)
    assert text.count(start) == 1 and text.count(end) == 1, f"{name}: the {start} / {end} markers are missing"
    before, rest = text.split(start)
    _, after = rest.split(end)
    indent = before[before.rindex("\n") + 1:]
    write(path, f"{before}{start}\n{block(indent)}\n{indent}{end}{after}", newline)


def patent_count() -> int:
    text, _ = read(ROOT / "main.js")
    match = re.search(r"var PATENT_COUNT = (\d+);", text)
    assert match, "main.js: var PATENT_COUNT = <number>; is missing"
    return int(match.group(1))


def sync_patents(count: int) -> None:
    """Write the patent count into the bios and description tags ("48+ patents"), so it does not depend on JavaScript."""
    for name in ("index.html", "talks.html"):
        path = ROOT / name
        text, newline = read(path)
        text, spans = re.subn(r'(<span id="patent-text">)[^<]*(</span>)', rf"\g<1>{count}+\g<2>", text)
        text, counts = re.subn(r"\d+\+(\s+)patents", rf"{count}+\g<1>patents", text)
        assert spans + counts, f"{name}: no patent count found to update"
        write(path, text, newline)


def plain(fragment: str) -> str:
    """Text of an HTML fragment on one line."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).replace(" ,", ",").replace(" .", ".").replace(" —", "—").split())


def news_items() -> list[str]:
    """The news items of news.html, newest first: each <li class="home-row"> between the news markers, unindented."""
    page, _ = read(ROOT / "news.html")
    assert page.count(NEWS_START) == 1 and page.count(NEWS_END) == 1, "news.html: the news markers are missing"
    region = page.split(NEWS_START)[1].split(NEWS_END)[0]
    found = []
    for item in re.findall(r'[ \t]*<li class="home-row">.*?</li>', region, re.S):
        lines = item.split("\n")
        cut = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
        found.append("\n".join(line[cut:] for line in lines))
    assert found, "news.html: no news items found"
    return found


def news_block(news: list[str], indent: str) -> str:
    return "\n".join("\n".join(indent + line for line in item.split("\n")) for item in news[:LATEST_NEWS])


def llms(items: list[dict], rows: list[dict], news: list[str]) -> str:
    """llms.txt (llmstxt.org): who he is, the pages, every post and publication, as links with one-line notes."""
    home, _ = read(ROOT / "index.html")
    role = plain(re.search(r'<p class="bio-role">(.*?)</p>', home, re.S).group(1))
    bio = [plain(p) for p in re.findall(r'<p class="bio-text"[^>]*>(.*?)</p>', home, re.S)]
    out = ["# Fatih Bulut", "", f"> {role}.", ""]
    for paragraph in bio:
        out += [paragraph, ""]
    out += ["## Pages", "",
            f"- [Home]({SITE}/): bio, news, latest posts and recent publications",
            f"- [Research]({SITE}/research.html): selected recent work in security and AI, newest first, with patents and papers",
            f"- [Talks]({SITE}/talks.html): talks, podcasts and speaker bios",
            f"- [Publications]({SITE}/publications.html): papers, preprints and articles",
            f"- [Blog]({SITE}/blog.html): essays on AI and security",
            f"- [News]({SITE}/news.html): talks, papers, podcasts and other updates, newest first",
            f"- [Projects archive]({SITE}/projects.html): research projects from IBM Research",
            "", "## News", ""]
    for item in news:
        meta = plain(re.search(r'<span class="home-row-meta">(.*?)</span>', item, re.S).group(1))
        text = plain(re.search(r'<span class="home-row-text">(.*?)</span>\s*</li>', item, re.S).group(1))
        out.append(f"- {meta}: {text}")
    out += ["", "## Posts", ""]
    out += [f'- [{post["title"]}]({SITE}/{post["href"]}): {post["excerpt"]} ({post["date"]:%Y-%m-%d})' for post in items]
    out += ["", "## Publications", ""]
    for pub in rows:
        link = re.search(r'href="([^"]+)"', pub["venue"])
        venue = re.sub(r"(\s+-\s+(Arxiv|Spotify|PDF))+\s*$", "", plain(pub["venue"]))
        out.append(f'- [{plain(pub["title"])}]({link.group(1) if link else SITE + "/publications.html"}): '
                   f'{plain(pub["authors"])}. {pub["type"]}, {pub["year"]}' + (f". {venue}" if venue else ""))
    out += ["", "## Elsewhere", "", f"- [LinkedIn]({LINKEDIN})", f"- [Google Scholar]({SCHOLAR})", ""]
    return "\n".join(out)


def main() -> None:
    items = posts()
    rows = publications()
    news = news_items()
    write(ROOT / "feed.xml", feed(items))
    write(ROOT / "sitemap.xml", sitemap(items))
    replace_between("index.html", START, END, lambda indent: latest_block(items, indent))
    replace_between("index.html", NEWS_START, NEWS_END, lambda indent: news_block(news, indent))
    replace_between("index.html", PUB_START, PUB_END, lambda indent: recent_pubs(rows, indent))
    replace_between("publications.html", PUB_START, PUB_END, lambda indent: pub_cards(rows, indent))
    sync_patents(patent_count())
    write(ROOT / "llms.txt", llms(items, rows, news))

    print(f"{len(items)} posts, {len(news)} news items, {len(rows)} publications: wrote feed.xml, sitemap.xml, llms.txt, "
          f"the home page lists and publications.html")


if __name__ == "__main__":
    main()
