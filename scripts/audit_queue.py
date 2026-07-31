#!/usr/bin/env python3
"""Read-only cursor and deduplication audit for backlink workspaces."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


SHARED_HOSTS = {
    "airtable.com",
    "docs.google.com",
    "forms.gle",
    "forms.office.com",
    "notion.site",
    "tally.so",
    "typeform.com",
}
PROCESSED_STATES = {"deferred", "terminal"}


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def parse_url(value: str) -> tuple[str, str]:
    raw = value.strip()
    if not raw:
        return "", ""
    candidate = raw if "://" in raw else f"https://{raw}"
    parsed = urlsplit(candidate)
    host = (parsed.hostname or "").casefold()
    if host.startswith("www."):
        host = host[4:]
    path = re.sub(r"/+", "/", unquote(parsed.path or "/"))
    if path != "/":
        path = path.rstrip("/")
    return host, path


def is_shared_host(host: str) -> bool:
    return any(host == item or host.endswith(f".{item}") for item in SHARED_HOSTS)


def dedupe_key(platform: str, url: str) -> str:
    host, path = parse_url(url)
    if host:
        return f"{host}{path}" if is_shared_host(host) else host
    return normalize_text(platform)


def source_key(csv_name: str, platform: str, url: str) -> str:
    host, path = parse_url(url)
    endpoint = f"{host}{path}" if host else normalize_text(url)
    return f"{csv_name}::{normalize_text(platform)}::{endpoint}"


def load_queue(workspace: Path) -> list[dict[str, object]]:
    platforms_dir = workspace / "platforms"
    declaration = platforms_dir / "queue.txt"
    if not declaration.is_file():
        raise ValueError(f"missing queue declaration: {declaration}")

    queue: list[dict[str, object]] = []
    filenames = [
        line.strip()
        for line in declaration.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not filenames:
        raise ValueError(f"queue declaration is empty: {declaration}")

    for filename in filenames:
        csv_path = platforms_dir / filename
        if not csv_path.is_file():
            raise ValueError(f"queue CSV does not exist: {csv_path}")
        with csv_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            required = {"platform", "platform_url"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError(
                    f"{csv_path} must contain columns: platform,platform_url"
                )
            for row_number, row in enumerate(reader, start=2):
                platform = (row.get("platform") or "").strip()
                platform_url = (row.get("platform_url") or "").strip()
                if not platform or not platform_url:
                    continue
                queue.append(
                    {
                        "index": len(queue),
                        "csv": filename,
                        "row_number": row_number,
                        "platform": platform,
                        "platform_url": platform_url,
                        "source_key": source_key(filename, platform, platform_url),
                        "dedupe_key": dedupe_key(platform, platform_url),
                    }
                )
    return queue


def load_progress(workspace: Path, website: str) -> list[dict[str, str]]:
    path = workspace / "records" / "platform-progress.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {
            "website",
            "csv",
            "source_key",
            "dedupe_key",
            "platform",
            "platform_url",
            "state",
            "last_status",
            "last_attempted",
            "evidence_url",
            "notes",
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"{path} does not match the required progress schema"
            )
        wanted = website.casefold().strip()
        return [
            {key: value or "" for key, value in row.items()}
            for row in reader
            if (row.get("website") or "").casefold().strip() == wanted
        ]


def latest_daily_summary(workspace: Path) -> dict[str, str]:
    daily_dir = workspace / "records" / "daily"
    files = sorted(daily_dir.glob("????-??-??.md")) if daily_dir.exists() else []
    if not files:
        return {"file": "", "active_csv": "", "next_cursor": ""}
    latest = files[-1]
    text = latest.read_text(encoding="utf-8")

    def extract(label: str) -> str:
        match = re.search(
            rf"(?im)^[ \t>*-]*{re.escape(label)}\s*:\s*`?([^`\n]+?)`?\s*$",
            text,
        )
        return match.group(1).strip() if match else ""

    return {
        "file": str(latest),
        "active_csv": extract("Active CSV"),
        "next_cursor": extract("Next cursor"),
    }


def audit(workspace: Path, website: str) -> dict[str, object]:
    queue = load_queue(workspace)
    progress = load_progress(workspace, website)
    summary = latest_daily_summary(workspace)

    persisted = [
        row for row in progress if row.get("state", "").casefold() in PROCESSED_STATES
    ]
    exact_keys = {row["source_key"] for row in persisted if row.get("source_key")}
    seen_dedupe: dict[str, dict[str, str]] = {}
    for row in persisted:
        key = row.get("dedupe_key") or dedupe_key(
            row.get("platform", ""), row.get("platform_url", "")
        )
        if key and key not in seen_dedupe:
            seen_dedupe[key] = row

    positions = {
        str(item["source_key"]): int(item["index"])
        for item in queue
    }
    persisted_positions = [
        positions[key] for key in exact_keys if key in positions
    ]
    furthest_index = max(persisted_positions, default=-1)

    next_item = next(
        (
            item
            for item in queue
            if int(item["index"]) > furthest_index
            and str(item["source_key"]) not in exact_keys
        ),
        None,
    )

    duplicate_match = None
    if next_item:
        earlier = seen_dedupe.get(str(next_item["dedupe_key"]))
        if earlier:
            duplicate_match = {
                "platform": earlier.get("platform", ""),
                "source_key": earlier.get("source_key", ""),
                "status": earlier.get("last_status", ""),
                "evidence_url": earlier.get("evidence_url", ""),
            }

    saved_cursor = summary["next_cursor"]
    reconciled_cursor = str(next_item["source_key"]) if next_item else "QUEUE_EXHAUSTED"
    return {
        "website": website,
        "workspace": str(workspace),
        "previous_daily_log": summary["file"],
        "saved_active_csv": summary["active_csv"],
        "saved_next_cursor": saved_cursor,
        "saved_cursor_matches": bool(saved_cursor)
        and saved_cursor == reconciled_cursor,
        "progress_rows": len(progress),
        "furthest_persisted_queue_index": furthest_index,
        "queue_rows": len(queue),
        "reconciled_active_csv": next_item["csv"] if next_item else "",
        "next_cursor": reconciled_cursor,
        "next_candidate": next_item,
        "duplicate_match": duplicate_match,
    }


def render_text(result: dict[str, object]) -> str:
    candidate = result["next_candidate"]
    duplicate = result["duplicate_match"]
    lines = [
        f"Website: {result['website']}",
        f"Previous daily log: {result['previous_daily_log'] or '(none)'}",
        f"Saved active CSV: {result['saved_active_csv'] or '(none)'}",
        f"Saved next cursor: {result['saved_next_cursor'] or '(none)'}",
        f"Saved cursor matches: {result['saved_cursor_matches']}",
        f"Progress rows: {result['progress_rows']}",
        f"Queue rows: {result['queue_rows']}",
        f"Reconciled active CSV: {result['reconciled_active_csv'] or '(exhausted)'}",
        f"Next cursor: {result['next_cursor']}",
    ]
    if candidate:
        lines.extend(
            [
                f"Next platform: {candidate['platform']}",
                f"Next URL: {candidate['platform_url']}",
                f"CSV row: {candidate['row_number']}",
            ]
        )
    if duplicate:
        lines.extend(
            [
                "Duplicate gate: duplicate-existing",
                f"Earlier platform: {duplicate['platform']}",
                f"Earlier source key: {duplicate['source_key']}",
                f"Earlier evidence: {duplicate['evidence_url'] or '(none)'}",
            ]
        )
    else:
        lines.append("Duplicate gate: clear")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit a backlink queue without modifying workspace files."
    )
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--website", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        result = audit(args.workspace.expanduser().resolve(), args.website)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
