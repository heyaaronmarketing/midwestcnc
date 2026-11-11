#!/usr/bin/env python3
"""
Insights weekly auto-draft orchestrator.

Picks the next scheduled article from src/data/insights-pillars.json,
calls the Anthropic API to draft it, runs it through the 11 quality
gates with up to 3 retry attempts, promotes on pass, regenerates pages,
commits to a feature branch, and pushes to origin.

Mirrors the steps in prompts/insights/07-auto-draft-runbook.md.

Designed for GitHub Actions (weekly cron) and runnable locally:

    ANTHROPIC_API_KEY=sk-... python3 scripts/insights_auto_draft.py

Environment:
    ANTHROPIC_API_KEY   — required, your Anthropic API key
    ANTHROPIC_MODEL     — optional, defaults to claude-opus-4-5
    AUTO_DRAFT_SLUG     — optional, force a specific slug instead of
                          picking from the schedule
    AUTO_DRAFT_DRY_RUN  — optional, "1" to skip git push at the end

Exit codes:
    0  success (article pushed, or nothing to draft)
    1  validation failed after MAX_RETRIES — review file saved
    2  pre-flight or environment failure (no recovery possible)
    3  API call failed
    4  git operation failed
"""

from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# ---------- Paths ----------

REPO = Path(__file__).resolve().parent.parent
PILLAR_DATA = REPO / "src" / "data" / "insights-pillars.json"
PUBLISHED_DIR = REPO / "src" / "content" / "insights"
DRAFTS_DIR = REPO / "src" / "content" / "insights" / "_drafts"
SHARED_CONTEXT = REPO / "prompts" / "insights" / "00-shared-context.md"

# ---------- Tuning ----------

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5")
MAX_TOKENS = 8000
MAX_RETRIES = 3
DAYS_HORIZON = 21  # widen from 14 so the workflow has flex if a week is skipped


# ---------- I/O helpers ----------

def info(msg: str) -> None:
    print(f"→ {msg}", flush=True)


def ok(msg: str) -> None:
    print(f"✓ {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"!  {msg}", flush=True)


def fail(msg: str, exit_code: int = 2) -> None:
    print(f"\n✗ {msg}", flush=True)
    sys.exit(exit_code)


def run(cmd: list, cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """Run a shell command, return (rc, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or REPO,
    )
    return result.returncode, result.stdout, result.stderr


# ---------- Pre-flight ----------

def preflight() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        fail("ANTHROPIC_API_KEY not set in environment.")

    for required in [
        REPO / "scripts" / "insights_schedule.py",
        REPO / "scripts" / "insights_link_suggester.py",
        REPO / "scripts" / "insights_validators.py",
        REPO / "scripts" / "generate_insights_pages.py",
        REPO / "scripts" / "generate_site_shell.py",
        REPO / "scripts" / "launch_audit.py",
        PILLAR_DATA,
        SHARED_CONTEXT,
    ]:
        if not required.exists():
            fail(f"Required file missing: {required.relative_to(REPO)}")

    # Don't enforce git-clean in CI — the workflow checks out a fresh
    # tree. Locally, the user is responsible for a clean state.
    if not os.environ.get("GITHUB_ACTIONS"):
        rc, out, _ = run(["git", "status", "--porcelain"])
        if rc != 0:
            fail("git status failed; cannot verify repo state.")
        if out.strip():
            fail("Working tree is dirty. Commit or stash before running.")

    ok("Pre-flight checks passed.")


# ---------- Article selection ----------

def is_published(pillar_slug: str, cluster_slug: str) -> bool:
    return (PUBLISHED_DIR / pillar_slug / f"{cluster_slug}.md").exists()


def is_drafted(cluster_slug: str) -> bool:
    return (DRAFTS_DIR / f"{cluster_slug}.md").exists()


def remote_branch_exists(slug: str) -> bool:
    rc, out, _ = run(["git", "ls-remote", "--heads", "origin", f"auto-draft/{slug}"])
    return rc == 0 and out.strip() != ""


def pick_next_article() -> Optional[dict]:
    """Return the next article to draft, or None if nothing to do."""
    forced = os.environ.get("AUTO_DRAFT_SLUG")
    data = json.loads(PILLAR_DATA.read_text(encoding="utf-8"))

    candidates = []
    for p in data["pillars"]:
        for c in p["clusters"]:
            candidate = dict(c)
            candidate["_pillar_slug"] = p["slug"]
            candidate["_pillar_title"] = p["title"]
            candidate["_pillar_summary"] = p.get("summary", "")
            candidate["_consolidates_signal_for"] = p.get("consolidates_signal_for", "")
            candidates.append(candidate)

    if forced:
        for c in candidates:
            if c["slug"] == forced:
                info(f"Forced slug via AUTO_DRAFT_SLUG: {forced}")
                if is_published(c["_pillar_slug"], c["slug"]):
                    fail(f"Forced slug {forced} is already published.", 2)
                return c
        fail(f"Forced slug {forced} not found in pillar data.", 2)

    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=DAYS_HORIZON)

    # Earliest target_publish_date in the horizon, not published, not
    # drafted, no remote branch.
    candidates_with_date = []
    for c in candidates:
        d = c.get("target_publish_date")
        if not d:
            continue
        try:
            dt = datetime.date.fromisoformat(d)
        except ValueError:
            continue
        if dt > horizon:
            continue
        if is_published(c["_pillar_slug"], c["slug"]):
            continue
        if is_drafted(c["slug"]):
            continue
        if remote_branch_exists(c["slug"]):
            continue
        candidates_with_date.append((dt, c))

    if not candidates_with_date:
        return None

    candidates_with_date.sort(key=lambda t: t[0])
    return candidates_with_date[0][1]


# ---------- Link suggester ----------

# Evergreen hub URLs — always valid to link to from any article.
# Padded into the suggestion list when the semantic suggester returns
# fewer than 8 (guarantees Opus has ≥5 real targets to weave in).
_EVERGREEN_HUB_LINKS = [
    {"url": "/repairs/",          "suggested_anchor": "CNC machine repair"},
    {"url": "/spindle-grinding/", "suggested_anchor": "spindle rebuild and grinding"},
    {"url": "/way-covers/",       "suggested_anchor": "replacement way covers"},
    {"url": "/service-area/",     "suggested_anchor": "our 7-state service area"},
    {"url": "/insights/",         "suggested_anchor": "technical insights"},
    {"url": "/get-a-quote/",      "suggested_anchor": "request a quote"},
    {"url": "/about/",            "suggested_anchor": "about Midwest CNC"},
]


def get_link_suggestions(query: str) -> list:
    rc, out, err = run([
        "python3", "scripts/insights_link_suggester.py",
        "--query", query,
        "--top-k", "8",
        "--json",
    ])
    if rc != 0:
        fail(f"link suggester failed:\n{err}")
    try:
        links = json.loads(out)
    except json.JSONDecodeError:
        fail(f"link suggester returned non-JSON:\n{out}")

    # Always pad with evergreen hub URLs so the article has ≥8 options
    # even for topics where the semantic suggester finds nothing close.
    # De-dupe by URL to avoid repeats when the suggester already picked a hub.
    seen = {L["url"] for L in links}
    for hub in _EVERGREEN_HUB_LINKS:
        if hub["url"] not in seen:
            links.append(hub)
            seen.add(hub["url"])
        if len(links) >= 10:
            break
    return links


# ---------- Prompt construction ----------

def build_system_prompt() -> str:
    shared = SHARED_CONTEXT.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    return f"""You are drafting a long-form technical article for Midwest CNC
Services' Insights publishing engine. Your output will be saved as a
markdown file and run through 11 automated quality gates. Articles that
fail the gates will be rewritten, costing time and tokens — so think
carefully and produce a complete, gate-passing first draft.

{shared}

---

# OUTPUT FORMAT (strict)

Your response must be a complete markdown article with frontmatter, ready
to save directly as a .md file. No preamble, no explanation, no "Here is
your article" — just the markdown.

The frontmatter block must include exactly these keys:

```yaml
---
title: "<final article title>"
slug: "<provided in user message>"
pillar: "<provided in user message>"
target_query: "<provided in user message>"
description: "<145-160 char meta description that includes the target query>"
author: "Ken — Midwest CNC Services"
date: "{today}"
signal_signature: "<phrase1; phrase2; phrase3; phrase4; phrase5>"
---
```

The body must follow this structure:

1. `## Key Takeaways` — exactly 3-5 bullet points. Each bullet a complete
   sentence ending in a period. Each containing at least one specific
   number or named entity.

2. A lede paragraph after Key Takeaways. 4 sentences maximum. First 300
   words of the article (Key Takeaways + lede combined) must contain at
   least one specific number AND at least 2 named entities (brand
   names, model numbers, places, control systems).

3. 4-6 content `## H2` sections. Each H2's first sentence must be
   declarative-definitional. NEVER a question. NEVER opening with
   "Have you", "Imagine", "Picture", "Let's", "Ever", or "Do you".

4. `## Sources & references` H2 — short list of what backs the article.

5. `## When to bring this work to us` (or similar closing H2) — short
   scenario-naming paragraph plus a CTA sentence linking to `/get-a-quote/`.

# HARD REQUIREMENTS THAT FAIL THE GATES

- Length: cluster articles 1200-2000 words (the user message specifies
  target_words for this article). Below 1200 fails.
- Flesch reading ease ≥ 60. Use short sentences. Avoid compound-complex
  constructions. Plain English over jargon where possible.
- Zero exclamation points anywhere.
- Zero hype words: premier, world-class, best-in-class, leading,
  unparalleled, cutting-edge, unmatched.
- Zero claim-audit ban-list phrases: photo-verified, factory-trained,
  factory-certified, 24/7, ISO 9001, ISO certif*, flat-rate, transparent
  pricing, guaranteed, warranty, same-day.
- 5+ in-body links from the provided suggestions, woven into prose as
  contextual anchors (not a "Related Posts" footer).
- The 5 phrases in signal_signature MUST appear LITERALLY in the body
  text. Pick phrases you can actually embed naturally.
- No placeholders. No [TODO], [FIXME], [Ken to fill], <placeholder>. The
  article must read complete on first draft.

# HEDGING (acceptable)

Specific claims must be falsifiable. Use these hedge patterns when you
don't have a hard number:
- "we have seen", "we typically see"
- "in the range of $X to $Y"
- "usually", "most often", "in our service log"
- "varies by platform"

# VOICE

Read like Ken (shop owner, 30+ years) writing for another shop owner.
Measured. Plain. Technical when it matters. No selling. No hype.
Numbered/named specifics over abstractions."""


def build_user_prompt(article: dict, links: list, attempt: int,
                      previous_draft: Optional[str], gate_failures: Optional[list]) -> str:
    lines = []
    lines.append("# Article to draft\n")
    lines.append(f"- **Slug:** `{article['slug']}`")
    lines.append(f"- **Title:** {article['title']}")
    lines.append(f"- **Pillar:** `{article['_pillar_slug']}` — {article['_pillar_title']}")
    lines.append(f"- **Target query:** `{article['target_query']}`")
    lines.append(f"- **Intent:** {article.get('intent', 'informational')}")
    lines.append(f"- **Target words:** {article.get('target_words', 1500)} (floor 1200, hard ceiling 2000)")
    lines.append("")
    lines.append("## Pillar context")
    lines.append(article["_pillar_summary"])
    lines.append("")
    lines.append("## Required proprietary signal")
    lines.append("The cluster spec requires this proprietary signal in-body. Embed each piece naturally:")
    for s in article.get("signal", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append("Pick 5+ short phrases from your draft that capture this signal and list them in `signal_signature`. The validator will check that each phrase appears literally in the body.")
    lines.append("")
    lines.append("## Internal-link targets (weave 5+ as in-context anchors)")
    for link in links[:8]:
        lines.append(f"- `{link['url']}` — suggested anchor: \"{link['suggested_anchor']}\"")
    lines.append("")

    consol = article.get("_consolidates_signal_for", "")
    if consol:
        lines.append(f"This pillar reinforces the service page at `{consol}`. Linking to it in the closing section is appropriate.")
        lines.append("")

    if attempt > 1 and gate_failures:
        lines.append(f"## Retry attempt {attempt} of {MAX_RETRIES}")
        lines.append("")
        lines.append("Your previous attempt failed these specific gates:")
        for f in gate_failures:
            lines.append(f"- {f}")
        lines.append("")

        # Detect internal_links failure — the most common gate failure and
        # the one Opus consistently under-addresses with the generic hint.
        # Give an explicit markdown-link example + require literal format.
        if any("internal_links" in str(f) for f in gate_failures):
            lines.append("### ⚠ CRITICAL: internal_links gate failed")
            lines.append("")
            lines.append("The validator requires **AT LEAST 5 in-body markdown links** to other pages on this site. "
                        "Your previous draft did not include them.")
            lines.append("")
            lines.append("**Mandatory format** — each link must be a full markdown link syntax woven into a sentence:")
            lines.append("")
            lines.append("    ... for context on rebuild timelines, see our [spindle grinding hub](/spindle-grinding/). ...")
            lines.append("    ... teardown costs are documented on the [machine repair hub](/repairs/). ...")
            lines.append("")
            lines.append("**Minimum requirements for this rewrite:**")
            lines.append(f"1. At least 5 links from the \"Internal-link targets\" list above.")
            lines.append("2. Each link appears as a FULL markdown anchor: `[anchor text](url)` — NOT as a bare URL, NOT as a \"Related Posts\" footer.")
            lines.append("3. Links are woven into body prose, one per H2 section where contextually natural.")
            lines.append("4. The evergreen hub URLs (/repairs/, /spindle-grinding/, /way-covers/) are always safe to link to — use them if the semantic suggestions don't fit.")
            lines.append("")
            lines.append("If you cannot naturally weave 5 links into the current article structure, "
                        "restructure the article — add a sentence per H2 that references a related page. "
                        "This is non-negotiable. Draft WILL fail validation without it.")
            lines.append("")

        # ban_list specific CRITICAL block — Opus sometimes reaches for
        # these words when searching for differentiation. Make it explicit.
        if any("ban_list" in str(f) for f in gate_failures):
            lines.append("### ⚠ CRITICAL: ban_list gate failed")
            lines.append("")
            lines.append("Your previous draft contained one or more of these BANNED phrases. They are not "
                        "allowed anywhere in the article — not even in quoted material, examples, or hedges:")
            lines.append("")
            lines.append("- `warranty` / `warranties` (we don't offer warranty — don't reference the concept)")
            lines.append("- `guaranteed` / `guarantee`")
            lines.append("- `same-day`")
            lines.append("- `24/7`")
            lines.append("- `ISO 9001`, `ISO certif*`")
            lines.append("- `flat-rate`, `transparent pricing`")
            lines.append("- `photo-verified`, `factory-trained`, `factory-certified`")
            lines.append("")
            lines.append("If you need to talk about warranties or guarantees, REWORD. Examples:")
            lines.append("- 'warranty' → 'return period' or 'the manufacturer's coverage window'")
            lines.append("- 'guaranteed' → 'reliably' or 'consistently' (or just delete the hedge)")
            lines.append("- 'same-day' → 'within the day' or 'on the day of the call'")
            lines.append("")
            lines.append("Grep your draft for each banned phrase before submitting. Draft WILL fail validation if ANY appear.")
            lines.append("")

        # cosine_similarity specific CRITICAL block — most common structural
        # failure mode when the cluster topic overlaps with an existing page.
        if any("cosine_similarity" in str(f) for f in gate_failures):
            lines.append("### ⚠ CRITICAL: cosine_similarity gate failed")
            lines.append("")
            lines.append("Your previous draft shares too much vocabulary with an existing published page "
                        "(similarity ≥ 0.30). Rewrite to differentiate — pick a NARROWER angle this article "
                        "owns that the existing page does NOT cover.")
            lines.append("")
            lines.append("**Strategies that actually move the cosine score:**")
            lines.append("1. **Narrow the scope.** Instead of 'Used Doosan Buying Guide', focus on "
                        "'Rebadged Daewoo Controls on Pre-2012 Doosan Machines' — a sub-topic the existing "
                        "page doesn't go into.")
            lines.append("2. **Change the perspective.** If the existing page is 'what we do,' make this "
                        "'how you evaluate before you buy' — different buyer intent, different vocabulary.")
            lines.append("3. **Introduce entities the existing page lacks.** Specific model names, "
                        "serial-number ranges, control-generation cutoff years. Those words don't appear in "
                        "the existing page, so they LOWER the cosine score.")
            lines.append("4. **Drop generic vocabulary.** Words like 'quality', 'service', 'repair' appear "
                        "everywhere; swap for specific technical terms.")
            lines.append("")
            lines.append("If no narrower angle exists that genuinely differentiates from the existing page, "
                        "write the best differentiated version you can — the orchestrator will promote the "
                        "latest attempt if the next rewrite reduces cosine below 0.30.")
            lines.append("")

        lines.append("Rewrite the entire article addressing these issues. Common fixes:")
        lines.append("- **flesch** → shorter sentences, fewer compound clauses, plainer words")
        lines.append("- **cosine_similarity** → reduce vocabulary overlap with existing pages; differentiate by focusing on the unique angle this article addresses")
        lines.append("- **definitional_h2** → rewrite the flagged H2's first sentence as a declarative statement")
        lines.append("- **proprietary_signal** → either add the declared signal_signature phrases verbatim, OR update signal_signature to phrases that ARE in the body (keeping them specific and falsifiable)")
        lines.append("- **internal_links** → see CRITICAL section above")
        lines.append("- **first_300_words** → add specific numbers and named entities to the lede")
        lines.append("- **ban_list** / **hype_words** / **exclamations** → remove the offending phrases")
        lines.append("")
        lines.append("Below is your previous draft for reference:")
        lines.append("")
        lines.append("```markdown")
        lines.append(previous_draft or "")
        lines.append("```")
    else:
        lines.append("## Output")
        lines.append("Produce the complete markdown article now. No preamble. Start with the `---` of the frontmatter and end with the CTA sentence.")

    return "\n".join(lines)


# ---------- Anthropic API ----------

def call_claude(system: str, user: str) -> str:
    try:
        from anthropic import Anthropic
    except ImportError:
        fail("anthropic SDK not installed. Run: pip install anthropic", 3)

    client = Anthropic()
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as e:
        fail(f"Anthropic API call failed: {e}", 3)

    # Extract text content from the response
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "".join(parts)


def extract_markdown(response_text: str) -> str:
    """Strip preamble/postamble and return just the markdown article."""
    text = response_text.strip()
    # Find the first frontmatter '---' line
    m = re.search(r"^---\s*$", text, re.MULTILINE)
    if not m:
        return text
    return text[m.start():]


# ---------- Validation ----------

def validate(draft_path: Path) -> tuple[bool, str, list]:
    rc, out, _ = run([
        "python3", "scripts/insights_validators.py", str(draft_path),
    ])
    failures = []
    for line in out.splitlines():
        if "[✗]" in line:
            failures.append(line.strip())
    return rc == 0, out, failures


def save_review_log(slug: str, failures: list, last_draft: str) -> Path:
    review = DRAFTS_DIR / f"{slug}.review.md"
    review.write_text(
        f"# Auto-draft validation failure\n\n"
        f"Attempts: {MAX_RETRIES}\n"
        f"Model: {MODEL}\n"
        f"Date: {datetime.datetime.now().isoformat()}\n\n"
        f"## Last attempt's failed gates\n\n"
        + "\n".join(f"- {f}" for f in failures)
        + "\n\n## Last draft\n\n"
        + "```markdown\n"
        + last_draft
        + "\n```\n",
        encoding="utf-8",
    )
    return review


# ---------- Promote, regen, audit, commit, push ----------

def promote(draft_path: Path) -> None:
    rc, out, err = run([
        "python3", "scripts/insights_validators.py",
        "--promote", str(draft_path),
    ])
    if rc != 0:
        fail(f"promote failed:\n{out}\n{err}")
    ok("Draft promoted.")


def regenerate() -> None:
    for label, cmd in [
        ("insights pages", ["python3", "scripts/generate_insights_pages.py"]),
        ("schedule report", ["python3", "scripts/insights_schedule.py", "report"]),
        ("site shell + sitemap + llms.txt", ["python3", "scripts/generate_site_shell.py"]),
    ]:
        rc, _, err = run(cmd)
        if rc != 0:
            fail(f"regen failed at {label}:\n{err}")
        ok(f"Regenerated: {label}")


def audit() -> str:
    rc, out, _ = run(["python3", "scripts/launch_audit.py"])
    # Check broken links specifically — the only blocker we treat as fatal
    for line in out.splitlines():
        if "Broken links:" in line:
            try:
                count = int(line.split(":")[1].strip())
            except (IndexError, ValueError):
                continue
            if count > 0:
                fail(f"broken links regression detected: {count}\n\n{out}")
    ok("Audit passed (no new broken links).")
    return out


def git_commit_push(article: dict) -> tuple[str, bool]:
    """Create the auto-draft branch, commit, push. Returns (branch, pushed)."""
    branch = f"auto-draft/{article['slug']}"
    slug = article["slug"]
    title = article["title"]

    # Git identity (only set in CI or if not configured)
    if os.environ.get("GITHUB_ACTIONS"):
        run(["git", "config", "user.name", "Insights Auto-Draft Bot"])
        run(["git", "config", "user.email",
             "insights-bot@midwestcncservices.com"])

    rc, _, err = run(["git", "checkout", "-b", branch])
    if rc != 0:
        fail(f"branch create failed: {err}", 4)

    run(["git", "add", "-A"])

    commit_body = f"""Auto-drafted: {title}

Generated by scripts/insights_auto_draft.py (weekly GitHub Actions
auto-draft). Pillar: {article['_pillar_slug']}. Slug: {slug}.

This is a v1 draft using publicly defensible facts and hedged ranges.
A v2 edit pass with Ken's specific shop data (real pricing, named
customer scenarios, bench photos) will deepen the piece.

All 11 quality gates passed. Open the PR and apply the 60-second human
review checklist before merging.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"""
    rc, _, err = run(["git", "commit", "-m", commit_body])
    if rc != 0:
        fail(f"git commit failed: {err}", 4)

    if os.environ.get("AUTO_DRAFT_DRY_RUN") == "1":
        warn("AUTO_DRAFT_DRY_RUN=1 — skipping push.")
        return branch, False

    rc, _, err = run(["git", "push", "-u", "origin", branch])
    if rc != 0:
        fail(f"git push failed:\n{err}", 4)

    ok(f"Pushed branch: {branch}")
    return branch, True


# ---------- Final report ----------

def report(article: dict, branch: str, pushed: bool, gate_summary: str) -> None:
    print()
    print("=" * 60)
    print(" Auto-draft complete")
    print("=" * 60)
    print(f"  Article:  {article['title']}")
    print(f"  Slug:     {article['slug']}")
    print(f"  Pillar:   {article['_pillar_slug']}")
    print(f"  Branch:   {branch}")
    if pushed:
        print(f"  PR URL:   https://github.com/aaronconsent/midwestcnc/pull/new/{branch}")
    else:
        print(f"  PR URL:   (dry run — branch not pushed)")
    print()
    print(" Gate summary")
    print("-" * 60)
    for line in gate_summary.splitlines():
        if line.startswith("  ["):
            print(" " + line)
    print()
    print(" What's still ahead")
    print("-" * 60)
    print("  - 60-second human-gate review (read the draft, check voice,")
    print("    verify all numerical claims are defensible)")
    print("  - Merge the PR — Cloudflare Pages deploys within ~2 min")
    print("  - Optional v2 edit pass with Ken's actual proprietary signal")
    print()


# ---------- Main ----------

def main() -> int:
    info("Pre-flight")
    preflight()

    info("Selecting next article")
    article = pick_next_article()
    if not article:
        ok("Nothing to draft in the next 14 days. Exiting.")
        return 0
    info(f"  → {article['slug']}: {article['title']}")
    info(f"     pillar={article['_pillar_slug']}, target_query='{article['target_query']}'")

    info("Gathering internal-link targets")
    links = get_link_suggestions(f"{article['title']} {article['target_query']}")
    info(f"  → {len(links)} suggestions")

    system_prompt = build_system_prompt()
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    draft_path = DRAFTS_DIR / f"{article['slug']}.md"

    previous_draft: Optional[str] = None
    gate_failures: Optional[list] = None
    last_validator_output = ""

    for attempt in range(1, MAX_RETRIES + 1):
        info(f"Drafting attempt {attempt}/{MAX_RETRIES} (model: {MODEL})")
        user_prompt = build_user_prompt(article, links, attempt,
                                        previous_draft, gate_failures)
        response_text = call_claude(system_prompt, user_prompt)
        markdown = extract_markdown(response_text)

        draft_path.write_text(markdown, encoding="utf-8")
        ok(f"Saved attempt {attempt} to {draft_path.relative_to(REPO)}")

        info(f"Validating attempt {attempt}")
        passed, val_out, failures = validate(draft_path)
        last_validator_output = val_out
        print(val_out)

        if passed:
            ok(f"All 11 gates passed on attempt {attempt}.")
            break

        previous_draft = markdown
        gate_failures = failures

        if attempt == MAX_RETRIES:
            review_path = save_review_log(article["slug"], failures, markdown)
            fail(f"All {MAX_RETRIES} attempts failed validation. "
                 f"Review log saved to {review_path.relative_to(REPO)}.", 1)

    info("Promoting draft")
    promote(draft_path)

    info("Regenerating pages, schedule, site shell")
    regenerate()

    info("Running audit")
    audit()

    info("Branch + commit + push")
    branch, pushed = git_commit_push(article)

    report(article, branch, pushed, last_validator_output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
