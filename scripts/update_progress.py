#!/usr/bin/env python3
"""Regenerate the progress section of README.md from plan/weeks.tsv + log/W*.md.

Zero dependencies, stdlib only. Run: python3 scripts/update_progress.py
"""
import datetime as dt
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = ROOT / "plan" / "weeks.tsv"
LOGS = ROOT / "log"
README = ROOT / "README.md"
MARK_START = "<!-- PROGRESS:START -->"
MARK_END = "<!-- PROGRESS:END -->"

ICON = {"done": "✅", "wip": "🟡", "blocked": "⛔", "skip": "⏭️", "todo": "⬜"}
DONE = {"done", "skip"}


def die(msg):
    sys.exit(f"update_progress: {msg}")


def read_weeks():
    lines = PLAN.read_text(encoding="utf-8").splitlines()
    weeks = []
    for line in lines[1:]:
        if not line.strip():
            continue
        num, date, phase, title = line.split("\t")
        weeks.append({
            "num": num,
            "date": dt.date.fromisoformat(date),
            "phase": phase,
            "title": title,
        })
    return weeks


def read_log(num):
    path = LOGS / f"W{num}.md"
    if not path.exists():
        return "todo", ""
    text = path.read_text(encoding="utf-8")
    status = re.search(r"^status:\s*(\S+)", text, re.M)
    summary = re.search(r"^summary:\s*(.+)$", text, re.M)
    return (
        status.group(1).lower() if status else "wip",
        summary.group(1).strip() if summary else "",
    )


def progress_bar(done, total, width=30):
    filled = round(width * done / total) if total else 0
    return "█" * filled + "░" * (width - filled)


def render(weeks, today):
    for w in weeks:
        w["status"], w["summary"] = read_log(w["num"])

    done = sum(1 for w in weeks if w["status"] in DONE)
    current = None
    for w in weeks:
        if w["date"] <= today:
            current = w["num"]

    streak = 0
    for w in weeks:
        if w["status"] in DONE:
            streak += 1
        else:
            break

    out = [f"**{done}/{len(weeks)} 周完成** · 连续 {streak} 周 · 更新于 {today.isoformat()}", ""]
    out.append(f"`{progress_bar(done, len(weeks))}` {round(100 * done / len(weeks))}%")
    out.append("")
    out.append("| 周 | 起始 | 主题 | 状态 | 摘要 |")
    out.append("|---|---|---|---|---|")

    last_phase = None
    for w in weeks:
        if w["phase"] != last_phase:
            last_phase = w["phase"]
            out.append(f"| | | **{w['phase']}** | | |")
        mark = " ◀ 本周" if w["num"] == current else ""
        icon = ICON.get(w["status"], "❓")
        summary = w["summary"]
        if len(summary) > 60:
            summary = summary[:57] + "..."
        out.append(
            f"| W{w['num']}{mark} | {w['date'].isoformat()} | {w['title']} | {icon} | {summary} |"
        )

    unknown = sorted(
        p.stem for p in LOGS.glob("W*.md")
        if p.stem[1:] not in {w["num"] for w in weeks}
    )
    if unknown:
        out.append("")
        out.append(f"> ⚠️ 这些周记不在计划表中：{', '.join(unknown)}")
    return "\n".join(out)


def main():
    if not PLAN.exists():
        die(f"缺少 {PLAN}")
    text = README.read_text(encoding="utf-8")
    if MARK_START not in text or MARK_END not in text:
        die(f"README.md 缺少 {MARK_START} / {MARK_END} 标记")

    weeks = read_weeks()
    for w in weeks:
        w["status"], _ = read_log(w["num"])
    body = render(weeks, dt.date.today())
    head, rest = text.split(MARK_START, 1)
    _, tail = rest.split(MARK_END, 1)
    README.write_text(head + MARK_START + "\n" + body + "\n" + MARK_END + tail, encoding="utf-8")
    print(f"README.md 已更新（{len(weeks)} 周，{sum(1 for w in weeks if w['status'] in DONE)} 完成）")


if __name__ == "__main__":
    main()
