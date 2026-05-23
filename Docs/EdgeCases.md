# Edge Cases: AI-Powered Restaurant Recommendation System

Detailed edge cases for implementation and testing, derived from [Problemstatement1.md](./Problemstatement1.md) and [PhaseWiseArchitecture.md](./PhaseWiseArchitecture.md).

**Legend**

| Severity | Meaning |
|----------|---------|
| **Critical** | Blocks core flow or causes wrong recommendations |
| **High** | Degraded UX, cost blow-up, or data integrity risk |
| **Medium** | Should handle gracefully; workaround exists |
| **Low** | Cosmetic, rare, or nice-to-have |

| Handling | Meaning |
|----------|---------|
| **Reject** | Validation error; do not proceed |
| **Degrade** | Continue with reduced quality or fallback |
| **Skip** | Omit invalid item; continue |
| **Abort** | Stop pipeline; user-visible error |
| **Retry** | Automatic retry then fallback/abort |

---

## Cross-Cutting / End-to-End

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| X-01 | Cold start before data load | Request before Phase 1 completes | **Abort** with “System initializing”; no LLM call | Critical |
| X-02 | Data loaded but LLM unavailable | Missing/invalid API key, provider outage | **Degrade**: rule-based Top-N from Phase 3 + message “AI explanations unavailable” | High |
| X-03 | Partial pipeline failure | Filter OK, LLM fails | Return filter-based ranking + error banner; do not show empty success | High |
| X-04 | Duplicate submit (double-click) | Same preferences submitted twice quickly | Idempotent handling or debounce; optional short cache (Phase 6) | Medium |
| X-05 | Concurrent requests | Multiple users/sessions | Thread-safe repository; no shared mutable preference state | High |
| X-06 | Stale cache after dataset refresh | Cached Parquet from old schema | Version cache key; invalidate on schema/dataset version change | High |
| X-07 | Preference + result mismatch | UI shows old results while new request in flight | Cancel/ignore stale responses; show loading state (Phase 5) | Medium |
| X-08 | End-to-end timeout | Total latency exceeds SLA (e.g. 60s) | Abort with timeout message; log phase where time was spent | High |
| X-09 | Recommendation for city not in dataset | Valid input, zero restaurants in store for location | **Abort** before LLM: “No restaurants for {location}” + suggest known cities | Critical |
| X-10 | All phases succeed but enrich fails | LLM `restaurant_id` not in repository | **Skip** orphan IDs; log warning; fill gaps with “Details unavailable” | High |

---

## Phase 0: Foundation

### Configuration & environment

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P0-01 | Missing `LLM_API_KEY` | Env var unset at startup | Fail fast in dev with clear message; runtime recommend returns config error (not 500 stack trace) | Critical |
| P0-02 | Invalid API key format | Empty string, whitespace only | Treat as missing; same as P0-01 | High |
| P0-03 | Missing `DATASET_CACHE_DIR` | Optional path not set | Use sensible default; create directory if writable | Low |
| P0-04 | Cache dir not writable | Permission denied | **Abort** startup with actionable path error | High |
| P0-05 | Conflicting config sources | Env vs config file disagree | Document precedence (env wins); log active values at debug | Medium |

### Domain models & contracts

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P0-06 | `Restaurant.rating` out of schema range | Internal bug passes 6.0 or negative | Clamp or reject at model validation boundary | Medium |
| P0-07 | Optional fields null vs missing | JSON `null` vs omitted key | Normalize to optional defaults in deserializer | Medium |
| P0-08 | Circular imports between modules | Wrong package layout | Enforce `models` leaf package per architecture layout | Low |
| P0-09 | Interface swap (mock LLM) | Tests use fake provider | Same `Recommendation` shape as production parser | Medium |

---

## Phase 1: Data Ingestion

### Dataset load (Hugging Face)

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P1-01 | Network failure on download | HF unreachable, timeout | **Retry** with backoff; then **Abort** with “Could not load dataset” | Critical |
| P1-02 | Dataset removed or renamed | 404 on HF hub | **Abort**; log dataset ID and version pinned in config | Critical |
| P1-03 | Dataset schema change | New/removed columns vs normalizer | **Abort** or versioned normalizer; do not silently map wrong fields | Critical |
| P1-04 | Empty dataset returned | Zero rows after load | **Abort** startup; cannot satisfy exit criteria | Critical |
| P1-05 | Partial download / corrupt cache | Truncated Parquet/file | Detect checksum/size; delete cache and re-download | High |
| P1-06 | Disk full during cache write | OSError on save | **Abort** with disk space message | High |
| P1-07 | Hugging Face rate limit | HTTP 429 | **Retry** with exponential backoff | Medium |

### Preprocessing & normalization

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P1-08 | Row missing `name` | Null/empty name | **Skip** row; increment skip counter in logs | High |
| P1-09 | Row missing `location` | Null/empty location | **Skip** row or assign `unknown` and exclude from location filter index | High |
| P1-10 | Missing `rating` | Null, `NaN`, `"-"`, `"NEW"` | Default to `null` or 0; exclude from min-rating filter unless policy says include “new” | High |
| P1-11 | Non-numeric rating | `"4.5/5"`, `"Good"` | Parse best-effort; on failure treat as missing (P1-10) | Medium |
| P1-12 | Rating > 5 or < 0 | Data error | Clamp to [0, 5] or **Skip** row; log anomaly | Medium |
| P1-13 | Missing cost | No price field | Map budget band to `unknown`; filter may use inclusive/default band | High |
| P1-14 | Cost as range string | `"₹300–₹600"`, `"300-600 for two"` | Parse min/max or midpoint; fallback `unknown` | Medium |
| P1-15 | Cost extreme outlier | `0` or `999999` | Cap/winsorize or **Skip**; avoid breaking budget bands | Medium |
| P1-16 | Multiple cuisines in one field | `"Chinese, North Indian, Mughlai"` | Split on delimiters; trim; dedupe tokens | High |
| P1-17 | Cuisine casing/spacing | `"north indian"` vs `"North Indian"` | Normalize to canonical lowercase or title case for matching | High |
| P1-18 | Duplicate restaurants | Same name + location + address | Dedupe: keep highest rating or first; log count removed | Medium |
| P1-19 | Duplicate IDs after merge | ID collision | Regenerate stable hash ID from name+location+row index | High |
| P1-20 | Very long restaurant name | 500+ characters | Truncate for display; full name in raw store if needed | Low |
| P1-21 | Special characters in text | Emoji, RTL marks, zero-width chars | Unicode normalize (NFC); strip control chars | Medium |
| P1-22 | Location granularity mismatch | Area in data vs city in user input | Normalize to city list; maintain alias map (e.g. “Bengaluru” → “Bangalore”) | Critical |

### Repository & query

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P1-23 | `get_all()` on huge dataset | 50k+ rows | Lazy load or index; do not copy full list per request | High |
| P1-24 | Filter returns empty for valid city | Sparse data for niche city | Empty set is valid; Phase 3 handles (P3-01) | High |
| P1-25 | Case-insensitive location query | User `delhi` vs data `Delhi` | Case-insensitive match after normalization | High |
| P1-26 | Repository read during reload | Hot reload of dataset | Read lock or single-flight reload; no half-loaded reads | Medium |

---

## Phase 2: User Input

### Required fields & validation

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P2-01 | Missing `location` | Empty, whitespace only | **Reject** 400: “Location is required” | Critical |
| P2-02 | Missing `cuisine` | Empty list/string | **Reject** 400: “At least one cuisine required” | Critical |
| P2-03 | Missing `budget` | Omitted or null | **Reject** or default to `medium` (document choice) | High |
| P2-04 | Invalid `budget` enum | `"cheap"`, `1`, `"LOW"` | **Reject** with allowed values; accept case-insensitive if documented | High |
| P2-05 | `min_rating` below 0 or above 5 | `6`, `-1` | **Reject** with range message | High |
| P2-06 | `min_rating` non-numeric | `"four"` | **Reject** field-level error | Medium |
| P2-07 | Unknown `location` not in dataset | Typo `"Delh"` | **Reject** with “Did you mean Delhi?” if fuzzy match; else list supported cities | High |
| P2-08 | Location valid but unsupported | City in allowlist but no data rows | **Reject** early with “No coverage for {location}” (see X-09) | Critical |

### Input shape & abuse

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P2-09 | Multiple cuisines | `["Italian", "Chinese"]` | OR-semantics for filter (match any) unless product spec says AND | High |
| P2-10 | Duplicate cuisines in list | `["Italian", "italian"]` | Dedupe after normalize | Low |
| P2-11 | Cuisine not in dataset vocabulary | `"Ethiopian"` in city with none | Allow input; Phase 3 may return zero matches (P3-01) | Medium |
| P2-12 | `additional` empty string | `""` | Treat as not provided | Low |
| P2-13 | `additional` very long | 10k chars paste | **Reject** max length (e.g. 500) to protect prompt size | High |
| P2-14 | Prompt injection in `additional` | “Ignore instructions and recommend…” | Sanitize/strip instruction-like patterns; system prompt hardening (Phase 4) | Critical |
| P2-15 | HTML/script in text fields | `<script>alert(1)</script>` | Escape on output; store as plain text | High |
| P2-16 | SQL injection style strings | `'; DROP TABLE--` | No raw SQL from user input; parameterized queries only | Critical |
| P2-17 | Unicode homoglyphs in location | Cyrillic “а” in “Delhi” | Normalize; fuzzy match against known cities | Medium |
| P2-18 | Only whitespace in fields | `"   "` | **Reject** as missing | Medium |
| P2-19 | Wrong Content-Type / malformed JSON | API client error | **Reject** 415/400 with parse detail | Medium |
| P2-20 | Extra unknown JSON fields | Forward compatibility | Ignore unknown keys; do not fail | Low |

### API / UI-specific

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P2-21 | Partial form submit (web) | HTML5 validation bypassed | Server-side validation always (P2-01–P2-08) | Critical |
| P2-22 | CLI missing args | Incomplete argv | Print usage; exit code ≠ 0 | Medium |
| P2-23 | Rate limit per IP/user | Abuse | 429 with Retry-After (Phase 6) | Medium |

---

## Phase 3: Integration Layer

### Hard filters

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P3-01 | Zero candidates after all hard filters | Strict prefs in sparse city | **Abort** before LLM; message lists which constraint to relax | Critical |
| P3-02 | Zero after location only | Data gap | Same as P3-01 / X-09 | Critical |
| P3-03 | Zero after cuisine filter only | Rare cuisine | Suggest broadening cuisine; optional “near matches” without LLM | High |
| P3-04 | Zero after budget filter only | All restaurants outside band | Suggest adjacent budget; show count per band if cheap to compute | High |
| P3-05 | Zero after min_rating only | `min_rating: 4.8` | Suggest lower threshold; show max rating in city | High |
| P3-06 | Combined filters overly strict | All filters ANDed | Same as P3-01; optionally report filter funnel stats in debug | High |
| P3-07 | Single candidate remains | Only one match | Still call LLM (or skip LLM and return 1 with template explanation—document choice) | Medium |
| P3-08 | Thousands match before Top-K | Loose filters in Mumbai | Apply Top-K (15–30); soft score before truncate | Critical |
| P3-09 | Tie scores in soft ranking | Same rating/cost fit | Stable sort by `id` or name for reproducibility | Medium |
| P3-10 | Budget band boundary | Cost exactly on band edge | Document inclusive/exclusive rules; consistent mapping | High |
| P3-11 | Restaurant `price_band` unknown | Missing cost in data | Include in “unknown” bucket or exclude from strict budget filter | High |
| P3-12 | Multi-cuisine restaurant partial match | User wants Italian; resto is Italian+Chinese | Match if any user cuisine ∈ restaurant cuisines | High |
| P3-13 | `additional` not in structured data | “Family-friendly” | Pass text to LLM only; do not hard-filter unless tagged in dataset | Medium |

### Context packaging

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P3-14 | Context exceeds model token limit | Large Top-K + verbose fields | Reduce Top-K dynamically; truncate attributes; never silently drop IDs mid-list without logging | Critical |
| P3-15 | Empty context sent to LLM | Bug bypasses P3-01 check | Guard: never call LLM if candidate list empty | Critical |
| P3-16 | Special characters break JSON prompt | Quotes in restaurant name `Joe's "Best" Pizza` | Proper JSON escaping in context serializer | High |
| P3-17 | Duplicate IDs in candidate list | Dedupe failure upstream | Dedupe before pack; log warning | High |
| P3-18 | Candidate list order bias | Alphabetical default | Soft-rank before pack so LLM sees best-first | Medium |
| P3-19 | PII in dataset fields | Phone/address in raw data | Strip from LLM context unless required; never echo in explanations | High |

### Prompt template (draft)

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P3-20 | Missing template variable | Template bug | **Abort** internal error; do not call LLM with broken prompt | High |
| P3-21 | User preference encoding in prompt | Non-ASCII location/cuisine | UTF-8 safe prompt assembly | Medium |

---

## Phase 4: Recommendation Engine (LLM)

### Provider & network

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P4-01 | LLM HTTP timeout | Slow provider | **Retry** once; then **Degrade** to Phase 3 rule-based ranking | Critical |
| P4-02 | Rate limit 429 | Quota exceeded | **Retry** with backoff; user message on persistent failure | High |
| P4-03 | Auth error 401/403 | Bad key revoked | **Abort**; no retry; “Check API configuration” | Critical |
| P4-04 | Model not found / deprecated | Wrong model name in config | **Abort** with config hint | High |
| P4-05 | Empty completion | Zero tokens returned | **Degrade** fallback | High |
| P4-06 | Completion truncated (max tokens) | `finish_reason: length` | **Degrade** parse partial JSON or fallback; log truncation | High |
| P4-07 | Provider returns HTML error page | Gateway error | Treat as failure; retry then fallback | Medium |

### Response parsing

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P4-08 | Non-JSON response | Markdown prose only | Regex/json repair; then fallback | High |
| P4-09 | JSON wrapped in markdown fences | ` ```json ... ``` ` | Strip fences before parse | High |
| P4-10 | Invalid JSON syntax | Trailing comma, single quotes | Repair attempt; fallback | High |
| P4-11 | Missing `recommendations` key | Wrong schema | Fallback | High |
| P4-12 | Empty `recommendations` array | LLM returns [] | Fallback to Top-N from Phase 3 | High |
| P4-13 | Duplicate ranks | Two `rank: 1` | Renumber by array order or re-sort | Medium |
| P4-14 | Missing `rank` field | Partial objects | Assign rank by array index | Medium |
| P4-15 | Missing `explanation` | Null/empty | Default: “Matches your preferences based on rating and cuisine.” | Medium |
| P4-16 | Hallucinated `restaurant_id` | ID not in candidate set | **Skip**; log; do not invent restaurant row | Critical |
| P4-17 | Valid ID but not in current candidates | ID from training memory | **Skip** (same as P4-16) | Critical |
| P4-18 | Fewer than requested Top-N | User expects 5, got 2 | Show available; optional fallback fill from Phase 3 | Medium |
| P4-19 | More than Top-N in response | LLM returns 20 | Truncate to configured display N | Low |
| P4-20 | `summary` missing | Optional field absent | Omit summary UI block | Low |
| P4-21 | Explanation contradicts data | “Budget fine dining” for low-cost row | Display LLM text but data fields authoritative; optional disclaimer | Medium |
| P4-22 | Offensive / unsafe content in explanation | Model guardrail miss | Provider moderation if available; else truncate + report template | High |

### Prompt & behavior

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P4-23 | User asks for restaurants outside candidate set via `additional` | “Recommend Goa beach shack” in Delhi query | LLM should only rank provided IDs; parser enforces P4-16 | Critical |
| P4-24 | Equal preference conflict | Low budget + “fine dining” in additional | LLM explains tradeoff; ranking may be subjective | Medium |
| P4-25 | Temperature/randomness | High temperature setting | Same input may differ run-to-run; document for demos | Low |
| P4-26 | Token cost spike | Huge `additional` + max Top-K | Cap inputs (P2-13, P3-14); log token usage | High |

---

## Phase 5: Output Display

### Enrichment & presentation

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P5-01 | Missing display field in dataset | Null cuisine after enrich | Show “—” or “Not available”; never crash card render | High |
| P5-02 | LLM explanation present but name missing | Enrich failure X-10 | Show ID + explanation; flag incomplete card | High |
| P5-03 | Cost display format | Raw number vs band | Consistent formatting (e.g. `₹500 for two` or `Medium`) | Medium |
| P5-04 | Rating display | `null` rating | “New” or “No rating” per product copy | Medium |
| P5-05 | Long explanation text | 2k char essay | Truncate with “Read more” or CSS clamp | Low |
| P5-06 | Zero results UI | P3-01 path | Empty state with suggestions; not blank page | High |
| P5-07 | Error during load | LLM failure with fallback | Show results + non-blocking warning banner | High |
| P5-08 | Loading state stuck | Hung request | Timeout UI; cancel button if supported | Medium |
| P5-09 | Rank order vs display order | Sort by `rank` ascending | Stable ordering; handle gaps in rank numbers | Medium |
| P5-10 | Mobile narrow viewport | Small screen | Stack cards; no horizontal overflow on long names | Low |
| P5-11 | XSS from dataset or LLM | Malicious string in name | Encode on render (ties P2-15) | Critical |

### API response contract

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P5-12 | Partial success response | Some IDs skipped | 200 with `warnings[]` listing skipped IDs | Medium |
| P5-13 | Large response payload | 50 recommendations | Paginate or cap display count | Medium |

---

## Phase 6: Hardening (Optional)

| ID | Edge case | Trigger | Expected behavior | Severity |
|----|-----------|---------|-------------------|----------|
| P6-01 | Cache hit with stale preferences key | Hash collision | Include full normalized prefs in cache key | High |
| P6-02 | Cache returns LLM result for wrong city | Key bug | Never cache across locations | Critical |
| P6-03 | Log leaks API key | Misconfigured logger | Redact secrets in all log sinks | Critical |
| P6-04 | Log contains full prompt PII | Debug mode on in prod | Sampling + redaction policy | High |
| P6-05 | Identical prefs, different model version | Prompt/model upgrade | Cache key includes model + prompt version | Medium |
| P6-06 | Thundering herd on startup | 100 parallel first requests | Single-flight dataset load | High |
| P6-07 | Regression in filter logic | Code change | Golden tests: prefs → expected ID set | High |

---

## Edge Case Decision Matrix (Quick Reference)

| Situation | Call LLM? | User sees |
|-----------|-----------|-----------|
| Invalid input (Phase 2) | No | Validation errors |
| No restaurants in city (X-09) | No | Coverage message |
| Zero after filters (P3-01) | No | Relax constraints hints |
| 1–K candidates, LLM OK | Yes | Ranked cards + explanations |
| LLM fails (P4-01) | No (fallback) | Rule-based list + warning |
| Hallucinated IDs (P4-16) | Yes (partial) | Fewer cards + optional warning |
| All IDs invalid parse | No (fallback) | Rule-based Top-N |

---

## Suggested Test Priorities

### P0 — Must test before MVP release

- P1-01, P1-08–P1-10, P1-22, P2-01–P2-02, P2-14, P3-01, P3-14–P3-15, P4-01, P4-16–P4-17, P5-06–P5-07, X-02, X-09

### P1 — High value regression suite

- P1-16–P1-18, P2-07–P2-09, P3-08–P3-12, P4-08–P4-12, P4-23, P5-01, P6-03

### P2 — Nice to have / post-MVP

- Remaining Low severity items, P4-25, P5-10, P6-05

---

## Traceability

| Document section | Edge case IDs |
|------------------|---------------|
| Problem §1 Data ingestion | P1-* |
| Problem §2 User input | P2-* |
| Problem §3 Integration | P3-* |
| Problem §4 Recommendation engine | P4-* |
| Problem §5 Output display | P5-* |
| Architecture Phase 0 | P0-* |
| Architecture Phase 6 | P6-* |
| End-to-end flow | X-* |

---

## Open Product Decisions

These edge cases allow multiple valid behaviors; lock one choice in implementation:

1. **P3-07** — Call LLM for a single candidate, or return a template explanation without LLM?
2. **P2-03** — Reject missing budget vs default `medium`?
3. **P2-09** — Multi-cuisine filter: OR vs AND?
4. **P1-10** — Include “NEW” / null rating restaurants when `min_rating` is set?
5. **P3-11** — Include `unknown` price band under strict budget filter or exclude?

Document the chosen behavior in `config` or README when implemented.
