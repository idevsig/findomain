from __future__ import annotations

import logging
import os
from pathlib import Path

# VALID_LOG_LEVELS = {0, 10, 20, 30, 40, 50}


def set_log_level(level: int | str):
    level_mapping = logging.getLevelNamesMapping()
    level_value = logging.INFO

    if isinstance(level, str):
        level_name = level.upper()
        if level_name in level_mapping:
            level_value = level_mapping[level_name]
    elif isinstance(level, int):
        valid_levels = set(level_mapping.values())  # 提取合法的整数值集合
        if level in valid_levels:
            level_value = level
    return level_value


def setup_logging(
    name: str,
    dir_path: str = 'logs',
    level: int = logging.INFO,
):
    """配置日志记录"""
    # 创建日志目录
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=set_log_level(level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(dir_path, name)),
            logging.StreamHandler(),
        ],
    )
