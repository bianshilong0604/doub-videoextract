"""
基础提取器类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class ContentData:
    """内容数据模型"""

    # 基本信息
    platform: str = ""  # 平台名称
    content_type: str = ""  # 内容类型：video, image_text, article
    url: str = ""  # 原始URL

    # 标题和作者
    title: str = ""
    author: str = ""
    author_id: str = ""

    # 内容
    description: str = ""
    text_content: str = ""  # 图文内容/文案
    subtitles: List[str] = field(default_factory=list)  # 字幕

    # 媒体
    cover_url: str = ""
    images: List[str] = field(default_factory=list)  # 图片列表
    video_url: str = ""

    # 统计数据
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0

    # 元数据
    duration: int = 0  # 视频时长（秒）
    tags: List[str] = field(default_factory=list)
    publish_time: str = ""

    # 提取信息
    extracted_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    extractor_version: str = "1.0"

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'platform': self.platform,
            'content_type': self.content_type,
            'url': self.url,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'text_content': self.text_content,
            'subtitles': self.subtitles,
            'cover_url': self.cover_url,
            'images': self.images,
            'video_url': self.video_url,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'share_count': self.share_count,
            'duration': self.duration,
            'tags': self.tags,
            'publish_time': self.publish_time,
            'extracted_at': self.extracted_at
        }

    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        lines = []

        # 标题
        lines.append(f"# {self.title}\n")

        # 元信息
        lines.append("## 📋 基本信息\n")
        lines.append(f"- **平台**: {self.platform}")
        lines.append(f"- **类型**: {self.content_type}")
        lines.append(f"- **作者**: {self.author}")

        if self.duration > 0:
            minutes = self.duration // 60
            seconds = self.duration % 60
            lines.append(f"- **时长**: {minutes}分{seconds}秒")

        if self.publish_time:
            lines.append(f"- **发布时间**: {self.publish_time}")

        lines.append("")

        # 统计数据
        if any([self.view_count, self.like_count, self.comment_count, self.share_count]):
            lines.append("## 📊 数据统计\n")
            if self.view_count:
                lines.append(f"- **播放量**: {self.view_count:,}")
            if self.like_count:
                lines.append(f"- **点赞数**: {self.like_count:,}")
            if self.comment_count:
                lines.append(f"- **评论数**: {self.comment_count:,}")
            if self.share_count:
                lines.append(f"- **分享数**: {self.share_count:,}")
            lines.append("")

        # 描述
        if self.description:
            lines.append("## 📄 描述\n")
            lines.append(self.description)
            lines.append("")

        # 文案/文本内容
        if self.text_content:
            lines.append("## 📝 文案内容\n")
            lines.append(self.text_content)
            lines.append("")

        # 字幕
        if self.subtitles:
            lines.append("## 💬 字幕/文本\n")
            for subtitle in self.subtitles:
                lines.append(subtitle)
            lines.append("")

        # 标签
        if self.tags:
            lines.append("## 🏷️ 标签\n")
            lines.append(", ".join(f"`{tag}`" for tag in self.tags))
            lines.append("")

        # 图片
        if self.images:
            lines.append("## 🖼️ 图片\n")
            for i, img_url in enumerate(self.images, 1):
                lines.append(f"{i}. {img_url}")
            lines.append("")

        # 底部信息
        lines.append("---")
        lines.append(f"\n*提取时间: {self.extracted_at}*  ")
        lines.append(f"*原始链接: {self.url}*")

        return "\n".join(lines)


class BaseExtractor(ABC):
    """基础提取器抽象类"""

    def __init__(self):
        self.platform = "unknown"

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """判断是否可以处理该URL"""
        pass

    @abstractmethod
    def extract(self, url: str) -> Optional[ContentData]:
        """提取内容"""
        pass

    def detect_content_type(self, url: str) -> str:
        """检测内容类型"""
        return "unknown"

    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""

        # 移除多余空白
        text = " ".join(text.split())

        return text.strip()
