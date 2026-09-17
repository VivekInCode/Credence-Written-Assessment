# Credence Written Assessment

Python transformation service for provider JSON. Node.js owns third-party API calls, authentication and retries. This service interprets, validates and transforms the resulting JSON.

Python 3.11+. Tests: `pip install -r requirements.txt` then `python -m pytest -q`.

---

## Task 1 — Existing Code Observations

- **India** treats `director_shareholdings == "Not available"` as empty, drops any record with a non-null `date_of_cessation`, then de-duplicates on `din_pan` falling back to `full_name`. Output keeps the existing field names (`Name`, `Designation`, `Shareholding (%)`, `Number of Share`).
- **India** previously copied `percentage_holding` with `str(...)`. `None` therefore became the string `"None"`, and there was no fallback to company-level `total_issued_shares`. That is the behaviour this change replaces for missing/null percentages.
- **India** assumes `section_data[0]` is the company object and that share counts are numeric enough for `format_with_commas`. Duplicate people with different `din_pan` values are not merged.
- **China** walks `directorSupervisors[]`, reads nested `directorSupervisorBase`, and emits `{name, position}` only when `fullName` or `position` is non-empty after strip. Other nested fields (e.g. `dataId`) are unused. The existing output is **not** the global `active_management` shape (`position` vs `role_title`).
- **Risks:** provider schemas differ (India shareholding rows vs China nested officers). Dedup keys can collide on blank/`full_name` duplicates. Calculated percentages depend on `total_issued_shares` being the correct denominator; a supplied percentage is never overwritten, so provider and calculated figures can disagree.

### India change

When `percentage_holding` is missing or null, set `Shareholding (%)` from `(no_of_shares / total_issued_shares) * 100`. A supplied numeric value — including `0` — is preserved. If shares or total are missing, non-numeric, or total is `0`, the percentage is `""` and the rest of the run continues.

**Formatting:** the same helper formats supplied and calculated values via `Decimal`. Integers render as `"25"`, non-integers as `"12.5"`. No extra decimal places, no float noise such as `12.500000000000002`. Empty string matches the existing “unavailable” convention (`s.get(..., "")`).

### Intentionally changed vs left unchanged

- **Changed:** missing/null `percentage_holding` is calculated when safe; malformed supplied percentages become `""` rather than `"None"` or a guessed number; empty/`None` `section_data` returns `[]` instead of raising.
- **Unchanged:** cessation filter, `"Not available"` handling, `din_pan`/`full_name` dedupe, output field names, `format_with_commas` for `Number of Share`, China logic (aside from skipping non-dict rows so bad JSON cannot crash the loop).

---

## Task 2 — Assumptions / Questions

1. Singapore `id` is mapped only to `official_identifier`. What identifier type is it (national ID, company officer ID, provider key)? `identifier_type` is left blank until that is defined.
2. Can `principalName` always be treated as the canonical `name`, or can it be a local/alias form that belongs in `alternate_name`?
3. Is `dateOfAppointment` always the *current* appointment date (vs original appointment), and is `nationalityCitizenship` the same concept as global `nationality` (citizenship vs nationality vs incorporation)?

---

## Task 3A — Maintainability

- Keep **one module per provider** (as here: `india.py`, `china.py`, `singapore.py`) so a 15th provider is an add, not an edit to unrelated adapters.
- Keep **provider-to-global mapping inside that module**. Do not share a single mega-dict of field names across countries; similar names are not the same semantics (`position` vs `role_title`).
- Share only **mechanics**: number/date formatting, missing-value checks, “empty list on bad payload”. Do not share business rules such as India cessation/dedupe unless a second provider truly has the same rule.
- Keep a **stable global output contract** (`active_management`, `management_ownership`) and map into it only where the source meaning is clear. Existing India/China shapes stay as they are until a deliberate migration.
- Treat provider exceptions **explicitly** (`"Not available"`, nested China `directorSupervisorBase`, Singapore `officer`) rather than hiding them in a generic mapper.
- **Tests per provider** with hardcoded fixtures (this assessment’s style); one new provider = one new test module, no need to re-run interpretation of other countries’ JSON.
- **Do not** introduce a mapping DSL, plugin framework, or shared ORM. At 15–20 providers, folders + a one-line router (`transform.py`) are enough.
- Add **structured logs** (provider, record count, skipped/unmapped fields) at the adapter boundary; leave Node.js responsible for HTTP retries and auth.

---

## Task 3B — Impact Analysis

- Inventory **Python producers** of `role_title` (Singapore now; any later adapters) and every **test/fixture** that asserts that key.
- Coordinate **downstream consumers**: product APIs, Node.js response shaping, frontends, search/index documents, caches, and any stored/serialized company payloads that still contain `role_title`.
- Decide **compatibility**: dual-write both keys, API version bump, or coordinated deploy — a Python-only rename will break clients that still read `role_title`.
- Update **schemas/docs/monitors** (OpenAPI, log field names, dashboards that filter on `role_title`) in the same change window.
- Sequence the release: consumers tolerant of the new name first (or dual-read), then Python rename, then remove the old key; avoid a silent cache of old JSON sitting in front of the new contract.
