#!/usr/bin/env python3
"""Sync new Notion entries (Talent Pool, FCP projects) into the studiomalibu.de site arrays.

Mechanical half of the Notion -> website sync pipeline. This script never commits, pushes,
or opens a PR by itself, and never makes a content-judgment call -- it only:

  1. fetches candidate rows from the two Notion databases (gate field == "NO"),
  2. maps them onto the site JSON schemas,
  3. runs structural validation (required fields, known enum values, URL reachability,
     image sanity),
  4. downloads + processes any poster/photo (existing sharp+blur convention),
  5. writes a JSON report describing what it would add and any validation flags.

The caller (a Claude Code task, see plan) reads the report, does the content-plausibility
judgment on free-text fields, and -- for entries it accepts -- calls this script again with
--apply to actually rewrite the HTML arrays, then handles git branch/commit/push/PR/marking
the Notion rows as synced itself.

See /Users/knut/.claude/plans/floating-greeting-pillow.md for the full design.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from PIL import Image, ImageEnhance, ImageFilter

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_HTML = REPO_ROOT / "projects" / "index.html"
EXPERTS_HTML = REPO_ROOT / "experts" / "index.html"
POSTERS_DIR = REPO_ROOT / "projects" / "posters"
POSTERS_BLUR_DIR = POSTERS_DIR / "blur"

TOKEN_FILE = Path.home() / ".malibu_credentials" / "notion_website_sync_token.txt"
NOTION_VERSION = "2022-06-28"
NOTION_API = "https://api.notion.com/v1"

# From reference_studiomalibu_site_notion_sources.md. These are the Notion *page* ids for
# the two databases with dashes inserted; NOT yet live-verified against the REST API (needs
# a real token -- see plan Verification step 1). If /v1/databases/{id}/query 404s, check
# whether Notion's Data Sources API wants a different id for this workspace.
PROJECTS_DB_ID = "c902a5be-2374-4862-aa9a-a0997dbd1d03"
TALENT_DB_ID = "2098-6489-2e5d-4c5e-8dfeafcd52694cc3"  # NB: verify dash placement live

PROJECTS_GATE_PROPERTY = "On Website"
TALENT_GATE_PROPERTY = "Review Status"

# Enum values currently used by the site's filter UI (from live-data analysis). An entry
# with a value outside this set still gets included -- it just gets flagged, because
# silently dropping someone's project/role is worse than a slightly-off filter.
PROJECT_TYPE_VALUES = {
    "Commercial", "Documentary", "Feature Film - Cinema", "Feature Film - Streamer",
    "Mini Series", "Music video", "Series - Streamer", "Short Film", "TV Movie",
    "TV Series",
}
CONTINENT_VALUES = {
    "Africa", "Asia", "Europe", "North America", "Oceania", "South America",
}
ROLE_VALUES = {"Editor", "Assistant Editor", "VFX Editor", "Workflow Builder"}
CONTENT_TYPE_VALUES = {"Narrative", "Commercials", "Music Videos", "Documentaries", "Social"}

# Country name -> flag emoji, for the small set actually seen in PROJECTS today. Extend as
# new countries show up (a missing entry is a validation flag, not a crash).
COUNTRY_FLAGS = {
    "Germany": "🇩🇪", "United States": "🇺🇸", "United Kingdom": "🇬🇧", "France": "🇫🇷",
    "Spain": "🇪🇸", "Italy": "🇮🇹", "Austria": "🇦🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Greece": "🇬🇷", "Portugal": "🇵🇹",
}

BLUR_RESIZE_FACTOR = 1.15
BLUR_RADIUS = 25
BLUR_BRIGHTNESS = 0.54


@dataclass
class Flag:
    field: str
    message: str


@dataclass
class SyncCandidate:
    kind: str  # "project" | "talent"
    notion_page_id: str
    entry: dict[str, Any]
    flags: list[Flag] = field(default_factory=list)

    def to_report_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "notion_page_id": self.notion_page_id,
            "entry": self.entry,
            "flags": [f"{f.field}: {f.message}" for f in self.flags],
        }


def load_token() -> str:
    if not TOKEN_FILE.exists():
        sys.exit(
            f"Kein Notion-Token gefunden unter {TOKEN_FILE}.\n"
            "Knut muss zuerst eine eigene Notion-Integration ('Studio Malibu Website Sync') "
            "anlegen, sie fuer 'FCP Talent Pool' und 'FCP projects around the world' "
            "freigeben, und den Token (Format 'TOKEN:ntn_...') in diese Datei legen "
            "(chmod 600)."
        )
    raw = TOKEN_FILE.read_text().strip()
    return raw.split(":", 1)[1] if ":" in raw else raw


def notion_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def query_database(token: str, database_id: str, gate_property: str) -> list[dict[str, Any]]:
    """Return all pages where gate_property (a checkbox) is unchecked."""
    url = f"{NOTION_API}/databases/{database_id}/query"
    payload = {"filter": {"property": gate_property, "checkbox": {"equals": False}}}
    results: list[dict[str, Any]] = []
    while True:
        resp = requests.post(url, headers=notion_headers(token), json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        results.extend(data["results"])
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results


def prop_text(page: dict, name: str) -> str:
    prop = page.get("properties", {}).get(name)
    if not prop:
        return ""
    t = prop.get("type")
    if t == "title":
        return "".join(r["plain_text"] for r in prop["title"]).strip()
    if t == "rich_text":
        return "".join(r["plain_text"] for r in prop["rich_text"]).strip()
    if t == "url":
        return prop.get("url") or ""
    if t == "email":
        return prop.get("email") or ""
    if t == "number":
        return prop.get("number")
    if t == "checkbox":
        return prop.get("checkbox")
    if t == "select":
        sel = prop.get("select")
        return sel["name"] if sel else ""
    if t == "multi_select":
        return [o["name"] for o in prop.get("multi_select", [])]
    return ""


def prop_files(page: dict, name: str) -> list[dict]:
    prop = page.get("properties", {}).get(name)
    if not prop or prop.get("type") != "files":
        return []
    return prop.get("files", [])


def slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug or "untitled"


def download_file(url: str) -> bytes:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def process_poster(image_bytes: bytes, slug: str) -> list[Flag]:
    """Write projects/posters/<slug>.jpg (sharp) + projects/posters/blur/<slug>.jpg."""
    flags: list[Flag] = []
    try:
        img = Image.open(__import__("io").BytesIO(image_bytes))
        img.load()
    except Exception as exc:  # noqa: BLE001 - want any decode failure reported as a flag
        return [Flag("poster", f"Bild laesst sich nicht dekodieren: {exc}")]

    if img.width < 300 or img.height < 300:
        flags.append(Flag("poster", f"Ungewoehnlich klein ({img.width}x{img.height})"))

    img = img.convert("RGB")
    sharp_path = POSTERS_DIR / f"{slug}.jpg"
    img.save(sharp_path, "JPEG", quality=90)

    blurred = img.resize(
        (int(img.width * BLUR_RESIZE_FACTOR), int(img.height * BLUR_RESIZE_FACTOR))
    )
    blurred = blurred.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))
    blurred = ImageEnhance.Brightness(blurred).enhance(BLUR_BRIGHTNESS)
    blur_path = POSTERS_BLUR_DIR / f"{slug}.jpg"
    blurred.save(blur_path, "JPEG", quality=85)

    return flags


def check_url(url: str, field_name: str) -> Flag | None:
    if not url:
        return None
    try:
        resp = requests.head(url, timeout=8, allow_redirects=True)
        if resp.status_code >= 400:
            return Flag(field_name, f"HTTP {resp.status_code} bei HEAD-Request")
    except requests.RequestException as exc:
        return Flag(field_name, f"nicht erreichbar: {exc}")
    return None


def map_project(page: dict) -> SyncCandidate:
    title = prop_text(page, "Project Name") or ""
    country = prop_text(page, "Country") or ""
    # "Country" select values in this DB are plain names; flag emoji looked up separately
    # rather than parsed out of the select label (see COUNTRY_FLAGS).
    years = prop_text(page, "Year of Release")
    year = years[0] if isinstance(years, list) and years else (years or "")
    genre = prop_text(page, "Genre")
    entry = {
        "title": title,
        "poster": "",  # filled in after image processing, if any
        "year": str(year),
        "type": prop_text(page, "Type of show") or "",
        "country": country,
        "flag": COUNTRY_FLAGS.get(country, ""),
        "continent": prop_text(page, "Continent") or "",
        "director": prop_text(page, "Director(s)") or "",
        "editor": prop_text(page, "Editor(s)") or "",
        "assistant": prop_text(page, "Assistant Editor(s)") or "",
        "production": prop_text(page, "Production Company") or "",
        "distributor": prop_text(page, "Distributor (or client for commercials)") or "",
        "genre": genre if isinstance(genre, list) else ([genre] if genre else []),
        "award": prop_text(page, "Award(s)") or "",
        "nomination": prop_text(page, "Nomination(s)") or "",
        "imdb": prop_text(page, "imdb") or "",
    }
    c = SyncCandidate(kind="project", notion_page_id=page["id"], entry=entry)

    if not title:
        c.flags.append(Flag("title", "fehlt"))
    if entry["type"] and entry["type"] not in PROJECT_TYPE_VALUES:
        c.flags.append(Flag("type", f"unbekannter Wert '{entry['type']}', nicht in Filter-UI"))
    if entry["continent"] and entry["continent"] not in CONTINENT_VALUES:
        c.flags.append(Flag("continent", f"unbekannter Wert '{entry['continent']}'"))
    if not entry["flag"] and country:
        c.flags.append(Flag("flag", f"kein Emoji fuer Land '{country}' hinterlegt, COUNTRY_FLAGS ergaenzen"))
    for f in (
        check_url(entry["imdb"], "imdb"),
        check_url(prop_text(page, "Link to Trailer or Streaming platform"), "trailer"),
    ):
        if f:
            c.flags.append(f)

    files = prop_files(page, "Poster")
    if files:
        file_obj = files[0]
        url = file_obj.get("file", {}).get("url") or file_obj.get("external", {}).get("url")
        if url:
            slug = slugify(title)
            try:
                img_bytes = download_file(url)
                c.flags.extend(process_poster(img_bytes, slug))
                entry["poster"] = f"{slug}.jpg"
            except Exception as exc:  # noqa: BLE001
                c.flags.append(Flag("poster", f"Download fehlgeschlagen: {exc}"))
    else:
        c.flags.append(Flag("poster", "kein Poster-File in Notion hinterlegt"))

    return c


def map_talent(page: dict) -> SyncCandidate:
    name = prop_text(page, "Name") or ""
    roles = prop_text(page, "Role")
    content_types = prop_text(page, "Content Types")
    languages = prop_text(page, "Languages")
    other_lang = prop_text(page, "Other language(s)")
    lang_parts = (languages if isinstance(languages, list) else []) + (
        [other_lang] if other_lang else []
    )
    entry = {
        "name": name,
        "roles": roles if isinstance(roles, list) else ([roles] if roles else []),
        "country": prop_text(page, "Country / Region") or "",
        "years": prop_text(page, "Years with FCP") or 0,
        "remote": bool(prop_text(page, "Remote capable")),
        "ownSystem": bool(prop_text(page, "Has own edit system")),
        "showContact": bool(prop_text(page, "Show contact publicly")),
        "email": prop_text(page, "Email") or "",
        # "Website / Portfolio" preferred; falls back to "Full Filmography Link" if the
        # portfolio field is empty -- the site schema only has one `website` slot.
        "website": prop_text(page, "Website / Portfolio") or prop_text(page, "Full Filmography Link") or "",
        "languages": ", ".join(lang_parts),
        "resume": prop_text(page, "Resume / Filmography") or "",
    }
    if isinstance(content_types, list) and content_types:
        entry["contentTypes"] = content_types

    c = SyncCandidate(kind="talent", notion_page_id=page["id"], entry=entry)

    if not name:
        c.flags.append(Flag("name", "fehlt"))
    if entry["showContact"] and not entry["email"] and not entry["website"]:
        c.flags.append(Flag("showContact", "Kontakt soll oeffentlich sein, aber weder Email noch Website vorhanden"))
    for role in entry["roles"]:
        if role not in ROLE_VALUES:
            c.flags.append(Flag("roles", f"unbekannter Wert '{role}', nicht in Filter-UI"))
    for ct in entry.get("contentTypes", []):
        if ct not in CONTENT_TYPE_VALUES:
            c.flags.append(Flag("contentTypes", f"unbekannter Wert '{ct}'"))
    for f in (check_url(entry["website"], "website"),):
        if f:
            c.flags.append(f)

    return c


def build_report(candidates: list[SyncCandidate]) -> dict[str, Any]:
    return {
        "candidate_count": len(candidates),
        "flagged_count": sum(1 for c in candidates if c.flags),
        "candidates": [c.to_report_dict() for c in candidates],
    }


def apply_entries(candidates: list[SyncCandidate]) -> None:
    """Append accepted entries into the live HTML arrays. Called by the caller (Claude
    step) only for candidates it has accepted after the plausibility pass -- this function
    itself does not filter anything."""
    projects = [c for c in candidates if c.kind == "project"]
    talents = [c for c in candidates if c.kind == "talent"]

    if projects:
        html = PROJECTS_HTML.read_text()
        match = re.search(r"const PROJECTS = (\[.*?\]);", html)
        if not match:
            sys.exit(f"PROJECTS-Array in {PROJECTS_HTML} nicht gefunden -- Format geaendert?")
        current = json.loads(match.group(1))
        current.extend(c.entry for c in projects)
        new_array = json.dumps(current, ensure_ascii=False)
        html = html[: match.start(1)] + new_array + html[match.end(1) :]
        PROJECTS_HTML.write_text(html)

    if talents:
        html = EXPERTS_HTML.read_text()
        match = re.search(
            r'(<script id="peopleData" type="application/json">)(\[.*?\])(</script>)', html
        )
        if not match:
            sys.exit(f"peopleData-Array in {EXPERTS_HTML} nicht gefunden -- Format geaendert?")
        current = json.loads(match.group(2))
        current.extend(c.entry for c in talents)
        new_array = json.dumps(current, ensure_ascii=False)
        html = html[: match.start(2)] + new_array + html[match.end(2) :]
        EXPERTS_HTML.write_text(html)


def mark_synced(token: str, page_id: str, gate_property: str) -> None:
    url = f"{NOTION_API}/pages/{page_id}"
    payload = {"properties": {gate_property: {"checkbox": True}}}
    resp = requests.patch(url, headers=notion_headers(token), json=payload, timeout=15)
    resp.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-out", type=Path, default=REPO_ROOT / "scripts" / "sync_report.json",
        help="Where to write the candidate report (fetch mode).",
    )
    parser.add_argument(
        "--apply", type=Path, default=None,
        help="Path to a (possibly Claude-filtered) report JSON to actually apply -- "
        "rewrites the HTML arrays, downloads/processes any missing posters, and marks the "
        "corresponding Notion pages as synced. Skips the fetch step entirely.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fetch mode only: print the report, do not write --report-out.",
    )
    args = parser.parse_args()

    token = load_token()

    if args.apply:
        report = json.loads(args.apply.read_text())
        candidates = [
            SyncCandidate(kind=c["kind"], notion_page_id=c["notion_page_id"], entry=c["entry"])
            for c in report["candidates"]
        ]
        apply_entries(candidates)
        for c in candidates:
            gate = PROJECTS_GATE_PROPERTY if c.kind == "project" else TALENT_GATE_PROPERTY
            mark_synced(token, c.notion_page_id, gate)
        print(f"Applied {len(candidates)} entries and marked them synced in Notion.")
        return

    project_pages = query_database(token, PROJECTS_DB_ID, PROJECTS_GATE_PROPERTY)
    talent_pages = query_database(token, TALENT_DB_ID, TALENT_GATE_PROPERTY)

    candidates = [map_project(p) for p in project_pages] + [map_talent(p) for p in talent_pages]
    report = build_report(candidates)

    if args.dry_run:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        args.report_out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(f"{report['candidate_count']} Kandidaten ({report['flagged_count']} mit Flags) -> {args.report_out}")


if __name__ == "__main__":
    main()
