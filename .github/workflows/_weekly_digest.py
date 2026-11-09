#!/usr/bin/env python3
"""
Weekly Insights Digest — composes a Monday-morning email summarizing:
  - What shipped (merged auto-draft PRs) in the last 7 days
  - What's open for review
  - What's scheduled next (from src/data/insights-pillars.json)
  - Top-line SEO/AEO metrics (from the live /api/case-study.json)

Sends via Resend. Called by .github/workflows/weekly-digest.yml.
"""
from __future__ import annotations
import json, os, subprocess, sys, urllib.request
from datetime import datetime, timedelta, timezone


def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def gh_json(args: list[str]):
    try:
        return json.loads(sh(["gh"] + args))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def merged_last_week() -> list[dict]:
    """Shipped insight articles in the last 7 days — detected via commits
    whose subject starts with 'Auto-drafted:' since that's the PR title
    convention used by the squash-merge bot."""
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    log = sh([
        "git", "log", f"--since={since}", "--format=%cI|%s", "main",
    ])
    rows = []
    for line in log.splitlines():
        if "|" not in line: continue
        ts, msg = line.split("|", 1)
        if msg.startswith(("Auto-drafted:", "Insights:")) or "insights" in msg.lower():
            title = msg.replace("Auto-drafted:", "").replace("Insights:", "").strip()
            rows.append({"ts": ts[:10], "title": title[:100]})
    return rows


def open_prs() -> list[dict]:
    """Open PRs on heyaaronmarketing/midwestcnc with the insights label."""
    data = gh_json([
        "pr", "list", "--state", "open",
        "--repo", "heyaaronmarketing/midwestcnc",
        "--label", "insights-auto-draft",
        "--json", "number,title,url,createdAt,headRefName",
        "--limit", "50",
    ])
    return data or []


def upcoming_from_schedule(limit: int = 6) -> list[dict]:
    """Next N clusters from src/data/insights-pillars.json where
    scheduled_publish_date is in the future and still unpublished."""
    path = "src/data/insights-pillars.json"
    if not os.path.exists(path):
        return []
    data = json.load(open(path))
    pillars = data.get("pillars", []) if isinstance(data, dict) else data
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    upcoming = []
    for pillar in pillars:
        for cluster in pillar.get("clusters", []):
            if cluster.get("status") == "published": continue
            d = cluster.get("scheduled_publish_date") or cluster.get("target_publish_date")
            if not d or d < today: continue
            upcoming.append({
                "date": d,
                "pillar": pillar.get("title", pillar.get("slug", "")),
                "title": cluster.get("title", cluster.get("slug", "")),
            })
    upcoming.sort(key=lambda x: x["date"])
    return upcoming[:limit]


def case_study_metrics() -> dict:
    """Fetch the live JSON and distill the headline numbers."""
    try:
        req = urllib.request.Request(
            "https://midwestcncservices.com/api/case-study.json",
            headers={"User-Agent": "digest/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}
    g = data.get("google_search", {})
    a = data.get("ai_search", {})
    leads = data.get("leads", {})
    traffic = data.get("traffic_signals", {})
    return {
        "gsc_all_time_clicks": g.get("all_time", {}).get("clicks"),
        "gsc_all_time_impressions": g.get("all_time", {}).get("impressions"),
        "gsc_last_90d_clicks": g.get("last_90d", {}).get("clicks"),
        "gsc_delta_90d_pct": g.get("delta_90d", {}).get("clicks_pct"),
        "ai_all_time_citations": a.get("all_time", {}).get("total_citations"),
        "ai_last_30d": a.get("last_30d", {}).get("citations"),
        "ai_delta_30d_pct": a.get("delta_30d_pct"),
        "best_ai_day": a.get("best_day"),
        "lead_total": leads.get("total_submissions"),
        "lead_delivered": leads.get("emails_delivered"),
        "traffic_7d_bot_crawls": traffic.get("bot_crawls"),
        "traffic_by_bot": (traffic.get("by_bot") or [])[:5],
        "ai_referrals": traffic.get("ai_engine_referrals") or [],
    }


# ---------- Email composition ----------

def html_table(rows, columns):
    if not rows:
        return '<p style="color:#888;font-style:italic;">(nothing)</p>'
    head = "".join(f'<th style="text-align:left;padding:8px 12px;background:#f5f5f5;border-bottom:1px solid #ddd;">{c}</th>' for c in columns)
    body = ""
    for r in rows:
        cells = "".join(f'<td style="padding:8px 12px;border-bottom:1px solid #eee;vertical-align:top;">{v}</td>' for v in r)
        body += f"<tr>{cells}</tr>"
    return f'<table style="border-collapse:collapse;width:100%;font-family:system-ui,sans-serif;font-size:14px;"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def compose_email(shipped, open_list, upcoming, metrics):
    week_of = datetime.now(timezone.utc).strftime("%B %-d, %Y")
    html_parts = [
        '<div style="font-family:system-ui,-apple-system,sans-serif;max-width:720px;margin:0 auto;padding:24px;color:#1a1a1a;">',
        f'<h1 style="margin:0 0 8px;color:#b8341a;">Midwest CNC — Weekly Insights Digest</h1>',
        f'<p style="color:#666;margin:0 0 32px;">Week of {week_of}</p>',

        '<h2 style="color:#b8341a;border-bottom:2px solid #eee;padding-bottom:8px;">📊 This week\'s numbers</h2>',
    ]
    if "error" in metrics:
        html_parts.append(f'<p>Could not fetch metrics: {metrics["error"]}</p>')
    else:
        m = metrics
        bot_rows = [(b["bot"], f'{b["hits"]:,} hits') for b in m.get("traffic_by_bot", [])]
        html_parts.append(f'''
            <table style="border-collapse:collapse;width:100%;font-size:14px;font-family:system-ui;">
              <tr><td style="padding:6px 0;">Google clicks, last 90d</td><td style="padding:6px 0;text-align:right;font-variant-numeric:tabular-nums;"><strong>{m["gsc_last_90d_clicks"] or 0:,}</strong> ({m["gsc_delta_90d_pct"] or 0:+d}%)</td></tr>
              <tr><td style="padding:6px 0;">Google clicks, all-time</td><td style="padding:6px 0;text-align:right;font-variant-numeric:tabular-nums;"><strong>{m["gsc_all_time_clicks"] or 0:,}</strong></td></tr>
              <tr><td style="padding:6px 0;">AI citations, last 30d</td><td style="padding:6px 0;text-align:right;font-variant-numeric:tabular-nums;"><strong>{m["ai_last_30d"] or 0:,}</strong> ({m["ai_delta_30d_pct"] or 0:+d}%)</td></tr>
              <tr><td style="padding:6px 0;">AI citations, all-time</td><td style="padding:6px 0;text-align:right;font-variant-numeric:tabular-nums;"><strong>{m["ai_all_time_citations"] or 0:,}</strong></td></tr>
              <tr><td style="padding:6px 0;">AI/search bot crawls (last 7d)</td><td style="padding:6px 0;text-align:right;font-variant-numeric:tabular-nums;"><strong>{m["traffic_7d_bot_crawls"] or 0:,}</strong></td></tr>
              <tr><td style="padding:6px 0;">Leads (all-time)</td><td style="padding:6px 0;text-align:right;font-variant-numeric:tabular-nums;"><strong>{m["lead_total"] or 0:,}</strong> delivered: {m["lead_delivered"] or 0:,}</td></tr>
            </table>
        ''')
        if bot_rows:
            html_parts.append('<p style="margin-top:16px;"><strong>Top AI/search bot crawlers (last 7d):</strong></p>')
            html_parts.append(html_table(bot_rows, ["Bot", "Hits"]))

    html_parts.append('<h2 style="color:#b8341a;border-bottom:2px solid #eee;padding-bottom:8px;margin-top:32px;">✅ Shipped this week</h2>')
    html_parts.append(html_table(
        [(s["ts"], s["title"]) for s in shipped[:20]],
        ["Date", "Article"]
    ))
    html_parts.append(f'<p style="color:#666;font-size:13px;">{len(shipped)} total shipped in the last 7 days.</p>')

    html_parts.append('<h2 style="color:#b8341a;border-bottom:2px solid #eee;padding-bottom:8px;margin-top:32px;">👁️ Open for review</h2>')
    if open_list:
        rows = []
        for pr in open_list[:20]:
            created = pr["createdAt"][:10]
            rows.append((created, f'<a href="{pr["url"]}" style="color:#b8341a;">#{pr["number"]} — {pr["title"][:70]}</a>'))
        html_parts.append(html_table(rows, ["Opened", "PR"]))
        html_parts.append(f'<p style="color:#666;font-size:13px;">{len(open_list)} open auto-draft PR(s). Most are auto-merging on gates-pass; manual review only if you want to catch one before it ships.</p>')
    else:
        html_parts.append('<p style="color:#888;font-style:italic;">(none — auto-merge is caught up)</p>')

    html_parts.append('<h2 style="color:#b8341a;border-bottom:2px solid #eee;padding-bottom:8px;margin-top:32px;">📅 Scheduled next</h2>')
    if upcoming:
        html_parts.append(html_table(
            [(u["date"], u["pillar"], u["title"]) for u in upcoming],
            ["Target date", "Pillar", "Cluster"]
        ))
    else:
        html_parts.append('<p style="color:#888;font-style:italic;">No scheduled clusters found. The auto-draft queue may be exhausted — add more to <code>src/data/insights-pillars.json</code> or let the orchestrator pick opportunistically.</p>')

    html_parts.append(f'''
        <hr style="border:none;border-top:1px solid #eee;margin:40px 0 24px;">
        <p style="color:#888;font-size:13px;line-height:1.5;">
          This digest was assembled by the <code>weekly-digest</code> GitHub Actions workflow on
          midwestcnc. It pulls shipped articles from <code>git log</code>, open PRs from the GitHub API,
          scheduled clusters from <code>src/data/insights-pillars.json</code>, and live metrics from
          <code>https://midwestcncservices.com/api/case-study.json</code>.<br><br>
          Live admin dashboards: <a href="https://midwestcncservices.com/admin" style="color:#b8341a;">leads</a> ·
          <a href="https://midwestcncservices.com/admin/case-study" style="color:#b8341a;">case study</a> ·
          <a href="https://midwestcncservices.com/admin/traffic" style="color:#b8341a;">traffic</a>
        </p>
        </div>
    ''')
    return "".join(html_parts)


# ---------- Resend send ----------

def send(subject: str, html: str) -> None:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("No RESEND_API_KEY — printing instead")
        print(subject)
        print(html[:2000])
        return
    to_raw = os.environ.get("DIGEST_TO", "")
    to = [t.strip() for t in to_raw.split(",") if t.strip()]
    from_email = os.environ.get("DIGEST_FROM", "Midwest CNC Insights <insights@midwestcncservices.com>")

    payload = {"from": from_email, "to": to, "subject": subject, "html": html}
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read())
        print(f"✓ Sent: {res.get('id', 'ok')}  →  {', '.join(to)}")
    except urllib.error.HTTPError as e:
        print(f"✗ Resend {e.code}: {e.read().decode()[:400]}")
        sys.exit(1)


def main() -> int:
    shipped = merged_last_week()
    open_list = open_prs()
    upcoming = upcoming_from_schedule()
    metrics = case_study_metrics()
    html = compose_email(shipped, open_list, upcoming, metrics)
    week_of = datetime.now(timezone.utc).strftime("%b %-d")
    subject = f"Midwest CNC — Weekly Insights Digest · {week_of} · {len(shipped)} shipped, {len(open_list)} open"
    send(subject, html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
