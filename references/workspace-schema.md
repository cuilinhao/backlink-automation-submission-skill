# Workspace schema

Use this layout:

```text
backlink-workspace/
├── sites/
│   └── ExampleSite.md
├── assets/
│   └── example-site/
├── platforms/
│   ├── queue.txt
│   ├── public-platforms.csv
│   └── blacklist.csv
└── records/
    ├── platform-progress.csv
    └── daily/
```

Copy starter files from `assets/templates/` and replace the sample values.

## Site profile

Store one Markdown file per real target website. Include:

- Website Name
- Website URL
- One-liner
- Long Description
- Target Users
- Categories
- Tags
- Contact Email
- Logo Path
- Screenshot Paths
- Authorized Browser Profile
- Available Accounts
- Constraints

Exclude demo or test profiles unless the user explicitly requests them.

## Queue declaration

List one executable CSV filename per line in `platforms/queue.txt`. Resolve paths relative to `platforms/`.

Ignore blank lines and lines beginning with `#`.

Example:

```text
public-platforms.csv
high-authority-platforms.csv
```

Never put a blacklist or failure archive in this file.

## Platform CSV

Use UTF-8 CSV with these columns:

```text
platform,platform_url,category,notes
```

Preserve file and row order. Keep platform URLs canonical and include the submission path when known.

## Blacklist CSV

Use:

```text
platform,platform_url,reason
```

Match normalized URL and path first. Avoid domain-only exclusion for shared form hosts.

## Progress CSV

Use:

```text
website,csv,source_key,dedupe_key,platform,platform_url,state,last_status,last_attempted,evidence_url,notes
```

Create one row per target website and source key. Upsert immediately after every candidate.

Build:

- `source_key`: `<csv filename>::<normalized platform>::<normalized host/path>`
- `dedupe_key`: normalized platform hostname, or host/path for a shared form host

CSV-level status is never proof that a specific target website was submitted.

## Daily log

Create `records/daily/YYYY-MM-DD.md`.

Include:

- target count and current count
- run-start resume audit
- active CSV and next cursor
- processed, deferred, and remaining totals
- counted evidence table
- duplicate, paid, terminal, and deferred table
- exact blockers

The daily log is a readable audit trail. `platform-progress.csv` remains the row-level source of truth.
