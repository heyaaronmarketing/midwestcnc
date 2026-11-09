#!/usr/bin/env python3
"""
Send an insights-article review email to Muse (via Resend).

Called by .github/workflows/insights-auto-draft.yml right after a new
auto-draft PR is opened. Muse reads the email, reviews the article,
and signals approval by adding the 'muse-approved' label to the PR
on GitHub. The muse-approve.yml workflow then auto-merges.

Subject convention: '[REVIEW] Insights: {title}'
  — Muse filters her inbox on this exact prefix. Do not change the
    prefix without also updating her filter rules.

Env (all required):
  RESEND_API_KEY   — Resend API key (shared with quote form)
  REVIEW_TO        — Muse's inbox (default hello@aaron.chat)
  REVIEW_FROM      — verified Resend sender
  PR_URL           — the GitHub PR URL
  PR_NUMBER        — the PR number
  ARTICLE_SLUG     — slug portion of the article path
  ARTICLE_TITLE    — article title from frontmatter
  ARTICLE_PATH     — repo-relative path to the .md file
"""
from __future__ import annotations
import json, os, sys, urllib.request, html as _html


SUBJECT_PREFIX = "[REVIEW] Insights:"


def read_article(path: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_markdown)."""
    if not os.path.exists(path):
        return {}, f"(article file not found at {path})"
    raw = open(path).read()
    fm = {}
    body = raw
    if raw.startswith("---\n"):
        parts = raw.split("---\n", 2)
        if len(parts) >= 3:
            front = parts[1]
            body = parts[2]
            # Minimal YAML parse — just key: "value" pairs (good enough for this)
            for line in front.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
    return fm, body


def compose_html(title, slug, pr_url, pr_number, fm, body):
    pillar = fm.get("pillar", "?")
    target_q = fm.get("target_query", "")
    author = fm.get("author", "")
    word_count = len([w for w in body.split() if w])

    # Preserve paragraph breaks in HTML preview
    body_html_bits = []
    for para in body.strip().split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if para.startswith("## "):
            body_html_bits.append(f'<h2 style="color:#b8341a;margin:28px 0 8px;">{_html.escape(para[3:])}</h2>')
        elif para.startswith("### "):
            body_html_bits.append(f'<h3 style="margin:20px 0 6px;">{_html.escape(para[4:])}</h3>')
        elif para.startswith("- ") or para.startswith("* "):
            items = "".join(f'<li>{_html.escape(line[2:].strip())}</li>' for line in para.splitlines() if line.startswith(("- ", "* ")))
            body_html_bits.append(f'<ul>{items}</ul>')
        else:
            body_html_bits.append(f'<p style="margin:0 0 14px;">{_html.escape(para)}</p>')
    body_html = "\n".join(body_html_bits)

    return f"""<div style="font-family:system-ui,-apple-system,sans-serif;max-width:720px;margin:0 auto;padding:24px;color:#1a1a1a;line-height:1.55;">
  <h1 style="margin:0 0 4px;color:#b8341a;">New insights article for review</h1>
  <p style="color:#888;margin:0 0 24px;font-size:14px;">
    Midwest CNC Services auto-draft · passed all 12 quality gates · awaiting Muse approval
  </p>

  <table style="border-collapse:collapse;width:100%;font-size:14px;margin-bottom:24px;">
    <tr><td style="padding:4px 0;color:#666;width:120px;">Title</td><td style="padding:4px 0;font-weight:600;">{_html.escape(title)}</td></tr>
    <tr><td style="padding:4px 0;color:#666;">Pillar</td><td style="padding:4px 0;">{_html.escape(pillar)}</td></tr>
    <tr><td style="padding:4px 0;color:#666;">Slug</td><td style="padding:4px 0;"><code>{_html.escape(slug)}</code></td></tr>
    <tr><td style="padding:4px 0;color:#666;">Target query</td><td style="padding:4px 0;"><code>{_html.escape(target_q)}</code></td></tr>
    <tr><td style="padding:4px 0;color:#666;">Words</td><td style="padding:4px 0;">{word_count:,}</td></tr>
    <tr><td style="padding:4px 0;color:#666;">PR</td><td style="padding:4px 0;"><a href="{pr_url}" style="color:#b8341a;">#{pr_number} on GitHub</a></td></tr>
  </table>

  <div style="background:#f8f7f4;border-left:4px solid #b8341a;padding:16px 20px;border-radius:4px;margin-bottom:24px;">
    <p style="margin:0 0 8px;font-weight:700;">How to approve</p>
    <p style="margin:0;">
      Add the label <code>muse-approved</code> to the PR (link above) and the
      auto-merge workflow will squash + deploy within ~90 seconds.
    </p>
    <p style="margin:8px 0 0;">
      To request changes: open a PR review with change requests, or just
      reply here with the edits and I'll apply them.
    </p>
  </div>

  <h2 style="color:#b8341a;border-bottom:2px solid #eee;padding-bottom:8px;">Article content</h2>
  {body_html}

  <hr style="border:none;border-top:1px solid #eee;margin:32px 0 16px;">
  <p style="color:#888;font-size:12px;">
    Sent by the insights-auto-draft GitHub Actions workflow on
    heyaaronmarketing/midwestcnc. Author: {_html.escape(author)}.<br>
    Approval signal: label <code>muse-approved</code> on the PR triggers
    merge. See <code>.github/workflows/muse-approve.yml</code>.
  </p>
</div>"""


def send(subject: str, html: str, text_fallback: str):
    """POST through the Worker's /api/internal/send-email endpoint.
    The Worker owns the Resend API key; we never need it here. Auth is
    a shared bearer token (WORKER_REVIEW_SECRET on GH Actions side,
    REVIEW_WEBHOOK_SECRET on the Worker side)."""
    endpoint = os.environ.get(
        "EMAIL_ENDPOINT", "https://midwestcncservices.com/api/internal/send-email"
    )
    secret = os.environ.get("WORKER_REVIEW_SECRET")
    if not secret:
        print("✗ WORKER_REVIEW_SECRET not set — can't auth to the email relay")
        sys.exit(1)

    to_raw = os.environ.get("REVIEW_TO", "hello@aaron.chat")
    to = [t.strip() for t in to_raw.split(",") if t.strip()]
    from_email = os.environ.get("REVIEW_FROM",
                                "Midwest CNC Insights <insights@midwestcncservices.com>")

    payload = {
        "from": from_email,
        "to": to,
        "subject": subject,
        "html": html,
        "text": text_fallback,
        # Reply-To routes direct replies to Aaron so Muse's text-replies
        # aren't lost in the unmonitored insights@ box.
        "reply_to": "hello@aaron.chat",
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json",
            "User-Agent": "midwestcnc-insights-review/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read())
        print(f"✓ Sent email id={res.get('id')} to {', '.join(to)}")
        print(f"  Subject: {subject}")
    except urllib.error.HTTPError as e:
        print(f"✗ Worker email relay {e.code}: {e.read().decode()[:400]}")
        sys.exit(1)


def main() -> int:
    title = os.environ.get("ARTICLE_TITLE", "").removeprefix("Insights: ")
    slug = os.environ.get("ARTICLE_SLUG", "")
    path = os.environ.get("ARTICLE_PATH", "")
    pr_url = os.environ.get("PR_URL", "")
    pr_number = os.environ.get("PR_NUMBER", "")

    if not pr_url:
        print("No PR_URL provided — nothing to review")
        return 0

    fm, body = read_article(path)
    # Prefer frontmatter title if ARTICLE_TITLE is empty
    if not title:
        title = fm.get("title", slug)

    subject = f"{SUBJECT_PREFIX} {title}"
    html = compose_html(title, slug, pr_url, pr_number, fm, body)
    text_fallback = (
        f"{title}\n\nPR: {pr_url}\n\n"
        f"To approve: add label 'muse-approved' to the PR.\n\n"
        f"--- Article ---\n\n{body}"
    )
    send(subject, html, text_fallback)
    return 0


if __name__ == "__main__":
    sys.exit(main())
