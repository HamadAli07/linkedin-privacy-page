"""
Per-day post specs: each entry pairs the LinkedIn topic with language, filename hint, and angle.
The model writes an original fenced code block from this guidance (no catalog code pasted in).

Languages are limited to: javascript, typescript, html, css (fence tags must match).
"""

import random
from typing import Literal, TypedDict

AllowedLang = Literal["javascript", "typescript", "html", "css"]


class PostSpec(TypedDict):
    """One runnable idea for a post: topic + how the code block should support it."""

    topic: str
    language: AllowedLang
    title: str
    angle: str


def _spec(topic: str, language: AllowedLang, title: str, angle: str) -> PostSpec:
    return {"topic": topic, "language": language, "title": title, "angle": angle}


# One spec per former TOPIC_POOL line per day — topic and code guidance always match.
POST_SPECS_BY_DAY: dict[str, list[PostSpec]] = {
    "Monday": [
        _spec(
            "When to split a component vs. when composition is enough",
            "typescript",
            "composition-boundaries.tsx",
            "Show a small parent that composes children vs. extracting a file only when boundaries buy reuse or isolation.",
        ),
        _spec(
            "Design tokens vs. ad-hoc CSS: what actually scales in teams",
            "css",
            "semantic-tokens.css",
            "Use CSS custom properties for semantic roles (surface, text, border) teams can theme consistently.",
        ),
        _spec(
            "Props drilling, context, and state colocation — a practical tradeoff",
            "typescript",
            "colocated-widget-state.tsx",
            "Keep state in the subtree that mutates it; lift to context only when distant siblings need the same read.",
        ),
        _spec(
            "Building a component API that other teams can reuse safely",
            "typescript",
            "public-table-props.ts",
            "Narrow exported props plus optional render props or slots—not a growing bag of boolean flags.",
        ),
    ],
    "Tuesday": [
        _spec(
            "Why centralized API layers scale better in Next.js apps",
            "typescript",
            "api-client.ts",
            "One module for base URL, JSON headers, error mapping, and timeouts so routes and RSCs stay thin.",
        ),
        _spec(
            "Why most frontend teams overcomplicate state management",
            "typescript",
            "local-vs-store.tsx",
            "Prefer useState/useReducer until multiple distant trees need the same data—then justify a store slice.",
        ),
        _spec(
            "Server Components vs. client islands: where I draw the line",
            "typescript",
            "client-island.tsx",
            "Mark the smallest interactive leaf with 'use client'; keep data fetching in the server parent when possible.",
        ),
        _spec(
            "Caching and revalidation patterns that avoid stale UI",
            "typescript",
            "fetch-with-tags.ts",
            "Show cache tags, revalidatePath intent, or honest stale-while-revalidate UX—do not lie about freshness.",
        ),
    ],
    "Wednesday": [
        _spec(
            "Session handling and what must never live only in the browser",
            "typescript",
            "assert-session.ts",
            "Server-side session/JWT check before returning sensitive JSON—never trust client-only isLoggedIn flags.",
        ),
        _spec(
            "OAuth and callback UX: what breaks in real users' flows",
            "html",
            "oauth-callback-shell.html",
            "Minimal callback page: status region, no flash of wrong account, clear loading while tokens finalize.",
        ),
        _spec(
            "Handling API retries and optimistic UI without lying to the user",
            "typescript",
            "mutation-retry.ts",
            "Bounded retries with rollback or honest failed/retry UI—not silent permanent optimistic state.",
        ),
        _spec(
            "Form validation: client convenience vs. server authority",
            "typescript",
            "dual-validation-form.ts",
            "Client hints for UX; same rules on submit/server action—surface authoritative server errors in the UI.",
        ),
    ],
    "Thursday": [
        _spec(
            "Why premature optimization hurts — and what to measure instead",
            "javascript",
            "observe-vitals.js",
            "Read CLS/LCP (or a thin wrapper) toward analytics—optimize the slowest real URL, not toy micro-benchmarks.",
        ),
        _spec(
            "Lazy loading, code splitting, and real-world bundle budgets",
            "typescript",
            "lazy-routes.tsx",
            "React.lazy + Suspense for a heavy route; name or constant for a chunk size budget the team agrees on.",
        ),
        _spec(
            "Rendering lists and tables without jank at scale",
            "typescript",
            "memoized-row.tsx",
            "Stable row with memo/useMemo on expensive derived cells so parent updates do not repaint every row.",
        ),
        _spec(
            "CSS containment, layers, and paint cost on long feeds",
            "css",
            "feed-containment.css",
            "content-visibility or contain for long lists; focus-visible for keyboard users on feed cards.",
        ),
    ],
    "Friday": [
        _spec(
            "Why analytics should live next to feature code, not in a spreadsheet",
            "typescript",
            "feature-analytics.ts",
            "Typed event helper next to the onboarding/checkout feature—not a disconnected list of string event names.",
        ),
        _spec(
            "Feature flags and experiments owned by engineering",
            "typescript",
            "experiment-keys.ts",
            "const object for experiment keys plus deterministic bucketing—no magic strings in JSX conditionals.",
        ),
        _spec(
            "What frontend metrics actually predict retention",
            "typescript",
            "correlate-vitals.ts",
            "Shape of web-vital payload with session id for joining to retention (illustrative, not a full pipeline).",
        ),
        _spec(
            "Instrumenting UX: clicks, errors, and time-to-interactive",
            "typescript",
            "ui-telemetry.ts",
            "Meaningful UI errors (boundary/fetch) and one primary interaction latency—not every click as noise.",
        ),
    ],
    "Saturday": [
        _spec(
            "Using AI for UI scaffolding without shipping unmaintainable code",
            "typescript",
            "ai-scaffold-review.tsx",
            "Small component with explicit props interface plus comments listing what a human must verify before merge.",
        ),
        _spec(
            "Reviewing AI-generated components like junior PRs",
            "typescript",
            "pr-review-checklist.ts",
            "Exported checklist: keys in lists, effect deps, a11y roles—apply the same bar to AI-generated JSX.",
        ),
        _spec(
            "Automating repetitive UI checks in CI",
            "javascript",
            "ci-smoke.config.js",
            "Minimal Playwright-style smoke: one URL, viewport, one assertion—fast in CI.",
        ),
        _spec(
            "When copilot helps and when it hurts architecture",
            "typescript",
            "architecture-boundaries.ts",
            "Thin domain module importing only types from UI—dependency direction Copilot often inverts.",
        ),
    ],
    "Sunday": [
        _spec(
            "Keyboard navigation and focus management in complex UIs",
            "typescript",
            "focus-cycle.ts",
            "Tab cycle within a modal or menu: focusable query, wrap on Shift+Tab, preventDefault on the trap edge.",
        ),
        _spec(
            "Semantic HTML and ARIA: mistakes I see in production",
            "html",
            "landmarks-and-live.html",
            "main/nav regions plus aria-live polite for async status—not div-only page chrome.",
        ),
        _spec(
            "Responsive layouts without breakpoint soup",
            "css",
            "fluid-type-layout.css",
            "clamp() for type or gaps; grid minmax; fewer named breakpoints, more intrinsic sizing.",
        ),
        _spec(
            "Motion, prefers-reduced-motion, and respectful defaults",
            "css",
            "respect-motion.css",
            "@media (prefers-reduced-motion: reduce) shortening transitions; optional @layer for motion tokens.",
        ),
    ],
}


def select_post_spec(day: str) -> PostSpec:
    """Pick a random topic+guidance bundle for the weekday (falls back to Monday)."""
    pool = POST_SPECS_BY_DAY.get(day) or POST_SPECS_BY_DAY["Monday"]
    return random.choice(pool)
