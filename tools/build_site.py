"""Regenerate the parts of the site that are built from lists.

Run it from the repo root after adding or editing a post card in blog.html, a news item in news.html, a row of list.csv,
or PATENT_COUNT in main.js:

    python3 tools/build_site.py

blog.html stays the one place where posts are listed by hand, news.html the one place for news items, and list.csv the one
place for publications. This script writes:

    feed.xml           the site's one RSS feed: blog posts and news items, newest first
    sitemap.xml        the list of pages, for search engines
    llms.txt           a plain-text summary of the site for AI assistants
    index.html         the "From the Blog", "News" and "Recent Publications" columns (the newest 3 of each), and the
                       patent count in the bio and the description tags
    publications.html  the full publication list
    <head> of pages    a <link rel="alternate"> to feed.xml on every main page and post, so browsers and feed readers
                       find the feed from any of them

Blocks are written only between their two marker comments, so the lists are in the HTML itself: search engines, link
previews and AI assistants see them without running JavaScript. It uses the standard library only and keeps each file's
line endings as they are.

Feed readers tell items apart by their guid: a post's is its URL, and a news item's comes from its month and first
words, so changing those makes readers show the item again as new.
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
FEED_TITLE = "Fatih Bulut: Blog and News"
FEED_DESCRIPTION = "Posts on AI and security, and news of talks, papers, podcasts and other updates."
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


def rss_item(title: str, link: str, guid: str, description: str, date: datetime | None = None,
             categories: list[str] = (), permalink: bool = False) -> list[str]:
    out = ["    <item>",
           f"      <title>{escape(title)}</title>",
           f"      <link>{escape(link)}</link>",
           f'      <guid isPermaLink="{str(permalink).lower()}">{escape(guid)}</guid>']
    if date:
        out.append(f"      <pubDate>{format_datetime(date)}</pubDate>")
    out.append(f"      <description>{escape(description)}</description>")
    out += [f"      <category>{escape(name)}</category>" for name in categories]
    return out + ["    </item>"]


def feed(items: list[dict], news: list[dict]) -> str:
    """The site's one RSS feed: blog posts and news items together, newest first. A news item is dated the first of its
    month, takes its text up to the first dash or parenthesis as its title, and links to its first link."""
    dated = []
    for post in items:
        url = f'{SITE}/{post["href"]}'
        dated.append((post["date"], rss_item(post["title"], url, url, post["excerpt"], post["date"], post["tags"],
                                             permalink=True)))
    for entry in news:
        title = headline(entry["text"])
        dated.append((entry["date"], rss_item(title, entry["href"], f'news-{entry["date"]:%Y-%m}-{slug(title)}',
                                              entry["html"], entry["date"], ["News"])))
    dated.sort(key=lambda pair: pair[0], reverse=True)  # a stable sort: a post stays ahead of news from the same day
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
           "  <channel>",
           f"    <title>{escape(FEED_TITLE)}</title>",
           f"    <link>{SITE}/</link>",
           f"    <description>{escape(FEED_DESCRIPTION)}</description>",
           "    <language>en</language>",
           f'    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>',
           f"    <lastBuildDate>{format_datetime(dated[0][0])}</lastBuildDate>"]
    for _, lines in dated:
        out += lines
    guids = re.findall(r"<guid[^>]*>(.*?)</guid>", "\n".join(out))
    assert len(guids) == len(set(guids)), f"two feed items share a guid: {sorted({g for g in guids if guids.count(g) > 1})}"
    return "\n".join(out + ["  </channel>", "</rss>", ""])


def slug(text: str) -> str:
    """The first 8 words of a text, lowercase and joined by dashes."""
    return "-".join(re.findall(r"[a-z0-9]+", text.lower())[:8])


def absolute(fragment: str) -> str:
    """An HTML fragment with its relative links made absolute, as feed readers show it away from the site."""
    return re.sub(r'(href|src)="(?![a-z]+:|#)([^"]*)"', rf'\1="{SITE}/\2"', fragment)


def headline(text: str, limit: int = 120) -> str:
    """A news item as a feed title: its text up to the first dash or parenthesis, cut at a word if still long."""
    short = re.split(r"\s*—|\s+\(", text)[0].rstrip(" .,:;!")
    if len(short) > limit:
        short = short[:limit].rsplit(" ", 1)[0].rstrip(" .,:;") + "…"
    return short


def feed_links(items: list[dict]) -> None:
    """Put the feed's <link rel="alternate"> at the end of the <head> of each main page and post."""
    for name in [page or "index.html" for page in PAGES] + [post["href"] for post in items]:
        path = ROOT / name
        text, newline = read(path)
        text = re.sub(r'[ \t]*<link rel="alternate" type="application/rss\+xml"[^>]*>\n', "", text)
        head = text.split("</head>")[0]
        assert head != text, f"{name}: </head> is missing"
        indent = re.findall(r"^([ \t]*)<(?:link|meta) ", head, re.M)[-1]
        start = head.rindex("\n") + 1
        prefix = "../" * name.count("/")
        link = (f'{indent}<link rel="alternate" type="application/rss+xml" title="{html.escape(FEED_TITLE)}" '
                f'href="{prefix}feed.xml">\n')
        write(path, text[:start] + link + text[start:], newline)


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


def news_entry(item: str) -> dict:
    """One news item of news.html: its month as shown and as a date, its text, its HTML, and its first link."""
    meta = plain(re.search(r'<span class="home-row-meta">(.*?)</span>', item, re.S).group(1))
    body = re.search(r'<span class="home-row-text">(.*?)</span>\s*</li>', item, re.S).group(1)
    link = re.search(r'href="([^"]+)"', absolute(body))
    return {"meta": meta, "date": datetime.strptime(meta, "%b %Y").replace(tzinfo=timezone.utc), "text": plain(body),
            "html": absolute(" ".join(body.split())),
            "href": html.unescape(link.group(1)) if link else f"{SITE}/news.html"}


def news_block(news: list[str], indent: str) -> str:
    return "\n".join("\n".join(indent + line for line in item.split("\n")) for item in news[:LATEST_NEWS])


def llms(items: list[dict], rows: list[dict], news: list[dict]) -> str:
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
    out += [f'- {entry["meta"]}: {entry["text"]}' for entry in news]
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
    entries = [news_entry(item) for item in news]
    write(ROOT / "feed.xml", feed(items, entries))
    feed_links(items)
    write(ROOT / "sitemap.xml", sitemap(items))
    replace_between("index.html", START, END, lambda indent: latest_block(items, indent))
    replace_between("index.html", NEWS_START, NEWS_END, lambda indent: news_block(news, indent))
    replace_between("index.html", PUB_START, PUB_END, lambda indent: recent_pubs(rows, indent))
    replace_between("publications.html", PUB_START, PUB_END, lambda indent: pub_cards(rows, indent))
    sync_patents(patent_count())
    write(ROOT / "llms.txt", llms(items, rows, entries))

    print(f"{len(items)} posts, {len(news)} news items, {len(rows)} publications: wrote feed.xml, sitemap.xml, "
          f"llms.txt, the home page lists, publications.html and the feed links")


if __name__ == "__main__":
    main()
