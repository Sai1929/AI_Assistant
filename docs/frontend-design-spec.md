# Christianity AI Assistant — Frontend Design Spec

> Paste this into **Claude claude.ai/design** (or share with a UI designer).  
> Target: replace the current Streamlit prototype with a production-quality React/Next.js web app.

---

## 1. Product Overview

**What it is:** A scripture-grounded AI assistant for Christians. Users ask about Bible verses, theology, prayer, and Christian history. The AI cites real scripture (verified against KJV/DRA/WEB translations), respects denomination differences (Catholic, Protestant, Orthodox), generates Christian-themed art, and refuses harmful or manipulative requests gracefully.

**Backend:** FastAPI at `http://localhost:8000`  
**Key API endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/chat` | Send message, get response + optional image |
| `DELETE` | `/session/{id}` | Clear conversation memory |
| `GET` | `/session/{id}/history` | Retrieve history |
| `GET` | `/health` | Liveness check |

**POST /chat request:**
```json
{ "session_id": "uuid-string", "message": "What does John 3:16 say?" }
```

**POST /chat response:**
```json
{
  "session_id": "uuid",
  "response": "For God so loved the world...",
  "image_b64": null,
  "intent": "scripture_qa",
  "denomination": "protestant",
  "toxicity_ok": true
}
```

When `image_b64` is non-null: render it as a base64 PNG/JPEG image inline.  
When `intent === "image_gen"` and `image_b64` is null: response contains a refusal message — show as a warning, not an error.

---

## 2. Visual Identity

### Tone
Reverent but modern. Not dated "stained glass" kitsch. Think: contemplative, clean, trustworthy — like a well-designed Bible study app.

### Color Palette

| Role | Color | Notes |
|------|-------|-------|
| Primary | `#1B4F72` (deep navy blue) | Faith, depth, trust |
| Accent | `#D4A017` (warm gold) | Scripture highlights, CTAs |
| Surface | `#FAF7F2` (warm off-white) | Page background — warmer than pure white |
| Card | `#FFFFFF` | Message bubbles, panels |
| Text primary | `#1C1C1C` | Body text |
| Text muted | `#6B7280` | Metadata, timestamps, labels |
| Success | `#16A34A` | Verse verified badges |
| Warning | `#D97706` | Soft refusals, caveats |
| Error | `#DC2626` | Connection errors only |
| Divider | `#E5E0D8` | Borders, separators |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| App title | Playfair Display or Lora (serif) | 22px | 700 |
| Section headers | Inter or system-ui (sans) | 16px | 600 |
| Body / chat | Inter | 15px | 400 |
| Scripture quote | Lora italic | 16px | 400 italic |
| Metadata / muted | Inter | 13px | 400 |
| Code/reference | JetBrains Mono | 13px | 400 |

### Iconography
Use **Lucide React** icons (clean, minimal line icons). Key icons:
- Cross / book → app logo
- `BookOpen` → scripture intent badge
- `Church` → theology intent badge
- `Image` → image generation tab
- `BarChart2` → eval tab
- `Trash2` → clear session
- `ChevronDown` → denomination selector
- `Shield` → safety/refusal indicator
- `Sparkles` → AI generating indicator

### Motion
Subtle only. Message bubbles fade-in (200ms ease-out). Typing indicator (3-dot pulse). No heavy animations — users may be reading scripture in a focused state.

---

## 3. Layout

### Shell (all pages)

```
┌─────────────────────────────────────────────────────────────┐
│  SIDEBAR (260px fixed)  │  MAIN CONTENT AREA (flexible)     │
│                         │                                    │
│  [Logo + App Name]      │  [Tab Bar: Chat | Image | Eval]   │
│  [Denomination Select]  │                                    │
│  ─────────────────────  │  [Active tab content]             │
│  [Session ID]           │                                    │
│  [Clear Session btn]    │                                    │
│  ─────────────────────  │                                    │
│  [About / Help link]    │                                    │
│                         │                                    │
└─────────────────────────────────────────────────────────────┘
```

On mobile (< 768px): sidebar collapses to a hamburger menu. Tab bar becomes bottom navigation bar.

---

## 4. Sidebar Detail

### Logo area
- Small cross icon (SVG, 20×20px, gold `#D4A017`)
- App name: "Christianity AI" in Playfair Display, navy
- Tagline: "Scripture-grounded · Denomination-aware" in muted text, 12px

### Denomination Selector
Custom styled `<select>` or dropdown component:

```
┌─────────────────────────────┐
│ Denomination           ▾    │
│ ● (auto-detect)             │
│   Catholic                  │
│   Protestant                │
│   Orthodox                  │
└─────────────────────────────┘
```

- Selected state shows denomination icon/badge next to name
- "auto-detect" is default — the AI classifier picks up from conversation
- Changing denomination does NOT reset conversation (server handles it)
- Display only — denomination is passed as context in the message if explicitly set (prepend `[Denomination: Catholic]` to the message string), OR just used for UI labeling

### Session Info
```
Session  a3f2b1c9…     [Copy icon]
```
Small monospace, muted color. Copy button copies full UUID.

### Clear Session Button
- Full-width, outlined style (not filled — destructive action)
- Border: `#DC2626`, text: `#DC2626`
- Hover: light red background `#FEF2F2`
- Clicking: shows confirmation modal (see Section 7)

### About / Help
Bottom of sidebar. Small link: "About · How it works · GitHub"

---

## 5. Tab 1: Chat

### Tab bar
Three tabs at top of main area:
```
[ 💬 Chat ]  [ 🖼️ Image ]  [ 📊 Eval ]
```
Active tab: bottom border `#D4A017` gold, text navy. Inactive: muted gray.

### Chat message list

**User message bubble:**
```
                              ┌──────────────────────────────┐
                              │ What does John 3:16 say?     │
                              │                      2:34 PM │
                              └──────────────────────────────┘
```
- Aligned right
- Background: `#1B4F72` (navy), text white
- Border radius: 16px 16px 4px 16px
- Max width: 70%
- Timestamp: small, bottom-right, white 70% opacity

**Assistant message bubble:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📖  scripture_qa  ·  KJV  ·  Protestant                    │
│─────────────────────────────────────────────────────────────│
│ For God so loved the world, that he gave his only           │
│ begotten Son, that whosoever believeth in him should        │
│ not perish, but have everlasting life.                      │
│                                                             │
│ ┌─────────────────────────────────────────────┐            │
│ │ 📜  John 3:16 (KJV)                    ✓   │            │
│ └─────────────────────────────────────────────┘            │
│                                                    2:34 PM  │
└─────────────────────────────────────────────────────────────┘
```
- Aligned left
- Background: `#FFFFFF`, border: `1px solid #E5E0D8`
- Border radius: 4px 16px 16px 16px
- Max width: 80%
- **Header row** (inside bubble): intent badge + translation + denomination — small, muted
- **Scripture citation chip**: pill shape, gold border, left icon 📜, right checkmark ✓ in green when verified
- If citation UNVERIFIED: amber ⚠ instead of green ✓, tooltip "Reference could not be verified in our Bible database"

**Intent badge styles:**

| Intent | Icon | Background | Text |
|--------|------|-----------|------|
| scripture_qa | 📖 | `#EFF6FF` | `#1D4ED8` |
| theology | ✝ | `#F5F3FF` | `#6D28D9` |
| image_gen | 🖼️ | `#FFF7ED` | `#C2410C` |
| contradiction | ⚖️ | `#FEF9C3` | `#854D0E` |
| general_chat | 💬 | `#F0FDF4` | `#166534` |
| refuse | 🛡️ | `#FFF1F2` | `#9F1239` |

**Refusal message style:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🛡️  Safety                                                 │
│─────────────────────────────────────────────────────────────│
│ I can't rewrite scripture to support an ideology. I'd be   │
│ happy to discuss the historical interpretations of this    │
│ passage instead.                                           │
└─────────────────────────────────────────────────────────────┘
```
Subtle amber-tinted background `#FFFBEB`, left border `4px solid #D97706`.

**Inline image (from image_gen):**
```
┌─────────────────────────────────────────────────────────────┐
│ 🖼️  image_gen                                              │
│─────────────────────────────────────────────────────────────│
│ [Generated image renders here, max-height 400px]           │
│                                                             │
│ [⬇ Download]  [🔗 Share]          Prompt: nativity scene  │
└─────────────────────────────────────────────────────────────┘
```

### Typing indicator
While waiting for API response:
```
┌─────────────────┐
│  ● ● ●          │   (pulsing 3 dots, 600ms cycle)
└─────────────────┘
```
Appears in assistant bubble position. Disappears when response arrives.

### Chat input bar
Fixed to bottom of chat area:
```
┌─────────────────────────────────────────────────────────────┐
│ [Cross icon]  Ask about scripture, theology, or prayer…  [→]│
└─────────────────────────────────────────────────────────────┘
```
- Full-width, border: `1px solid #E5E0D8`, focus: `#D4A017` gold border
- Cross icon left: decorative, gold, 16px
- Send button right: navy background, gold arrow icon, disabled when empty
- `Shift+Enter` = newline, `Enter` = send
- Max textarea height: 120px before scrolling
- Character counter shows when >1500 chars (limit 2000): `1723 / 2000`

### Suggested prompts (empty state)
When no messages, show 4 suggestion chips:
```
┌─────────────────────┐  ┌─────────────────────┐
│ 📖 What does        │  │ ✝ How do Catholics  │
│    John 3:16 say?   │  │   view Mary?        │
└─────────────────────┘  └─────────────────────┘
┌─────────────────────┐  ┌─────────────────────┐
│ 🕊 Generate a       │  │ 📜 What is the      │
│   nativity scene    │  │   Sermon on Mount?  │
└─────────────────────┘  └─────────────────────┘
```
Clicking a chip fills the input and submits.

---

## 6. Tab 2: Image Generation

Dedicated image generation UI — separate from chat.

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  Generate Christian Art                                     │
│  Two-stage safety review · Gemini image model               │
│─────────────────────────────────────────────────────────────│
│                                                             │
│  Prompt                                                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Describe the image you'd like...                      │ │
│  │                                                       │ │
│  │                                        0 / 500 chars  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────┐                      │
│  │  Quick prompts:                  │                      │
│  │  [Nativity scene] [The Shepherd] │                      │
│  │  [Baptism of Jesus] [The Cross]  │                      │
│  └──────────────────────────────────┘                      │
│                                                             │
│  [       ✨ Generate Image       ]  (full-width, navy btn) │
│                                                             │
│─────────────────────────────────────────────────────────────│
│                                                             │
│  [Generated image or placeholder]                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Generation states

**Idle (no image yet):**
Placeholder area: `#FAF7F2` background, dashed border `#E5E0D8`, centered icon + text "Your generated image will appear here"

**Loading:**
Progress indicator + text cycling through:
- "Checking prompt safety…" (1s)
- "Generating image…" (5–20s)
- "Reviewing image content…" (1s)

Show estimated wait time: "~15 seconds"

**Success:**
```
┌─────────────────────────────────────────────────────────────┐
│  [Full image, max-height 500px, object-fit: contain]       │
│─────────────────────────────────────────────────────────────│
│  Prompt rewritten to: "A serene nativity scene…"   ✓ Safe  │
│  [⬇ Download PNG]  [Generate another]                      │
└─────────────────────────────────────────────────────────────┘
```

**Refusal (soft):**
```
┌─────────────────────────────────────────────────────────────┐
│  🛡️  Image not generated                                   │
│─────────────────────────────────────────────────────────────│
│  I avoid generating photorealistic depictions of God the   │
│  Father. I can create symbolic imagery instead — a dove,   │
│  rays of light, or outstretched hands.                     │
│                                                             │
│  [Try suggested prompt]                                    │
└─────────────────────────────────────────────────────────────┘
```
Amber-tinted card, same refusal style as chat.

---

## 7. Tab 3: Eval Results

### Layout (results exist)
```
┌─────────────────────────────────────────────────────────────┐
│  Evaluation Results                    [🔄 Refresh]        │
│─────────────────────────────────────────────────────────────│
│  ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│  │ Pass Rate │  │  Passed   │  │  Failed   │              │
│  │  84.0%    │  │  42 / 50  │  │    8      │              │
│  └───────────┘  └───────────┘  └───────────┘              │
│                                                             │
│  By Category                                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ scripture_qa     ████████████░░  10/12  83%         │  │
│  │ theology         ██████████████  10/10  100%        │  │
│  │ safety_refusal   ████████████░░  10/12  83%         │  │
│  │ image_gen        ████████████    5/6    83%         │  │
│  │ denomination     ██████████████  6/6    100%        │  │
│  │ contradiction    ████████        4/4    100%        │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  Detailed Results           [Filter: All ▾] [Search…]     │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ ID          Category     Input         Pass  Intent │  │
│  │ scripture_1 scripture_qa What does J…  ✓     scrip… │  │
│  │ safety_3    safety_refu… Rewrite John… ✓     refuse │  │
│  │ theology_2  theology     What is the … ✓     theol… │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Layout (no results)
```
┌─────────────────────────────────────────────────────────────┐
│  No results yet                                             │
│                                                             │
│  Run the evaluation script to generate results:            │
│  $ python scripts/run_eval.py                              │
│                                                             │
│  Fast mode (no API keys needed):                           │
│  Tests regex pre-screen + intent classification only       │
│                                                             │
│  Full mode:                                                │
│  $ python scripts/run_eval.py --full                       │
│                                                             │
│  [🔄 Refresh]                                              │
└─────────────────────────────────────────────────────────────┘
```

### Metric cards
Each card: white background, `1px solid #E5E0D8` border, 12px border radius, 16px padding.  
Label: muted 12px. Value: navy 28px bold. Pass rate shows green if ≥ 80%, amber 60–79%, red < 60%.

### Category progress bars
Progress bar fill: navy `#1B4F72`. Background track: `#E5E0D8`. Height 8px, rounded.

### Results table
Columns: ID, Category (badge), Input (truncated 60 chars), Passed (✓ green / ✗ red), Intent (badge), Details (expandable).  
Sortable columns. Filter by category. Search by input text.  
Row click → expand to show full input, expected vs actual intent, any missing keywords.

---

## 8. Modals & Overlays

### Clear Session Confirmation
```
┌─────────────────────────────────────┐
│  Clear session?                     │
│                                     │
│  This will delete all conversation  │
│  history and cannot be undone.      │
│                                     │
│  [Cancel]      [Clear Session]      │
│                     (red button)    │
└─────────────────────────────────────┘
```
Centered modal, backdrop blur `rgba(0,0,0,0.4)`. Cancel = outline, Clear = filled red.

### Citation Tooltip
Hovering a scripture chip (e.g. "John 3:16 KJV") shows a tooltip with the full verse text:
```
┌─────────────────────────────────────────────────────────┐
│ John 3:16 (KJV)                                    ✓   │
│ "For God so loved the world, that he gave his          │
│  only begotten Son..."                                 │
└─────────────────────────────────────────────────────────┘
```
Max-width 320px. Arrow pointing to chip. Appears on hover after 300ms delay.

---

## 9. States & Edge Cases

### Connection error
```
┌─────────────────────────────────────────────────────────┐
│ ⚠  Cannot reach API                                    │
│ Make sure the backend is running:                      │
│ $ uvicorn app.main:app --reload                        │
│                                    [Retry]             │
└─────────────────────────────────────────────────────────┘
```
Red border, error icon. Retry button re-sends last message.

### Empty chat state
Centered welcome:
```
           ✝

   Christianity AI Assistant
   Scripture-grounded · Denomination-aware

   [John 3:16]  [Trinity]  [Nativity art]  [Sermon on Mount]
```
Cross icon in gold. Subtitle muted. 4 suggestion chips below.

### Long response
If response > 800 chars: show first 400 chars + "Read more" expand link. Full text visible after expand.

### Rate limit / 429 error
```
The AI service is busy. Please wait a moment and try again.   [Retry in 15s]
```
Countdown timer on retry button.

---

## 10. Responsive Breakpoints

| Breakpoint | Layout change |
|-----------|---------------|
| ≥ 1200px | Full sidebar + main, all columns visible |
| 768–1199px | Sidebar collapses to icon rail (48px wide) |
| < 768px | Sidebar hidden (hamburger), tab bar → bottom nav |

Mobile chat: full-width bubbles (90%), input bar full bottom width, font size 14px.

---

## 11. Accessibility

- All interactive elements: `aria-label` attributes
- Color contrast: minimum 4.5:1 for body text (WCAG AA)
- Focus rings: `2px solid #D4A017` gold on all focusable elements
- Scripture text: `lang="en"` on all text blocks (Bible in English)
- Images: `alt` text = the rewritten prompt used for generation
- Keyboard nav: Tab order sidebar → tabs → chat input → send button
- Screen reader: intent badge announced as "Response type: scripture question"

---

## 12. Tech Stack Recommendation

| Concern | Recommendation |
|---------|---------------|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS + shadcn/ui components |
| Icons | Lucide React |
| Fonts | Google Fonts: Playfair Display + Inter |
| State | Zustand (session, messages) |
| API client | TanStack Query (react-query) for loading states |
| Markdown | react-markdown (for scripture formatting) |
| Images | Next.js `<Image>` with base64 src for generated images |
| Animations | Framer Motion (subtle, minimal) |

---

## 13. API Integration Notes

### Session ID management
Generate UUID on app load, persist in `localStorage`. On tab close / clear → reset.

### Polling pattern (not needed)
API is synchronous — one POST returns one response. No streaming/SSE needed unless added to backend.

### Denomination in message
If user explicitly selects denomination (not auto-detect):
```js
const message = denomination !== 'auto-detect'
  ? `[Denomination preference: ${denomination}] ${userInput}`
  : userInput
```

### Image display
Response `image_b64` is a base64-encoded PNG. Display as:
```jsx
<img src={`data:image/png;base64,${image_b64}`} alt={promptText} />
```

### Error handling
- Network error → show "Cannot reach API" banner
- 500 from API → show `detail` field from error JSON
- `toxicity_ok: false` in response → show response in amber refusal style even if it's text

---

## 14. Component Checklist for Claude Design

When generating UI components, create these in order:

- [ ] `AppShell` — sidebar + main area layout
- [ ] `Sidebar` — logo, denomination select, session info, clear button
- [ ] `TabBar` — 3 tabs with active state
- [ ] `ChatWindow` — scrollable message list
- [ ] `MessageBubble` — user variant + assistant variant
- [ ] `IntentBadge` — colored pill for each intent type
- [ ] `CitationChip` — scripture reference with verified/unverified state
- [ ] `TypingIndicator` — 3-dot pulse animation
- [ ] `ChatInput` — textarea + send button + char counter
- [ ] `SuggestionChips` — empty state prompt chips
- [ ] `ImageGenTab` — prompt input + generate button + result display
- [ ] `EvalDashboard` — metric cards + category bars + results table
- [ ] `ConfirmModal` — clear session confirmation
- [ ] `CitationTooltip` — hover tooltip with verse text
- [ ] `RefusalCard` — amber-tinted safety message display
- [ ] `ConnectionError` — API unreachable banner
