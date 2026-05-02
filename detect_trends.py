#!/usr/bin/env python3
"""
Trend detection for Japanese infectious disease surveillance data.

Algorithm: seasonal same-week baseline (compare current week vs same week
in past N years). Conservative dual-gate: z-score AND ratio both must exceed
thresholds for 2 consecutive weeks before an alert is raised.

Outputs trend_alerts.json consumed by the GitHub Actions workflow.
"""

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Disease configurations
# ---------------------------------------------------------------------------

TEITEN_DISEASES = {
    "インフルエンザ": {
        "col": "インフルエンザ_報告",
        "min_abs": 500,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
        "exclude_suppressed_frac": 0.15,  # skip COVID-suppressed flu years
    },
    "ＲＳウイルス感染症": {
        "col": "ＲＳウイルス感染症_報告",
        "min_abs": 200,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "咽頭結膜熱": {
        "col": "咽頭結膜熱_報告",
        "min_abs": 100,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "Ａ群溶血性レンサ球菌咽頭炎": {
        "col": "Ａ群溶血性レンサ球菌咽頭炎_報告",
        "min_abs": 200,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "感染性胃腸炎": {
        "col": "感染性胃腸炎_報告",
        "min_abs": 500,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "手足口病": {
        "col": "手足口病_報告",
        "min_abs": 100,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "百日咳": {
        "col": "百日咳_報告",
        "min_abs": 20,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "マイコプラズマ肺炎": {
        "col": "マイコプラズマ肺炎_報告",
        "min_abs": 50,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "COVID-19": {
        "col": "COVID-19_報告",
        "min_abs": 100,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 3,
    },
    "ヘルパンギーナ": {
        "col": "ヘルパンギーナ_報告",
        "min_abs": 100,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "流行性耳下腺炎": {
        "col": "流行性耳下腺炎_報告",
        "min_abs": 50,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
}

ZENSU_DISEASES = {
    "百日咳": {
        "col": "百日咳_報告",
        "min_abs": 20,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "麻しん": {
        "col": "麻しん_報告",
        "min_abs": 5,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
        "cap_ratio": 50,
    },
    "梅毒": {
        "col": "梅毒_報告",
        "min_abs": 100,
        "z_thresh": 3.0,
        "ratio_thresh": 2.0,
        "baseline_years": 2,
    },
    "風しん": {
        "col": "風しん_報告",
        "min_abs": 10,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
        "cap_ratio": 50,
    },
    "劇症型溶血性レンサ球菌感染症": {
        "col": "劇症型溶血性レンサ球菌感染症_報告",
        "min_abs": 10,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "腸管出血性大腸菌感染症": {
        "col": "腸管出血性大腸菌感染症_報告",
        "min_abs": 50,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "レジオネラ症": {
        "col": "レジオネラ症_報告",
        "min_abs": 30,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "急性脳炎": {
        "col": "急性脳炎_報告",
        "min_abs": 10,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "侵襲性肺炎球菌感染症": {
        "col": "侵襲性肺炎球菌感染症_報告",
        "min_abs": 30,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
    },
    "デング熱": {
        "col": "デング熱_報告",
        "min_abs": 5,
        "z_thresh": 2.5,
        "ratio_thresh": 2.0,
        "baseline_years": 5,
        "cap_ratio": 50,
    },
}

CONSEC_WEEKS = 2  # required consecutive alert weeks before raising / after dropping

# ---------------------------------------------------------------------------
# Core detection logic
# ---------------------------------------------------------------------------


def agg_national(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Sum all prefectures to national weekly total."""
    return (
        df.groupby(["年", "週", "開始日"])[col]
        .sum(min_count=1)
        .reset_index()
        .sort_values(["年", "週"])
        .reset_index(drop=True)
    )


def build_alert_flags(
    df: pd.DataFrame,
    col: str,
    min_abs: float,
    z_thresh: float,
    ratio_thresh: float,
    baseline_years: int,
    exclude_suppressed_frac: float = 0.0,
    cap_ratio: float = 100.0,
    consec_weeks: int = CONSEC_WEEKS,
) -> pd.DataFrame:
    """
    Compute per-week alert flags using seasonal same-week baseline.

    Returns df with added columns:
      baseline_med, baseline_std, z, ratio, raw_flag, alert
    """
    d = df.copy().reset_index(drop=True)
    vals = d[col]
    annual = d.groupby("年")[col].sum()
    long_avg = float(annual.mean()) if len(annual) > 0 else 1.0

    baseline_med = np.full(len(d), np.nan)
    baseline_std = np.full(len(d), np.nan)

    for i, row in d.iterrows():
        yr, wk = int(row["年"]), int(row["週"])
        candidate_years = list(range(yr - baseline_years, yr))
        if exclude_suppressed_frac > 0 and long_avg > 0:
            candidate_years = [
                y
                for y in candidate_years
                if annual.get(y, 0) >= long_avg * exclude_suppressed_frac
            ]
        hist = d[(d["週"] == wk) & (d["年"].isin(candidate_years))][col].dropna()
        if len(hist) >= 2:
            baseline_med[i] = float(hist.median())
            baseline_std[i] = float(hist.std())

    d["baseline_med"] = baseline_med
    d["baseline_std"] = baseline_std
    d["z"] = (vals - d["baseline_med"]) / (d["baseline_std"] + 1e-9)
    raw_ratio = vals / (d["baseline_med"] + 1e-9)
    d["ratio"] = np.minimum(raw_ratio, cap_ratio)

    d["raw_flag"] = (vals >= min_abs) & (d["z"] >= z_thresh) & (d["ratio"] >= ratio_thresh)

    # Require consec_weeks consecutive raw flags to open an alert
    d["alert"] = (
        d["raw_flag"]
        .rolling(consec_weeks, min_periods=consec_weeks)
        .min()
        .fillna(0)
        .astype(bool)
    )

    return d


def find_streak_start(alert_series: pd.Series, current_idx: int) -> int:
    """
    Given a boolean alert series and the index of the current (latest) week,
    walk backwards to find the first week of the current consecutive alert run.
    Returns the index of the streak start.
    """
    idx = current_idx
    while idx > 0 and alert_series.iloc[idx - 1]:
        idx -= 1
    return idx


def generate_mermaid(
    flagged: pd.DataFrame,
    col: str,
    disease_name: str,
    dataset: str,
    n_weeks: int = 12,
) -> str:
    """
    Build a Mermaid xychart-beta block showing the last n_weeks of data.
    Bar = actual weekly reports; Line = seasonal baseline median.
    GitHub renders Mermaid natively in markdown — no image hosting needed.
    """
    recent = flagged.tail(n_weeks).copy()

    # Show year only on the first week of each year to reduce x-axis clutter
    labels = []
    seen_years: set[int] = set()
    for _, r in recent.iterrows():
        yr, wk = int(r["年"]), int(r["週"])
        if yr not in seen_years:
            labels.append(f"{yr}W{wk:02d}")
            seen_years.add(yr)
        else:
            labels.append(f"W{wk:02d}")
    actual = [int(round(v)) if pd.notna(v) else 0 for v in recent[col]]
    baseline = [int(round(v)) if pd.notna(v) else 0 for v in recent["baseline_med"]]

    y_max = max(max(actual, default=1), max(baseline, default=0), 1)
    y_max = int(y_max * 1.2) + 1

    labels_str = ", ".join(f'"{l}"' for l in labels)
    actual_str = ", ".join(str(v) for v in actual)
    baseline_str = ", ".join(str(v) for v in baseline)

    return (
        "```mermaid\n"
        "xychart-beta\n"
        f'    title "{disease_name} [{dataset}] — Last {n_weeks} Weeks"\n'
        f"    x-axis [{labels_str}]\n"
        f'    y-axis "Cases (national total)" 0 --> {y_max}\n'
        f"    bar [{actual_str}]\n"
        f"    line [{baseline_str}]\n"
        "```"
    )


def detect_disease(
    df: pd.DataFrame, dataset: str, disease_name: str, config: dict
) -> dict:
    """
    Run detection for a single disease and return a result dict.
    The result captures only the CURRENT state (latest weeks in data).
    """
    col = config["col"]
    if col not in df.columns:
        return {"dataset": dataset, "disease": disease_name, "in_alert": False, "skipped": True}

    national = agg_national(df, col)
    if len(national) < 4:
        return {"dataset": dataset, "disease": disease_name, "in_alert": False, "skipped": True}

    flagged = build_alert_flags(
        national,
        col,
        min_abs=config["min_abs"],
        z_thresh=config["z_thresh"],
        ratio_thresh=config["ratio_thresh"],
        baseline_years=config["baseline_years"],
        exclude_suppressed_frac=config.get("exclude_suppressed_frac", 0.0),
        cap_ratio=config.get("cap_ratio", 100.0),
    )

    latest_idx = len(flagged) - 1
    latest = flagged.iloc[latest_idx]
    in_alert = bool(latest["alert"])

    result: dict = {
        "dataset": dataset,
        "disease": disease_name,
        "col": col,
        "in_alert": in_alert,
        "current_year": int(latest["年"]),
        "current_week": int(latest["週"]),
        "current_month": int(pd.Timestamp(latest["開始日"]).month),
        "current_value": float(latest[col]) if pd.notna(latest[col]) else None,
        "baseline_med": round(float(latest["baseline_med"]), 1) if pd.notna(latest["baseline_med"]) else None,
        "z_score": round(float(latest["z"]), 2) if pd.notna(latest["z"]) else None,
        "ratio": round(float(latest["ratio"]), 2) if pd.notna(latest["ratio"]) else None,
    }

    if in_alert:
        streak_idx = find_streak_start(flagged["alert"], latest_idx)
        streak_row = flagged.iloc[streak_idx]
        result["alert_start_year"] = int(streak_row["年"])
        result["alert_start_week"] = int(streak_row["週"])
        result["alert_start_month"] = int(pd.Timestamp(streak_row["開始日"]).month)
        result["weeks_active"] = latest_idx - streak_idx + 1

        yr = result["alert_start_year"]
        mo = result["alert_start_month"]
        wk = result["alert_start_week"]
        result["issue_title"] = f"{yr}{mo:02d}W({wk:02d}) - {disease_name}"

        result["mermaid_chart"] = generate_mermaid(flagged, col, disease_name, dataset)

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    data_root = Path(__file__).parent / "data"

    teiten_path = data_root / "teiten" / "merged_teiten.parquet"
    zensu_path = data_root / "zensu" / "merged_zensu.parquet"

    if not teiten_path.exists() or not zensu_path.exists():
        print("ERROR: merged parquet files not found. Run: uv run main.py merge", file=sys.stderr)
        sys.exit(1)

    df_teiten = pd.read_parquet(teiten_path)
    df_zensu = pd.read_parquet(zensu_path)

    results = []

    for disease_name, config in TEITEN_DISEASES.items():
        r = detect_disease(df_teiten, "teiten", disease_name, config)
        results.append(r)

    for disease_name, config in ZENSU_DISEASES.items():
        r = detect_disease(df_zensu, "zensu", disease_name, config)
        results.append(r)

    active_alerts = [r for r in results if r.get("in_alert")]
    inactive = [r for r in results if not r.get("in_alert") and not r.get("skipped")]

    output = {
        "run_date": date.today().isoformat(),
        "active_alerts": active_alerts,
        "inactive_diseases": [
            {"dataset": r["dataset"], "disease": r["disease"]} for r in inactive
        ],
    }

    out_path = Path(__file__).parent / "trend_alerts.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
