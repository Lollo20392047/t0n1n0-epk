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
    parser=AuditParser(); parser.feed(HTML.read_text(encoding="utf-8"))
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
    required_meta=["description","viewport","og:title","og:description","og:url","og:image","twitter:card","twitter:image"]
    for item in required_meta:
        if item not in parser.meta: fail(f"Missing metadata: {item}",errors)
    if parser.canonical != parser.meta.get("og:url"):
        fail("Canonical URL and og:url must match", errors)
    for image_meta in ["og:image", "twitter:image"]:
        if not parser.meta.get(image_meta, "").startswith("https://"):
            fail(f"{image_meta} must use an absolute HTTPS URL", errors)
    if not parser.title: fail("Missing title element",errors)
    cfg=ROOT/"vercel.json"
    try: json.loads(cfg.read_text())
    except Exception as exc: fail(f"Invalid vercel.json: {exc}",errors)
    for required in [ROOT/"404.html", ROOT/"robots.txt", ROOT/"sitemap.xml", ROOT/"assets/favicon.svg", ROOT/"assets/t0n1n0-og.png"]:
        if not required.exists(): fail(f"Required deploy file missing: {required.relative_to(ROOT)}",errors)
    if errors:
        print("PRE-DEPLOY CHECKS FAILED")
        for e in errors: print(f"- {e}")
        return 1
    print(f"PRE-DEPLOY CHECKS PASSED ({len(parser.links)} links, {len(parser.ids)} IDs, {len(parser.resources)} local/external resources audited)")
    return 0

if __name__=="__main__": sys.exit(main())
