# Google Stitch UI Prompt — ZM Restaurant Recommendations

Use this document when generating UI in **[Google Stitch](https://stitch.withgoogle.com)** (or similar design-to-code tools). The production frontend is **Next.js 15 (App Router)** with **TypeScript** and **React 19**. Designs should map cleanly to that stack.

**How to use**

1. Open Google Stitch and start a new UI project.
2. Copy the entire prompt in [Section 2](#2-copy-paste-prompt-for-google-stitch) into Stitch.
3. Optionally attach [Problemstatement1.md](./Problemstatement1.md) or screenshots of the current app for refinement.
4. Export or hand off designs to implement under `frontend/` (`app/`, `components/`, `lib/api/`).

---

## 1. Product summary (context for designers)

**Product name:** ZM — AI-Powered Restaurant Recommendations  
**Inspiration:** Zomato-style discovery; data from a real restaurant dataset; rankings and explanations powered by Groq LLM on the server (never in the browser).

**Single-page flow:** User sets preferences → submits → sees ranked restaurant cards with AI explanations.

**Backend:** Separate FastAPI REST API (`http://localhost:8000`). The Next.js app calls it via `fetch` (dev: Next.js rewrites `/api/*` to the API).

---

## 2. Copy-paste prompt for Google Stitch

Copy everything inside the block below into Google Stitch:

---

```
Design a complete, production-quality web UI for "ZM — AI-Powered Restaurant Recommendations", a Zomato-inspired discovery app. The implementation framework is Next.js 15 (App Router), TypeScript, React 19, and CSS Modules or global CSS (no heavy UI kit required unless it fits the design). Mobile-first, responsive desktop two-column layout.

BRAND & VISUAL DIRECTION
- Modern food/discovery app feel; trustworthy and premium but approachable.
- Dark theme preferred: deep navy/charcoal background (#0f1419), elevated panels (#1a2332), subtle borders (#2d3a4f), primary accent blue (#3d9cf5), muted text (#8b9cb3), warning amber, error red.
- Typography: clean system UI or geometric sans (Segoe UI / Inter style). Clear hierarchy: page title, section titles, labels, hints, errors.
- Rounded corners (~10px panels, 6px inputs). Generous spacing; accessible contrast (WCAG AA).

PAGE STRUCTURE (single home page)
1) Header
   - Title: "ZM Restaurant Recommendations"
   - Subtitle: "AI-powered picks from real restaurant data — smart filters plus Groq explanations"
   - No global nav needed (single-page app).

2) Alert zone (below header, full width)
   - Error alert: API unreachable / data not loaded (e.g. "Run zm load-data then zm api")
   - Warning alert: loading state or Groq fallback warning from API
   - Info optional: none by default

3) Two-column layout on tablet/desktop (stacked on mobile)
   LEFT COLUMN — "Your preferences" (form panel)
   RIGHT COLUMN — "Recommendations" (results panel)

LEFT: PREFERENCE FORM
Fields (top to bottom):
- City (required): dropdown/select populated from API (e.g. Bangalore). Placeholder "Select a city".
- Area (optional): text input, placeholder "e.g. Bellandur"
- Budget section with toggle:
  - Checkbox: "Budget in ₹ (for two)" (default ON)
  - When ON: numeric input for INR amount (default 2000, min 100, max 50000), helper text explaining bands: "≤₹600 → low, ₹601–₹2000 → medium, >₹2000 → high (for two)"
  - When OFF: dropdown low | medium | high
- Cuisines (required): text input, comma-separated, placeholder "North Indian, Italian, Chinese" with hint "Comma-separated"
- Minimum rating: number input 0–5, step 0.1, default 4.0
- Additional notes: textarea 3 rows, placeholder about budget for two, ambiance, dietary needs
- Primary CTA button: "Get recommendations" (full width or prominent). Loading state label: "Finding restaurants…"
- Inline field errors in red under each field; form-level error banner at bottom of form if no matches

Form states: disabled when data not loaded; loading disables submit and shows spinner or loading text on button.

RIGHT: RECOMMENDATIONS PANEL
Empty state: "Submit the form to see ranked restaurants."
Loading state: "Searching and ranking…"
Results state:
- Optional summary line from API (one sentence)
- Source line: "Ranked by Groq AI" or "Ranked by Rule-based" with optional "· served from cache"
- Vertical list of 3–5 recommendation CARDS

Each recommendation CARD must show:
- Rank badge (#1, #2, …) in accent color
- Restaurant name (prominent heading)
- Three meta columns in a row: Cuisine | Rating (e.g. 4.2 or N/A) | Cost (e.g. "₹2,000 for two")
- AI explanation paragraph (muted body text, 2–4 lines)

Card design: darker inset background on panel, border, padding; hover subtle lift optional.

INTERACTION & UX
- Submit form → loading → results or errors (422 validation, 404 no matches)
- Do not show API keys or internal IDs to users except optional small rank; restaurant_id can be hidden
- Touch-friendly tap targets on mobile
- Focus states on inputs for keyboard users

DO NOT INCLUDE IN UI
- Login/signup, maps, photos (dataset has no images), cart/checkout, reviews list
- Direct LLM chat box (recommendations are batch-generated on submit)

TECHNICAL NOTES FOR HANDOFF TO NEXT.JS
- One page route: app/page.tsx hosting a client component RecommendPage
- Components: PreferenceForm, RecommendationList, RecommendationCard, Alert (variants: info, warning, error)
- API client calls:
  GET /api/v1/locations → { locations: string[] }
  GET /api/v1/metadata → { budgets, example_cuisines, display_top_n, budget_inr_bands }
  POST /api/v1/recommendations → body: { location, budget OR budget_inr, cuisines[], min_rating, additional?, area? }
- Success response includes recommendations[] with: rank, name, cuisines[], rating, estimated_cost, explanation
- Use env NEXT_PUBLIC_API_BASE_URL or same-origin rewrites in dev

DELIVERABLES FROM STITCH
- Desktop (1280px) and mobile (390px) frames for: empty, loading, success with 5 cards, validation error, no-results error, API-down error
- Component specs for form controls, alerts, cards, buttons
- Color and type tokens documented for CSS variables
```

---

## 3. Screen checklist (verify Stitch output)

| Screen | What to show |
|--------|----------------|
| Empty | Form enabled, results placeholder |
| Loading | Button loading, results panel "Searching and ranking…" |
| Success | 3–5 cards with rank, name, cuisine, rating, cost, explanation |
| Validation error | Red messages on fields (e.g. invalid city) |
| No match | Form-level error: no restaurants match |
| API down | Top error alert, form disabled |
| Warning | Amber banner when AI fallback or cache (optional) |
| Mobile | Single column, stacked panels |
| Desktop | Two columns: form left, results right |

---

## 4. API contract (for design ↔ dev alignment)

Designs should assume these labels and data shapes (not visible raw JSON):

**Request (on submit)**

| Field | UI control | Notes |
|-------|------------|--------|
| `location` | City dropdown | Required |
| `area` | Text | Optional neighborhood |
| `budget_inr` | Number | When ₹ toggle on |
| `budget` | Dropdown | When ₹ toggle off: low/medium/high |
| `cuisines` | Text → array | Comma-separated |
| `min_rating` | Number | 0–5 |
| `additional` | Textarea | Optional, max 500 chars |

**Each result card**

| Label | API field |
|-------|-----------|
| Rank | `rank` |
| Name | `name` |
| Cuisine | `cuisines` (joined) |
| Rating | `rating` |
| Cost | `estimated_cost` |
| Why recommended | `explanation` |

---

## 5. Mapping Stitch output to this repo

| Stitch / design artifact | Repo path |
|--------------------------|-----------|
| Home / main screen | `frontend/src/app/page.tsx`, `frontend/components/RecommendPage.tsx` |
| Form | `frontend/components/PreferenceForm.tsx` |
| Result cards | `frontend/components/RecommendationCard.tsx`, `RecommendationList.tsx` |
| Alerts | `frontend/components/Alert.tsx` |
| Global styles / tokens | `frontend/src/app/globals.css` |
| API types | `frontend/lib/api/types.ts` |
| API client | `frontend/lib/api/client.ts` |

After importing a Stitch design, keep `"use client"` on interactive components and preserve existing `fetch` calls to `/api/v1/*`.

---

## 6. Optional follow-up prompts for Stitch

Use these as **second messages** to refine a generated screen:

**Refinement — mobile**

```
Tighten the mobile layout (390px): single column, sticky bottom CTA optional, larger touch targets on the submit button, recommendation cards full width with meta grid stacking to 2 columns on very narrow screens.
```

**Refinement — accessibility**

```
Increase label contrast, add visible focus rings on all inputs, ensure error text is announced visually with icons, and keep minimum 44px tap height for buttons.
```

**Refinement — light theme variant**

```
Provide an optional light theme variant using white/off-white surfaces and dark text while keeping the same layout and components for Next.js theme toggle later.
```

---

## Related docs

- [Problemstatement1.md](./Problemstatement1.md) — product requirements  
- [PhaseWiseArchitecture.md](./PhaseWiseArchitecture.md) — phases 5a/5b/6 and Next.js layout  
- [README](../README.md) — run `zm api` and `npm run dev` in `frontend/`
