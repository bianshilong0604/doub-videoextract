"""
B站内容提取器
"""

import re
import asyncio
from typing import Optional

try:
    from bilibili_api import video, sync
    BILIBILI_API_AVAILABLE = True
except ImportError:
    BILIBILI_API_AVAILABLE = False
    print("警告: bilibili-api 未安装")

from .base import BaseExtractor, ContentData
from datetime import datetime


class BilibiliExtractor(BaseExtractor):
    """B站提取器"""

    def __init__(self):
        super().__init__()
        self.platform = "哔哩哔哩 (Bilibili)"

    def can_handle(self, url: str) -> bool:
        """判断是否可以处理该URL"""
        return 'bilibili.com' in url or 'b23.tv' in url

    def extract_bvid(self, url: str) -> Optional[str]:
        """从URL中提取BVID"""
        patterns = [
            r'BV[a-zA-Z0-9]+',
            r'/video/(BV[a-zA-Z0-9]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                bvid = match.group(0) if match.group(0).startswith('BV') else match.group(1)
                return bvid

        return None

    def extract(self, url: str) -> Optional[ContentData]:
        """提取内容"""
        if not BILIBILI_API_AVAILABLE:
            print("❌ bilibili-api 未安装，无法提取B站内容")
            return None

        return self._extract_video(url)

    async def _extract_async(self, url: str) -> Optional[ContentData]:
        """异步提取B站视频信息"""
        try:
            bvid = self.extract_bvid(url)
            if not bvid:
                print(f"❌ 无法从URL提取BVID: {url}")
                return None

            print(f"✓ 提取到BVID: {bvid}")

            # 创建视频对象
            v = video.Video(bvid=bvid)

            # 获取视频信息
            print("⏳ 正在获取B站视频信息...")
            info = await v.get_info()

            # 尝试获取字幕
            print("⏳ 正在获取字幕...")
            subtitle_list = []
            try:
                subtitle_data = await v.get_subtitle(0)
                if subtitle_data and 'subtitles' in subtitle_data:
                    for sub in subtitle_data['subtitles']:
                        if 'body' in sub:
                            for item in sub['body']:
                                content = item.get('content', '').strip()
                                if content:
                                    subtitle_list.append(content)
            except Exception as e:
                print(f"⚠️  字幕获取失败（可能需要登录）: {e}")

            # 构建 ContentData
            content = ContentData()
            content.platform = self.platform
            content.content_type = "video"
            content.url = url
            content.title = info.get('title', '未知标题')
            content.author = info.get('owner', {}).get('name', '未知作者')
            content.author_id = str(info.get('owner', {}).get('mid', ''))
            content.description = info.get('desc', '')
            content.duration = info.get('duration', 0)
            content.view_count = info.get('stat', {}).get('view', 0)
            content.like_count = info.get('stat', {}).get('like', 0)
            content.comment_count = info.get('stat', {}).get('reply', 0)
            content.share_count = info.get('stat', {}).get('share', 0)
            content.cover_url = info.get('pic', '')
            content.subtitles = subtitle_list

            # 处理发布时间
            pubdate = info.get('pubdate', 0)
            if pubdate:
                content.publish_time = datetime.fromtimestamp(pubdate).strftime('%Y-%m-%d %H:%M:%S')

            # 处理标签
            tags = info.get('tag', '')
            if tags:
                content.tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

            print(f"✅ B站视频提取成功: {content.title}")
            if subtitle_list:
                print(f"   - 提取到字幕 {len(subtitle_list)} 条")

            return content

        except Exception as e:
            print(f"❌ B站视频提取失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_video(self, url: str) -> Optional[ContentData]:
        """同步接口"""
        return sync(self._extract_async(url))
