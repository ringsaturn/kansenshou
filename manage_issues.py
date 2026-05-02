#!/usr/bin/env python3
"""
GitHub issue management for disease trend alerts.

Reads trend_alerts.json and creates/updates/closes GitHub issues via gh CLI.
Designed to be called from the trend-detection GitHub Actions workflow.
"""

import json
import subprocess
import sys
from pathlib import Path


LABEL = "trend-alert"
LABEL_COLOR = "d93f0b"  # red-orange


def gh(*args: str, capture: bool = True) -> subprocess.CompletedProcess:
    cmd = ["gh", *args]
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=False,
        encoding="utf-8",
    )


def ensure_label() -> None:
    """Create the trend-alert label if it doesn't exist."""
    result = gh("label", "list", "--json", "name", "--limit", "100")
    if result.returncode != 0:
        return
    labels = [l["name"] for l in json.loads(result.stdout or "[]")]
    if LABEL not in labels:
        gh("label", "create", LABEL, "--color", LABEL_COLOR,
           "--description", "Automated infectious disease trend alert",
           capture=False)
        print(f"Created label: {LABEL}")


def find_open_issue(title: str) -> int | None:
    """Search for an open issue with exactly this title and the trend-alert label."""
    result = gh(
        "issue", "list",
        "--label", LABEL,
        "--state", "open",
        "--json", "number,title",
        "--limit", "100",
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    issues = json.loads(result.stdout)
    for issue in issues:
        if issue["title"] == title:
            return int(issue["number"])
    return None


def find_open_issues_for_disease(disease: str) -> list[int]:
    """Find all open trend-alert issues that contain the disease name in the title."""
    result = gh(
        "issue", "list",
        "--label", LABEL,
        "--state", "open",
        "--json", "number,title",
        "--limit", "100",
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    issues = json.loads(result.stdout)
    return [int(i["number"]) for i in issues if disease in i["title"]]


def create_issue(alert: dict) -> None:
    disease = alert["disease"]
    dataset = alert["dataset"]
    title = alert["issue_title"]
    yr = alert["alert_start_year"]
    mo = alert["alert_start_month"]
    wk = alert["alert_start_week"]
    run_date = alert.get("run_date", "")
    cv = alert.get("current_value") or "N/A"
    bm = alert.get("baseline_med") or "N/A"
    z = alert.get("z_score") or "N/A"
    ratio = alert.get("ratio") or "N/A"
    chart = alert.get("mermaid_chart", "")

    body = f"""\
## 感染症トレンドアラート / Disease Trend Alert

**疾病 / Disease**: {disease}
**データセット / Dataset**: {dataset}
**アラート開始 / Alert started**: {yr}年{mo:02d}月 第{wk:02d}週
**初回検出日 / First detected**: {run_date}

### トレンド / Trend (bar = actual, line = seasonal baseline)

{chart}

### 検出指標 / Detection metrics

| 指標 | 値 |
|------|----|
| 現在値 / Current reports | {cv} |
| 季節性基準値 / Seasonal baseline | {bm} |
| Z スコア | {z} |
| 基準比 / Ratio vs baseline | {ratio}x |

### 解説 / Notes

{dataset} データに基づき、**{disease}** の報告数が季節的な基準値（過去同週の中央値）を\
有意に上回っています。

このIssueはデータ更新のたびに自動コメントで状況が更新されます。\
トレンドが通常レベルに戻ると自動的にクローズされます。

This issue is automatically updated each time new surveillance data is published.\
It will be closed automatically when the trend returns to baseline levels.

---
*自動生成 by [kansenshou](https://github.com/ringsaturn/kansenshou)*
"""

    result = gh(
        "issue", "create",
        "--title", title,
        "--label", LABEL,
        "--body", body,
        capture=False,
    )
    if result.returncode == 0:
        print(f"  Created issue: {title}")
    else:
        print(f"  ERROR creating issue: {title}", file=sys.stderr)


def update_issue(issue_number: int, alert: dict) -> None:
    disease = alert["disease"]
    run_date = alert.get("run_date", "")
    cv = alert.get("current_value") or "N/A"
    bm = alert.get("baseline_med") or "N/A"
    z = alert.get("z_score") or "N/A"
    ratio = alert.get("ratio") or "N/A"
    cy = alert.get("current_year", "")
    cw = alert.get("current_week", "")
    wa = alert.get("weeks_active", "")
    chart = alert.get("mermaid_chart", "")

    body = f"""\
## 週次更新 / Weekly Update — {run_date}

{chart}

| 指標 | 値 |
|------|----|
| 最新データ週 / Latest data week | {cy}年 第{cw}週 |
| 現在値 / Current reports | {cv} |
| 季節性基準値 / Seasonal baseline | {bm} |
| 基準比 / Ratio | {ratio}x |
| Z スコア | {z} |
| 継続期間 / Weeks active | {wa} 週 |

**{disease}** のアラートは継続中です。 / Alert continues.
"""

    result = gh("issue", "comment", str(issue_number), "--body", body, capture=False)
    if result.returncode == 0:
        print(f"  Updated issue #{issue_number}: {disease}")
    else:
        print(f"  ERROR updating issue #{issue_number}", file=sys.stderr)


def close_issue(issue_number: int, disease: str, run_date: str) -> None:
    body = f"""\
## トレンド終了 / Alert Resolved — {run_date}

**{disease}** の報告数が通常レベルに戻りました。このIssueをクローズします。

The **{disease}** trend has returned to baseline levels. Closing this issue.
"""
    gh("issue", "comment", str(issue_number), "--body", body, capture=False)
    result = gh("issue", "close", str(issue_number), capture=False)
    if result.returncode == 0:
        print(f"  Closed issue #{issue_number}: {disease}")
    else:
        print(f"  ERROR closing issue #{issue_number}", file=sys.stderr)


def main() -> None:
    alerts_path = Path(__file__).parent / "trend_alerts.json"
    if not alerts_path.exists():
        print("ERROR: trend_alerts.json not found. Run detect_trends.py first.", file=sys.stderr)
        sys.exit(1)

    with open(alerts_path, encoding="utf-8") as f:
        data = json.load(f)

    run_date = data.get("run_date", "")
    active_alerts = data.get("active_alerts", [])
    inactive_diseases = data.get("inactive_diseases", [])

    # Inject run_date into each alert for formatting
    for a in active_alerts:
        a["run_date"] = run_date

    ensure_label()

    active_disease_names = {a["disease"] for a in active_alerts}

    # --- Handle active alerts ---
    print(f"\nActive alerts: {len(active_alerts)}")
    for alert in active_alerts:
        title = alert["issue_title"]
        issue_number = find_open_issue(title)
        if issue_number is None:
            create_issue(alert)
        else:
            update_issue(issue_number, alert)

    # --- Close stale issues for diseases no longer in alert ---
    print(f"\nInactive diseases to check: {len(inactive_diseases)}")
    for item in inactive_diseases:
        disease = item["disease"]
        # Only close if this disease is genuinely not in any active alert
        if disease in active_disease_names:
            continue
        open_issues = find_open_issues_for_disease(disease)
        for num in open_issues:
            close_issue(num, disease, run_date)

    print("\nDone.")


if __name__ == "__main__":
    main()
