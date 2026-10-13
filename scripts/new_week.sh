#!/usr/bin/env bash
# 新建一周的周记。用法: scripts/new_week.sh 03
set -euo pipefail

num="${1:?用法: scripts/new_week.sh <两位周号>  (例如 03)}"
printf -v n '%02d' "$((10#$num))" 2>/dev/null || { echo "周号必须是数字"; exit 1; }

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
title=$(awk -F'\t' -v n="$n" '$1==n {print $4}' "$root/plan/weeks.tsv")
[ -n "$title" ] || { echo "周号 $n 不在 plan/weeks.tsv 中"; exit 1; }
date=$(awk -F'\t' -v n="$n" '$1==n {print $2}' "$root/plan/weeks.tsv")

out="$root/log/W$n.md"
[ -e "$out" ] && { echo "$out 已存在"; exit 1; }

sed -e "s/^# WXX · 主题/# W$n · $title/" \
    -e "s/^date: .*/date: $date/" \
    "$root/log/_TEMPLATE.md" > "$out"

echo "已创建 $out"
