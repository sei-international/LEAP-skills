#!/usr/bin/env python3
"""Check the LEAP skills repository.

Run from anywhere: python scripts/validate_skills.py [repo-root]

Checks every SKILL.md under plugins/*/skills:
  - front matter is present and has exactly the allowed keys (name, description, metadata)
  - name matches the folder name and follows the Agent Skills naming rules
  - description is 1 to 1024 characters
  - the file is under 500 lines
  - no tab characters
And the JSON files:
  - .claude-plugin/marketplace.json and each plugins/*/.claude-plugin/plugin.json parse
  - every marketplace entry points at a plugin folder that exists, and the entry name
    equals the plugin.json name

No dependencies beyond the Python standard library. Exit code 0 when everything passes.
"""

import json
import re
import sys
from pathlib import Path

ALLOWED_KEYS = {"name", "description", "metadata"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_LINES = 500
MAX_DESCRIPTION = 1024

errors = []


def fail(path, message):
    errors.append(f"{path}: {message}")


def parse_front_matter(text, path):
    """Return the front matter as a dict of top-level key -> value (string or dict).

    This is a small purpose-built reader, not a YAML parser. It handles what the
    skills use: scalar values, quoted scalars, and one level of indented mapping
    under `metadata`.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        fail(path, "front matter must start with --- on line 1")
        return None
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        fail(path, "front matter has no closing ---")
        return None

    data = {}
    current_map = None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        if raw.startswith(" ") or raw.startswith("\t"):
            if current_map is None:
                fail(path, f"indented line outside a mapping: {raw.strip()!r}")
                continue
            key, sep, value = raw.strip().partition(":")
            if not sep:
                fail(path, f"bad metadata line: {raw.strip()!r}")
                continue
            current_map[key.strip()] = value.strip()
            continue
        key, sep, value = raw.partition(":")
        if not sep:
            fail(path, f"bad front matter line: {raw.strip()!r}")
            continue
        key = key.strip()
        value = value.strip()
        if key in data:
            fail(path, f"duplicate front matter key {key!r}")
        if value == "":
            data[key] = {}
            current_map = data[key]
        else:
            data[key] = value
            current_map = None
    return data


def check_skill(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    rel = skill_md.as_posix()
    if not skill_md.is_file():
        fail(skill_dir.as_posix(), "no SKILL.md")
        return
    text = skill_md.read_text(encoding="utf-8")

    if "\t" in text:
        fail(rel, "contains tab characters")
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    if line_count >= MAX_LINES:
        fail(rel, f"{line_count} lines; must be under {MAX_LINES}")

    fm = parse_front_matter(text, rel)
    if fm is None:
        return
    keys = set(fm)
    extra = keys - ALLOWED_KEYS
    if extra:
        fail(rel, f"front matter keys not allowed: {sorted(extra)} (allowed: name, description, metadata)")
    for required in ("name", "description"):
        if required not in fm:
            fail(rel, f"front matter is missing {required!r}")

    name = fm.get("name")
    if isinstance(name, str):
        if name != skill_dir.name:
            fail(rel, f"name {name!r} does not match folder name {skill_dir.name!r}")
        if not NAME_RE.match(name) or len(name) > 64:
            fail(rel, f"name {name!r} must be 1-64 lowercase letters, digits and single hyphens")
    elif name is not None:
        fail(rel, "name must be a plain string")

    description = fm.get("description")
    if isinstance(description, str):
        d = description.strip().strip('"').strip("'")
        if not d:
            fail(rel, "description is empty")
        elif len(d) > MAX_DESCRIPTION:
            fail(rel, f"description is {len(d)} characters; limit is {MAX_DESCRIPTION}")
    elif description is not None:
        fail(rel, "description must be a plain string")

    metadata = fm.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        fail(rel, "metadata must be a mapping of key: value lines")


def load_json(path):
    rel = path.as_posix()
    if not path.is_file():
        fail(rel, "file is missing")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(rel, f"invalid JSON: {e}")
        return None


def check_json(root):
    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_path)
    plugin_names = {}

    for plugin_json in sorted(root.glob("plugins/*/.claude-plugin/plugin.json")):
        plugin_dir = plugin_json.parent.parent
        data = load_json(plugin_json)
        if data is None:
            continue
        name = data.get("name")
        if not isinstance(name, str) or not name:
            fail(plugin_json.as_posix(), "plugin.json needs a non-empty name")
            continue
        if name != plugin_dir.name:
            fail(plugin_json.as_posix(), f"name {name!r} does not match folder {plugin_dir.name!r}")
        plugin_names[plugin_dir.name] = name

    if marketplace is None:
        return
    rel = marketplace_path.as_posix()
    for key in ("name", "owner", "plugins"):
        if key not in marketplace:
            fail(rel, f"missing required field {key!r}")
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        fail(rel, "plugins must be a list")
        return
    for entry in entries:
        ename = entry.get("name")
        source = entry.get("source")
        if not isinstance(ename, str) or not isinstance(source, str):
            fail(rel, f"entry {entry!r} needs a string name and a relative-path source")
            continue
        if ".." in source:
            fail(rel, f"entry {ename!r}: source must not contain '..'")
        folder = root / source
        if not folder.is_dir():
            fail(rel, f"entry {ename!r}: source folder {source!r} does not exist")
            continue
        manifest_name = plugin_names.get(folder.name)
        if manifest_name is None:
            fail(rel, f"entry {ename!r}: {source}/.claude-plugin/plugin.json is missing or invalid")
        elif manifest_name != ename:
            fail(rel, f"entry {ename!r} differs from plugin.json name {manifest_name!r}")


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    skill_dirs = sorted(p for p in root.glob("plugins/*/skills/*") if p.is_dir())
    for d in skill_dirs:
        check_skill(d)
    check_json(root)

    if errors:
        print("Validation failed:")
        for e in errors:
            print("  " + e)
        return 1
    print(f"Validation passed: {len(skill_dirs)} skills checked under {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
