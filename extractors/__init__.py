"""
提取器模块初始化
"""

from .base import BaseExtractor, ContentData
from .douyin import DouyinExtractor
from .bilibili import BilibiliExtractor

__all__ = [
    'BaseExtractor',
    'ContentData',
    'DouyinExtractor',
    'BilibiliExtractor',
]
