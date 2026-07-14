#!/usr/bin/env python3
"""Dependency-free pre-deploy checks for the static EPK."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]; self.links=[]; self.resources=[]; self.target_blank=[]; self.meta={}; self.canonical=None; self.title=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if tag=="a" and "href" in a:
            self.links.append(a["href"])
            if a.get("target")=="_blank": self.target_blank.append(a)
        if tag in {"script","img","source"} and "src" in a: self.resources.append(a["src"])
        if tag=="link" and "href" in a:
            self.resources.append(a["href"])
            if a.get("rel")=="canonical": self.canonical=a["href"]
        if tag=="meta":
            key=a.get("name") or a.get("property")
            if key: self.meta[key]=a.get("content","")
        if tag=="title": self.title=True

def local_path(ref):
    parsed=urlparse(ref)
    if parsed.scheme or ref.startswith(("mailto:","tel:","#")): return None
    path=unquote(parsed.path)
    if not path or path=="/": return ROOT/"index.html"
    return ROOT/path.lstrip("/") if path.startswith("/") else ROOT/path

def fail(msg, errors): errors.append(msg)

def main():
    errors=[]
    if not HTML.exists(): fail("index.html is missing",errors)
    html_text=HTML.read_text(encoding="utf-8")
    parser=AuditParser(); parser.feed(html_text)
    duplicates={x for x in parser.ids if parser.ids.count(x)>1}
    if duplicates: fail(f"Duplicate IDs: {sorted(duplicates)}",errors)
    ids=set(parser.ids)
    for link in parser.links:
        if link.startswith("#") and link[1:] not in ids: fail(f"Broken anchor target: {link}",errors)
    for ref in parser.links+parser.resources:
        p=local_path(ref)
        if p and not p.exists(): fail(f"Missing local resource: {ref}",errors)
        if ref.startswith("http://"): fail(f"Insecure HTTP reference: {ref}",errors)
    for attrs in parser.target_blank:
        rel=set((attrs.get("rel") or "").split())
        if "noopener" not in rel: fail(f"target=_blank missing noopener: {attrs.get('href')}",errors)
    required_meta=["description","author","google-site-verification","viewport","og:title","og:description","og:site_name","og:url","og:image","twitter:card","twitter:image"]
    for item in required_meta:
        if item not in parser.meta: fail(f"Missing metadata: {item}",errors)
    if parser.canonical != parser.meta.get("og:url"):
        fail("Canonical URL and og:url must match", errors)
    if parser.canonical != "https://t0n1n0.com/":
        fail("Canonical URL must point to the official t0n1n0.com domain", errors)
    for image_meta in ["og:image", "twitter:image"]:
        if not parser.meta.get(image_meta, "").startswith("https://"):
            fail(f"{image_meta} must use an absolute HTTPS URL", errors)
    if not parser.title: fail("Missing title element",errors)
    if "MAT Academy" not in html_text: fail("MAT Academy education credit is missing",errors)
    if "https://www.instagram.com/_.Vallerianiii._/" not in parser.links:
        fail("Updated Instagram profile is missing",errors)
    if "Des1gner Visual" in html_text: fail("Removed Des1gner Visual block is still present",errors)
    if "Rashomon / Zalib" in html_text: fail("Removed Rashomon / Zalib credit is still present",errors)
    if "https://youtu.be/31NhgfSfY-w" not in parser.links:
        fail("ModaLisboa 2025 video link is missing",errors)
    if '<span class="credit-year">2025</span><span class="credit-name"><a' not in html_text:
        fail("ModaLisboa 2025 credit is missing or has the wrong year",errors)
    if "observer-mask" in html_text or "observer-eyes" in html_text:
        fail("Removed face/observer visual is still present",errors)
    for required_id in ["heroPortal", "signalSequence", "signalSequenceTitle", "scrollPortal"]:
        if required_id not in ids: fail(f"Scroll-driven portal ID is missing: {required_id}",errors)
    if "updateSignalSequence" not in html_text or "--progress" not in html_text:
        fail("Scroll-driven sequence logic is missing",errors)
    if 'translate="no"><span class="contact-title-line">Enter the</span><span class="contact-title-line contact-title-outline">signal.</span>' not in html_text:
        fail("Android-safe contact title structure is missing",errors)
    if "-webkit-text-stroke: 0;" not in html_text or "text-shadow:" not in html_text:
        fail("Android-safe shadow outline fallback is missing",errors)
    if '"@type": "Person"' not in html_text or '"url": "https://t0n1n0.com/"' not in html_text:
        fail("T0N1N0 structured artist data is missing",errors)
    robots_text=(ROOT/"robots.txt").read_text(encoding="utf-8")
    sitemap_text=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
    if "https://t0n1n0.com/sitemap.xml" not in robots_text:
        fail("robots.txt does not advertise the official-domain sitemap",errors)
    if "<loc>https://t0n1n0.com/</loc>" not in sitemap_text:
        fail("sitemap.xml does not contain the official homepage",errors)
    if "t0n1n0-epk.vercel.app" in html_text + robots_text + sitemap_text:
        fail("Legacy Vercel URLs remain in indexable SEO files",errors)
    cfg=ROOT/"vercel.json"
    try: json.loads(cfg.read_text())
    except Exception as exc: fail(f"Invalid vercel.json: {exc}",errors)
    for required in [ROOT/"404.html", ROOT/"robots.txt", ROOT/"sitemap.xml", ROOT/"assets/favicon.svg", ROOT/"assets/t0n1n0-og.png", ROOT/"assets/t0n1n0-stacked-mark.svg"]:
        if not required.exists(): fail(f"Required deploy file missing: {required.relative_to(ROOT)}",errors)
    if errors:
        print("PRE-DEPLOY CHECKS FAILED")
        for e in errors: print(f"- {e}")
        return 1
    print(f"PRE-DEPLOY CHECKS PASSED ({len(parser.links)} links, {len(parser.ids)} IDs, {len(parser.resources)} local/external resources audited)")
    return 0

if __name__=="__main__": sys.exit(main())
