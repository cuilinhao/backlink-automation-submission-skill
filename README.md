# Backlink Automation Submission Skill

[English](README.md) · [简体中文](README.zh-CN.md)

A reusable Codex skill for running low-volume, resumable, evidence-based, white-hat backlink and product-listing workflows.

This project treats backlink submission as a persistent queue instead of a one-off browser session. Every run resumes from the last saved cursor, checks the complete history for duplicates, submits only to relevant platforms, verifies platform-owned evidence, and saves the next cursor immediately.

## Why this skill exists

Backlink automation often fails in predictable ways:

- a new run starts again from the beginning;
- the same directory is submitted more than once;
- a refreshed technical report is incorrectly counted as a new backlink;
- a form is filled but counted before it is submitted;
- progress is kept only in browser tabs or memory;
- CAPTCHA, login, payment, or badge requirements are recorded inaccurately;
- a tool claims SEO value that was never verified.

This skill adds strict operational gates for cursor recovery, lifetime deduplication, evidence-based counting, immediate persistence, and safe browser operation.

## Key features

- Ordered CSV queue with automatic rollover
- Mandatory resume audit before any platform is opened
- Per-website, cross-run cursor
- Lifetime deduplication by platform, domain, path, source key, and evidence
- Shared-form-host handling for Typeform, Tally, Google Forms, and Airtable
- Clear `unprocessed`, `deferred`, and `terminal` states
- Counted versus not-counted status taxonomy
- Visible, authorized browser-session workflow
- Login, OAuth, email verification, magic-link, and one-time-code continuation
- Approved logo and screenshot uploads
- CAPTCHA and anti-abuse safeguards
- Immediate progress persistence after every candidate
- Read-only queue audit script with no external Python dependencies
- Reusable workspace templates
- Auditable daily Markdown reports

## What this skill will not do

It will not:

- create fake identities, reviews, votes, followers, or comments;
- publish thin pages solely to manufacture backlinks;
- use link farms, PBN marketplaces, or black-hat services;
- bypass CAPTCHA, Cloudflare, security warnings, or anti-bot controls;
- inspect or export cookies, passwords, tokens, or browser databases;
- make unapproved payments;
- invent company, customer, traffic, funding, hiring, or performance claims;
- guarantee ranking improvements or misrepresent a technical report as an endorsement.

## Repository contents

```text
backlink-automation-submission/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── scripts/
│   └── audit_queue.py
├── references/
│   └── workspace-schema.md
└── assets/
    └── templates/
        ├── site-profile.md
        ├── queue.txt
        ├── public-platforms.csv
        ├── blacklist.csv
        ├── platform-progress.csv
        └── daily-log.md
```

## Requirements

- Codex or another agent runtime that supports `SKILL.md`
- Python 3.9 or later
- A visible browser/computer-control capability for live submissions
- An authorized browser profile and accounts owned or approved by the user
- A backlink workspace created from the bundled templates

`scripts/audit_queue.py` uses only the Python standard library.

## Installation

### Install for Codex

Clone the repository into your Codex skills directory:

```bash
git clone https://github.com/cuilinhao/backlink-automation-submission-skill.git \
  ~/.codex/skills/backlink-automation-submission
```

Restart or refresh Codex so the skill can be discovered.

Invoke it explicitly with:

```text
$backlink-automation-submission
```

### Install in another agent runtime

Clone the repository and register its root `SKILL.md` using that runtime's skill-loading mechanism. Keep the relative `scripts/`, `references/`, and `assets/` directories intact.

### Update

```bash
git -C ~/.codex/skills/backlink-automation-submission pull --ff-only
```

## Quick start

### 1. Create a workspace

Example:

```bash
mkdir -p ~/backlink-workspace/{sites,assets,platforms,records/daily}

cp ~/.codex/skills/backlink-automation-submission/assets/templates/site-profile.md \
  ~/backlink-workspace/sites/ExampleSite.md

cp ~/.codex/skills/backlink-automation-submission/assets/templates/queue.txt \
  ~/backlink-workspace/platforms/queue.txt

cp ~/.codex/skills/backlink-automation-submission/assets/templates/public-platforms.csv \
  ~/backlink-workspace/platforms/public-platforms.csv

cp ~/.codex/skills/backlink-automation-submission/assets/templates/blacklist.csv \
  ~/backlink-workspace/platforms/blacklist.csv

cp ~/.codex/skills/backlink-automation-submission/assets/templates/platform-progress.csv \
  ~/backlink-workspace/records/platform-progress.csv
```

### 2. Complete the site profile

Edit `sites/ExampleSite.md`:

```markdown
# Website profile

- Website Name: ExampleSite
- Website URL: https://example.com
- One-liner: A concise, truthful product summary.
- Long Description: A complete description using only verified claims.
- Target Users: Creators, agencies, and marketing teams
- Categories: Creator Tools, Analytics
- Tags: research, analytics, video
- Contact Email: support@example.com
- Logo Path: assets/example-site/logo.png
- Screenshot Paths: assets/example-site/dashboard.png
- Authorized Browser Profile: Work
- Available Accounts: Existing Google and GitHub accounts in the Work profile
- Constraints: Do not pay for listings; do not publish guest posts
```

Do not leave fields ambiguous when a platform needs them. Do not add personal identity or business claims that the user has not approved.

### 3. Build the platform queue

List executable CSV files in `platforms/queue.txt`, one per line:

```text
public-platforms.csv
high-authority-platforms.csv
```

Each queue CSV uses:

```csv
platform,platform_url,category,notes
Example Directory,https://directory.example.com/submit,product-directory,Free manual-review listing
Example Audit,https://audit.example.com,technical-report,Count at most once
```

Preserve CSV order. Never add blacklist, failure archive, or historical export files to `queue.txt`.

### 4. Maintain the blacklist

Use `platforms/blacklist.csv`:

```csv
platform,platform_url,reason
Unsafe Example,https://unsafe.example.com,Link farm
```

Match URL and path before using a domain-wide exclusion, especially for shared form hosts.

### 5. Run the skill

Example prompt:

```text
Use $backlink-automation-submission.
Workspace: /absolute/path/to/backlink-workspace
Target website: ExampleSite
Complete 3 new, unique, countable backlinks.
Use only the Authorized Browser Profile from the site profile.
Skip only unapproved payments; defer other unavailable checkpoints precisely.
```

## Mandatory run-start audit

Every run must perform this sequence before opening a candidate platform:

1. Read the site profile.
2. Read `platforms/queue.txt` and every executable CSV.
3. Read the blacklist.
4. Read all progress rows for the target website.
5. Read the latest and relevant historical daily logs.
6. Run the queue audit script.
7. Reconcile the saved daily cursor with row-level progress.
8. Record the resolved cursor in today's daily log.

Run the audit manually with:

```bash
python3 ~/.codex/skills/backlink-automation-submission/scripts/audit_queue.py \
  --workspace /absolute/path/to/backlink-workspace \
  --website "ExampleSite"
```

JSON output:

```bash
python3 ~/.codex/skills/backlink-automation-submission/scripts/audit_queue.py \
  --workspace /absolute/path/to/backlink-workspace \
  --website "ExampleSite" \
  --json
```

The script is read-only. It does not edit CSV files or daily logs.

## How cursor recovery works

The row-level progress file is the primary persisted state. The latest daily log is the human-readable summary.

At startup, the skill:

- finds the furthest queue row with a persisted `deferred` or `terminal` state;
- compares it with the latest `Next cursor`;
- reports whether the cursor matches;
- selects the first unprocessed row after the verified position;
- flags queue exhaustion when no executable row remains.

If a daily summary is stale but later row-level records exist, row-level records win. If the records cannot be reconciled, the skill must repair them before opening any platform.

## Lifetime deduplication

Deduplication is scoped per target website and uses:

- normalized platform name;
- hostname without case or leading `www`;
- submission path;
- `source_key`;
- `dedupe_key`;
- previous evidence URLs;
- historical daily logs.

These are duplicates:

| Earlier result | New candidate | Decision |
|---|---|---|
| `example.com/submit` | `www.example.com/add-product` | Duplicate platform/domain |
| Technical report `report/123` | Technical report `report/456` | Duplicate technical platform |
| Existing listing | New update form for the same listing | Duplicate existing listing |
| Platform in CSV A | Same platform in CSV B | Duplicate cross-CSV source |
| Same domain with a new query string | Refreshed query | Duplicate |

A duplicate must be recorded as terminal `duplicate-existing`, linked to the earlier evidence, and excluded from the new-backlink count.

For shared form hosts, the path or form ID matters. Two different Typeform forms may represent two different destination platforms; the agent must verify the underlying destination before treating them as unique.

## Evidence-based counting

Count only when the platform itself shows at least one of:

- submitted;
- submission received;
- pending review;
- scheduled;
- a live/public listing;
- a dashboard record for the target website;
- a public verification page containing the target domain.

Do not count:

- a filled but unsubmitted form;
- a draft;
- an incomplete profile;
- a payment page;
- unresolved verification;
- a duplicate;
- an irrelevant platform;
- a missing badge;
- a generic result page without target-specific evidence;
- an existing listing discovered during a new-submission run.

Technical audit pages are public footprint evidence, not editorial recommendations. Each technical platform counts at most once per target website unless the user explicitly requests a historical audit.

## Browser and account safety

The site profile must name an authorized browser profile. Before any interaction, verify the visible profile.

The workflow may continue through visible, authorized controls for:

- existing login sessions;
- account creation;
- authorized OAuth;
- email verification and magic links;
- one-time codes from an already accessible mailbox;
- approved asset uploads;
- final submission buttons.

The workflow must not:

- inspect browser databases, cookies, passwords, or tokens;
- bypass CAPTCHA or anti-bot systems;
- ignore security interstitials;
- make payments without approval;
- guess which identity or account to use;
- upload unrelated or private files.

If a required permission or credential is unavailable, preserve the exact operation node and record `deferred`.

## State model

| State | Meaning |
|---|---|
| `unprocessed` | No meaningful attempt or disposition |
| `deferred` | A resumable checkpoint remains |
| `terminal` | Counted success or conclusive not-counted result |

Common counted statuses:

```text
submitted
submission-received
pending-review
scheduled
public
live
verified
```

Common not-counted statuses:

```text
duplicate-existing
paid
blacklisted
not-relevant
unavailable
login-required
email-verification
captcha
badge-required
draft
incomplete
failed
unclear
```

## Immediate persistence

After every candidate, before opening the next row:

1. Upsert the progress row.
2. Save the exact status and evidence.
3. Update today's processed/deferred/remaining totals.
4. Update `Next cursor`.
5. Verify that the cursor points to the first truly unprocessed row.

Never leave a batch of outcomes only in memory. After an interruption, run the complete startup audit again.

## Scheduled automation

Use your automation system to invoke the skill on a schedule. Keep the task prompt explicit:

```text
Every day at 07:30, use $backlink-automation-submission.
Workspace: /absolute/path/to/backlink-workspace
Target: 10 new, unique, countable results.
Resume from the persisted cursor.
Do not repeat previously counted platforms.
Skip only unapproved payments.
Persist each result immediately.
Report counted evidence, duplicates, paid items, deferred checkpoints,
the active CSV, remaining rows, and the next cursor.
```

Scheduling does not broaden permissions. The browser profile, payment policy, identity constraints, and anti-abuse rules still apply.

## Troubleshooting

### The run starts from the beginning

- Check `records/platform-progress.csv`.
- Confirm `website` exactly matches the site-profile name.
- Confirm `source_key` values match the current CSV filenames and URLs.
- Run `audit_queue.py`.
- Repair the daily `Next cursor` only after checking row-level progress.

### The same platform appears again

- Compare normalized hostnames and `dedupe_key`.
- Search historical daily logs.
- Check whether the platform appears in another CSV.
- Record it as `duplicate-existing`; do not resubmit it.

### The script reports a stale cursor

Use the reconciled cursor based on persisted row-level progress. Update today's run-start audit before browsing.

### A platform requires payment

Without explicit approval, record terminal `paid` and move to the next candidate.

### Login, OAuth, email, or OTP is required

Use only the authorized visible browser profile and available accounts. If the correct account or mailbox cannot be determined without guessing, defer at the exact checkpoint.

### CAPTCHA or anti-bot verification appears

Do not bypass it. Use the action-time confirmation or narrow user handoff required by the active control tool.

### A badge is required

Install it only through an authorized site-admin or code path. If no authorized backend is available, record `deferred` at the badge checkpoint.

### The queue is exhausted

Report exhaustion. Do not wrap to the first CSV unless the user explicitly requests a re-audit.

## Validation

Validate the skill structure:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py \
  /path/to/backlink-automation-submission
```

Validate the queue script:

```bash
python3 -m py_compile scripts/audit_queue.py
python3 scripts/audit_queue.py --help
```

## Contributing

Contributions are welcome when they preserve:

- truthful, white-hat submissions;
- strict lifetime deduplication;
- resume-before-browse behavior;
- immediate persistence;
- evidence-based counting;
- visible, authorized account operation;
- anti-abuse and payment safeguards.

Do not submit secrets, private site profiles, browser state, personal records, or real production credentials in issues or pull requests.

## License

MIT. See [LICENSE](LICENSE).
