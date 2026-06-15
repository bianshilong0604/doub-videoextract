"""
文件工具函数
"""

import json
import re
from pathlib import Path
from typing import Dict, Any


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    清理文件名，移除非法字符

    Args:
        filename: 原始文件名
        max_length: 最大长度

    Returns:
        清理后的文件名
    """
    # 移除换行符和其他空白字符（替换为空格）
    filename = re.sub(r'[\n\r\t]+', ' ', filename)

    # 移除非法字符（Windows文件名不允许的字符）
    filename = re.sub(r'[<>:"|?*\\\/]', '', filename)

    # 移除前后空白
    filename = filename.strip()

    # 移除多余的空格（多个空格替换为单个）
    filename = re.sub(r'\s+', ' ', filename)

    # 限制长度
    if len(filename) > max_length:
        filename = filename[:max_length].strip()

    # 如果为空，使用默认名称
    if not filename:
        filename = "untitled"

    return filename


def ensure_dir(path: Path) -> Path:
    """
    确保目录存在

    Args:
        path: 目录路径

    Returns:
        目录路径对象
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Dict[str, Any], file_path: Path):
    """
    保存JSON文件

    Args:
        data: 要保存的数据
        file_path: 文件路径
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    加载JSON文件

    Args:
        file_path: 文件路径

    Returns:
        加载的数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_urls_from_file(file_path: str) -> list:
    """
    从文件读取URL列表

    Args:
        file_path: 文件路径

    Returns:
        URL列表
    """
    urls = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if line and not line.startswith('#'):
                urls.append(line)

    return urls
