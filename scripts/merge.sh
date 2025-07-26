#!/usr/bin/env bash

# ------------------------------------------------------------------------------
# Script Name:    merge.sh
# Description:    本脚本用于合并多个以 filedomain_ 开头的文本文件（.txt）。
#                 合并前会显示每个文件的第二行和最后一行，供用户确认内容是否首尾相接。
#                 合并过程中会跳过每个文件的首行，并在新文件开头添加表头。
#                 最终生成一个带有时间戳、格式为 .csv 的合并输出文件。
#
# Features:
#   - 显示文件的第二行和最后一行
#   - 按文件名排序（使用 find，支持特殊字符）
#   - 用户确认后才进行合并
#   - 添加自定义 CSV 表头
#   - 原文件不被修改
#
# Usage:
#   bash merge.sh
#
# Author:         Jetsung Chan <i@jetsung.com>
# Created:        2025-07-26
# ------------------------------------------------------------------------------

# 使用 find 获取文件列表并排序
mapfile -t files < <(find . -maxdepth 1 -type f -name 'filedomain_*.txt' -printf '%P\n' | sort)

echo "以下是每个文件的第二行和最后一行（用于检查是否首尾相接）:"
echo

for file in "${files[@]}"; do
  echo "---- $file ----"
  sed -n '2p' "$file"
  tail -n 1 "$file"
  echo ""
done

# 提示用户是否继续合并
read -r -p "是否继续合并这些文件？(y/n): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "取消合并。"
  exit 0
fi

# 设置输出文件名和表头
timestamp=$(date +"%Y%m%d_%H%M%S")
output_file="merged_output_${timestamp}.csv"
header="domain, available, status, registration_date, expiration_date, nameserver, icp, error_code, provider"  # 可根据实际数据格式修改

# 写入表头
echo "$header" > "$output_file"

# 合并内容，跳过每个文件的第一行
for file in "${files[@]}"; do
  tail -n +2 "$file" >> "$output_file"
done

echo "合并完成，输出文件为：$output_file"
