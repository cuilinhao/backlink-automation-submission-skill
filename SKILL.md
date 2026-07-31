---
name: backlink-automation-submission
description: Run resumable, evidence-based, white-hat backlink, product-listing, directory-submission, and public technical-report workflows. Use when Codex must submit or continue submitting a website across an ordered platform queue, avoid historical duplicates, operate an authorized visible browser session through login or verification checkpoints, verify countable evidence, persist a cross-run cursor, and produce an auditable daily report.
---

# Backlink Automation Submission

Run low-volume, truthful backlink outreach as a persistent queue. Optimize for relevant, verifiable placements rather than raw submission volume.

Do not use this skill for link farms, fake accounts, fabricated reviews or votes, comment spam, cloaking, purchased links without approval, anti-abuse bypasses, or thin microsites created only to manufacture backlinks.

## Required workspace

Expect a workspace containing:

- `sites/`: one Markdown profile per target website
- `platforms/queue.txt`: executable CSV files in order
- `platforms/blacklist.csv`: exclusion and risk reference
- `records/platform-progress.csv`: cross-run state and cursor
- `records/daily/`: dated run logs
- `assets/`: approved site-specific submission assets

Read [references/workspace-schema.md](references/workspace-schema.md) when creating, validating, or repairing this structure. Copy starter files from `assets/templates/` when the workspace is missing.

Require these site-profile facts before submission:

- website name and canonical URL
- truthful one-liner and description
- target users, categories, and tags
- contact email
- logo or screenshots when available
- authorized browser profile label
- explicit constraints and available accounts

Never invent missing identity, company, customer, traffic, funding, hiring, integration, or performance claims.

## Mandatory run-start resume gate

Complete this gate before opening or navigating to any candidate platform.

1. Read the target site profile.
2. Read `platforms/queue.txt`, every listed executable CSV, and `platforms/blacklist.csv`.
3. Read every progress row for the target website and all relevant historical daily logs.
4. Run:

   ```bash
   python3 scripts/audit_queue.py --workspace /absolute/path/to/workspace --website "Website Name"
   ```

5. Compare the script result with the latest daily log's `Active CSV` and `Next cursor`.
6. Reconcile stale summaries against row-level progress. Treat the furthest verified persisted row as authoritative.
7. Write a `Run-start resume audit` entry to today's daily log containing:
   - previous daily-log filename
   - previous saved cursor
   - reconciled active CSV
   - exact next source key
8. Repair inconsistent records before interacting with any platform.

Never restart an exhausted CSV, return to an earlier processed row, or rely only on browser tabs or memory.

## Lifetime deduplication gate

Build a processed set for the target website from both `platform-progress.csv` and historical daily logs.

Normalize and compare:

- platform name
- hostname without case or leading `www`
- submission path
- evidence URL
- CSV source key
- `dedupe_key`

Apply these rules:

1. Treat a previously counted platform/domain as completed for that target website.
2. Do not create a new count because the platform changed its name, moved to another path, appears in another CSV, or has a second source key.
3. Do not count a refreshed scan, a new technical-report ID, an alternate `www` hostname, a different query string, or another DNS record type as a new backlink.
4. Do not resubmit an existing listing merely to produce another receipt.
5. Treat shared form hosts such as Typeform, Tally, Google Forms, and Airtable as separate only when their form paths or form IDs are different and the underlying destination platforms are genuinely different.
6. Record a duplicate candidate as terminal `duplicate-existing`, with the earlier evidence in notes.
7. Allow a repeat only when the user explicitly requests a re-audit, profile update, or repeat submission. Label it as a repeat and exclude it from the new-backlink count unless the user explicitly changes that counting rule.

## Ordered queue workflow

Process executable CSVs in the exact order listed in `platforms/queue.txt`.

For each target website:

1. Select the first truly unprocessed relevant row after the reconciled cursor.
2. Check the normalized URL and path against the blacklist.
3. Check the lifetime deduplication gate.
4. Exclude blacklisted, unsafe, irrelevant, or deceptive destinations.
5. Open the candidate only in the configured authorized browser profile.
6. Complete the ordinary submission flow with approved facts and assets.
7. Verify evidence.
8. Persist the outcome and next cursor before moving to another row.

Do not let a deferred row block later unprocessed rows. When a CSV has no remaining unprocessed relevant row, roll automatically to the next CSV. Never execute a file identified as a blacklist, blocklist, denylist, failure archive, or historical export.

## Platform priority

Prefer:

1. relevant product, SaaS, or tool directories
2. niche directories matching the target audience
3. legitimate public technical, security, or SEO reports
4. explicit add-URL or discovery submissions with confirmation

Reject:

- link farms and black-hat marketplaces
- fake review, vote, follower, comment, or identity requirements
- unrelated directories
- copied promotional articles or thin backlink pages
- security-warning or anti-abuse bypasses

Payment is the only ordinary checkpoint to skip automatically when the user has not approved spending. Record it as terminal `paid`.

## Authorized browser operation

Use a visible browser or computer-control tool when the task depends on an existing signed-in session, password manager, mailbox, or browser profile.

Before every interaction:

1. Confirm the visible browser profile matches the `Authorized Browser Profile` in the site profile.
2. Re-inspect after any window or profile switch.
3. Stop interacting if the wrong profile is active.
4. Never inspect or export cookies, passwords, tokens, recovery codes, browser databases, or private authentication state.

Continue ordinary non-payment checkpoints through visible controls:

- sign-in and account creation
- authorized OAuth
- magic links and email verification
- one-time codes from an already accessible authorized mailbox
- approved logo or screenshot uploads
- final submit buttons
- ordinary browser permission prompts

Do not bypass CAPTCHA, Cloudflare, security interstitials, rate limits, or anti-bot systems. Use only the narrow user handoff or action-time confirmation required by the active control tool, then resume.

If credentials, mailbox access, identity details, legal acceptance, CAPTCHA handoff, site-admin access, or another required permission is genuinely unavailable, preserve the exact operation node and record `deferred`. Continue with another candidate.

## Asset authorization

Treat the backlink task as authorization to upload assets that are clearly associated with the target site and explicitly present in its profile or site-specific asset folder.

Before upload:

1. Verify the requested file type and constraints.
2. Resolve the exact approved file.
3. Upload it through the visible authorized browser.
4. Verify the resulting filename or preview.

Never upload unrelated files, credentials, identity documents, financial records, private personal files, or an asset whose relationship to the target website is unclear.

## Evidence and counting

Count only when at least one clear platform-owned result exists:

- submitted
- submission received
- pending review
- scheduled
- live or public listing
- dashboard record representing the submitted site
- public verification page containing the target domain

Record the strongest evidence URL and a concise description of the visible proof.

Do not count:

- filled but unsubmitted forms
- drafts or incomplete profiles
- payment screens
- unresolved verification
- duplicates
- irrelevant platforms
- missing badges
- generic final pages that do not retain target-specific evidence
- prior listings found during a new-submission task

Technical reports are public-footprint evidence, not recommendations or editorial endorsements. Count each technical platform at most once per target website unless the user explicitly requests an audit inventory.

## State model

Use one progress row per target website and source key.

States:

- `unprocessed`: no meaningful attempt or disposition
- `deferred`: resumable checkpoint remains
- `terminal`: counted success or conclusive not-counted disposition

Common counted statuses:

- `submitted`
- `submission-received`
- `pending-review`
- `scheduled`
- `public`
- `live`
- `verified`

Common not-counted statuses:

- `duplicate-existing`
- `paid`
- `blacklisted`
- `not-relevant`
- `unavailable`
- `login-required`
- `email-verification`
- `captcha`
- `badge-required`
- `draft`
- `incomplete`
- `failed`
- `unclear`

Use `existing-active` only for an explicit existing-backlink audit, never for a daily new-backlink count.

## Immediate persistence rule

Before leaving each candidate:

1. Upsert its state, status, evidence URL, attempted time, and exact notes in `records/platform-progress.csv`.
2. Update today's count, active CSV, processed/deferred/remaining totals, and `Next cursor`.
3. Ensure `Next cursor` points to the first truly unprocessed relevant row.
4. Preserve any deferred browser draft without counting it.

Never keep a batch of inspected or submitted candidates only in memory. After interruption or hard stop, repeat the full run-start resume gate and continue from persisted state.

## Final report

Report:

1. target and counted total
2. each counted platform with evidence URL
3. duplicate, paid, terminal, and deferred outcomes
4. exact deferred operation nodes and missing access
5. active CSV
6. processed, deferred, and remaining counts
7. next source key
8. shortfall and reason when the target was not reached

State only what was verified. Never overstate SEO value, editorial endorsement, or placement quality.
