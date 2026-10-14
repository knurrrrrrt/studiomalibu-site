#!/usr/bin/env python3
"""Gate for app help docs (Studio Malibu). Exit 0 = publishable, 1 = problems found.

Usage:  check_help_docs.py <app_repo_root> <docs_dir> [--show-lines] [--app-version X.Y.Z]
        --show-lines prints the cited source line for every evidence item (speeds up the review)

Rules (see SKILL.md):
  - every <name>.en.md has a <name>.de.md and vice versa
  - frontmatter keys: title, app, slug, lang, version; lang matches the file name
  - frontmatter also needs `reviewed:` (date + who/what did the read-only claim review)
  - every "## " section carries an evidence comment: <!-- evidence: path:123, path#symbol, ... -->
    paths must exist (prefix `external:` resolves next to the app repo, for sibling packages); at least one item per section must be specific (line number that
    exists in the file, or #symbol that occurs in the file); file-only items are warnings
  - **Bold** is reserved for UI labels. A label must occur in the app sources (error if not);
    a label that matches no complete string literal (or catalog key) exactly, but occurs as a
    substring somewhere, is a warning with file:line so it can be checked by hand
  - no TODO-verify markers, relative links and images must exist
  - EN and DE have the same number of sections and the same evidence paths per section
"""
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "build", ".build", "DerivedData", "worktrees", "node_modules", "Pods", "docs", ".claude"}
SRC_SUFFIXES = {".swift", ".xcstrings", ".strings", ".stringsdict", ".plist", ".json", ".js", ".ts", ".py", ".m", ".h"}
MAX_FILE = 2_000_000


LITERAL = re.compile(r'"((?:[^"\\\n]|\\.){1,120})"')


def load_sources(root: Path):
    """Return (files, ui_strings): files = {relpath: text}; ui_strings = {complete string literal: 'file:line'}."""
    files, ui, ax_only = {}, {}, {}
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in SRC_SUFFIXES:
            continue
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts) or "Tests" in rel.parts:
            continue
        try:
            if p.stat().st_size > MAX_FILE:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        files[str(rel)] = text
        if p.suffix == ".swift":
            for ln, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith("//"):
                    continue
                hidden_ui = ".accessibilityLabel(" in line or ".accessibilityHint(" in line
                for m in LITERAL.finditer(line):
                    if hidden_ui:
                        ax_only.setdefault(m.group(1), f"{rel}:{ln}")
                    else:
                        ui.setdefault(m.group(1), f"{rel}:{ln}")
        elif p.suffix in (".xcstrings", ".strings", ".stringsdict"):
            for ln, line in enumerate(text.splitlines(), 1):
                for m in re.finditer(r'"([^"\\]{1,120})"\s*(?:=|:)', line):
                    ui.setdefault(m.group(1), f"{rel}:{ln}")
    return files, ui, ax_only


def locate(files, needle):
    for rel, text in files.items():
        i = text.find(needle)
        if i >= 0:
            return f"{rel}:{text.count(chr(10), 0, i) + 1}"
    return None


VENDORED = ("patcher", "vendor", "thirdparty", "third_party", "external", "fcpbridge", "pods", "carthage", "checkouts")


def app_version(root: Path):
    for name in ("project.yml",):
        f = root / name
        if f.exists():
            m = re.search(r"MARKETING_VERSION:\s*\"?([0-9][^\s\"]*)", f.read_text(errors="ignore"))
            if m:
                return m.group(1), name
    for f in root.rglob("Info.plist"):
        parts = [p.lower() for p in f.relative_to(root).parts]
        if any(part in SKIP_DIRS for part in f.relative_to(root).parts) or any(v in part for part in parts for v in VENDORED):
            continue
        m = re.search(r"<key>CFBundleShortVersionString</key>\s*<string>([0-9][^<]*)</string>", f.read_text(errors="ignore"))
        if m:
            return m.group(1), str(f.relative_to(root))
    return None, None


def frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text[m.end():]


def sections(body: str):
    """Split on '## ' headings; returns list of (heading, text)."""
    out, cur_h, cur = [], None, []
    for line in body.splitlines():
        if line.startswith("## "):
            if cur_h is not None:
                out.append((cur_h, "\n".join(cur)))
            cur_h, cur = line[3:].strip(), []
        elif cur_h is not None:
            cur.append(line)
    if cur_h is not None:
        out.append((cur_h, "\n".join(cur)))
    return out


def evidence_of(text: str):
    items = []
    for m in re.finditer(r"<!--\s*evidence:\s*(.*?)-->", text, re.S):
        # a comma starts a new item only when a file path (with extension) or external: follows,
        # so symbols and quoted UI text may contain commas
        for it in re.split(r",\s*(?=external:|[\w+.\-]+(?:/[\w+.\- ]+)*\.[A-Za-z0-9]+(?:[:#]|\s*,|\s*$))", m.group(1)):
            it = it.strip()
            if it:
                items.append(it)
    return items


def main():
    argv = sys.argv[1:]
    forced_ver = None
    if "--app-version" in argv:
        i = argv.index("--app-version")
        forced_ver = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    args = [a for a in argv if a != "--show-lines"]
    show_lines = "--show-lines" in sys.argv[1:]
    if len(args) != 2:
        print(__doc__)
        return 2
    root, docs = Path(args[0]), Path(args[1])
    shown = []
    problems = []
    files = sorted(docs.glob("*.md"))
    if not files:
        print(f"no markdown files in {docs}")
        return 1

    names = {}
    for f in files:
        m = re.match(r"^(.*)\.(en|de)\.md$", f.name)
        if not m:
            problems.append(f"{f.name}: file name must be <name>.en.md or <name>.de.md")
            continue
        names.setdefault(m.group(1), {})[m.group(2)] = f
    for n, langs in names.items():
        for l in ("en", "de"):
            if l not in langs:
                problems.append(f"{n}: missing .{l}.md counterpart")

    src_files, ui, ax_only = load_sources(root)
    src = "\n".join(src_files.values())
    cur_ver, ver_src = (forced_ver, "--app-version") if forced_ver else app_version(root)
    warnings = []
    parsed = {}
    for n, langs in names.items():
        for lang, f in langs.items():
            text = f.read_text(encoding="utf-8")
            fm, body = frontmatter(text)
            tag = f.name
            # Style rule (Knut, 2026-10-14): no dashes in prose. Evidence comments, code spans,
            # bold UI labels and quoted UI strings are exempt.
            prose = re.sub(r"<!--.*?-->", "", body, flags=re.S)
            prose = re.sub(r"`[^`]*`", "", prose)
            prose = re.sub(r"\*\*[^*]+\*\*", "", prose)
            prose = re.sub(r"\"[^\"]*\"", "", prose)
            for ln_no, ln in enumerate(prose.splitlines(), 1):
                if re.search(r"[\u2014\u2013]| - ", ln):
                    problems.append(f"{tag}: style: dash in prose, rephrase (line text: {ln.strip()[:70]!r})")
                    break
            if fm is None:
                problems.append(f"{tag}: frontmatter missing")
                continue
            for k in ("title", "app", "slug", "lang", "version", "reviewed"):
                if not fm.get(k):
                    problems.append(f"{tag}: frontmatter key '{k}' missing")
            if fm.get("lang") and fm["lang"] != lang:
                problems.append(f"{tag}: frontmatter lang '{fm['lang']}' != file name '{lang}'")
            if cur_ver and fm.get("version") and fm["version"] != cur_ver:
                warnings.append(f"{tag}: frontmatter version {fm['version']} != app version {cur_ver} ({ver_src}); re-verify before release")
            if re.search(r"TODO[ _-]?verify|\bTBD\b|\bXXX\b", body, re.I):
                problems.append(f"{tag}: contains a TODO-verify / TBD marker; not publishable")

            secs = sections(body)
            if not secs:
                problems.append(f"{tag}: no '## ' sections")
            ev_per_section = []
            for h, t in secs:
                ev = evidence_of(t)
                ev_per_section.append(sorted(e.split(":")[0] for e in ev))
                if not ev:
                    problems.append(f"{tag}: section '{h}' has no <!-- evidence: ... --> comment")
                specific = False
                for e in ev:
                    base = root
                    if e.startswith("external:"):
                        # sibling package next to the app repo, e.g. external:MalibuDesignKit/Sources/X.swift#Symbol
                        e, base = e[len("external:"):].strip(), root.parent
                    m2 = re.match(r"^([^:#]+?)(?::(\d+)|#(.+))?$", e)
                    path = (m2.group(1) if m2 else e).strip()
                    fpath = base / path
                    if not fpath.exists():
                        problems.append(f"{tag}: section '{h}': evidence path not found: {path}")
                        continue
                    if m2 and m2.group(2):
                        try:
                            n_lines = len(fpath.read_text(errors="ignore").splitlines())
                        except OSError:
                            n_lines = 0
                        if int(m2.group(2)) <= n_lines:
                            specific = True
                            ln_no = int(m2.group(2))
                            src_line = fpath.read_text(errors="ignore").splitlines()[ln_no - 1]
                            st = src_line.strip()
                            if show_lines:
                                shown.append(f"{tag} § {h}: {path}:{ln_no}: {st[:140]}")
                            if st == "" or st in ("}", "})", "]", ")", "{", "},", ")}"):
                                problems.append(f"{tag}: section '{h}': {path}:{ln_no} is blank or a lone bracket; cite the line that makes the claim true (or use path#symbol)")
                            elif st.startswith("//") or st.startswith("///") or st.startswith("#") or st.startswith("*") or st.startswith("/*"):
                                warnings.append(f"{tag}: section '{h}': {path}:{ln_no} is a comment, not code; prefer path#symbol")
                        else:
                            problems.append(f"{tag}: section '{h}': {path} has only {n_lines} lines, evidence says :{m2.group(2)}")
                    elif m2 and m2.group(3):
                        try:
                            has = m2.group(3).strip() in fpath.read_text(errors="ignore")
                        except OSError:
                            has = False
                        if has:
                            specific = True
                        else:
                            problems.append(f"{tag}: section '{h}': symbol '{m2.group(3).strip()}' not found in {path}")
                if ev and not specific:
                    problems.append(f"{tag}: section '{h}': evidence is file-level only; add path:LINE or path#symbol")

            # bold = UI label, must exist verbatim in app sources
            plain = re.sub(r"<!--.*?-->", "", body, flags=re.S)
            plain = re.sub(r"```.*?```", "", plain, flags=re.S)
            for lab in sorted(set(re.findall(r"\*\*([^*\n]+)\*\*", plain))):
                label = lab.strip().rstrip(".:")
                if not label:
                    continue
                base = label.rstrip("\u2026").rstrip(".").strip()
                if any(c in ui for c in (label, base, base + "\u2026", base + "...")):
                    continue
                if label in ax_only and label not in ui:
                    warnings.append(f"{tag}: **{label}** is only an accessibility label ({ax_only[label]}), not visible text; check what the user actually sees")
                    continue
                if label not in src:
                    problems.append(f"{tag}: UI label not found in app sources: **{label}**")
                else:
                    warnings.append(f"{tag}: **{label}** found only outside UI contexts at {locate(src_files, label)}; check by hand")

            # links and images
            for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", plain):
                target = m.group(1)
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                if not (f.parent / target.split("#")[0]).exists():
                    problems.append(f"{tag}: broken relative link: {target}")
            parsed[(n, lang)] = (len(secs), ev_per_section)

    for n, langs in names.items():
        if (n, "en") in parsed and (n, "de") in parsed:
            en, de = parsed[(n, "en")], parsed[(n, "de")]
            if en[0] != de[0]:
                problems.append(f"{n}: EN has {en[0]} sections, DE has {de[0]}")
            else:
                for i, (a, b) in enumerate(zip(en[1], de[1]), 1):
                    if a != b:
                        problems.append(f"{n}: section {i} evidence differs between EN and DE")

    for line in shown:
        print(" > ", line)
    seen = set()
    for w in warnings:
        key = re.sub(r"^[^:]+: ", "", w)
        if key in seen:
            continue
        seen.add(key)
        print(" ~ WARN", w)
    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for p in problems:
            print(" -", p)
        return 1
    print(f"OK: {len(files)} file(s) pass the gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
