"""
增强版抖音提取器
集成 Douyin_TikTok_Download_API + video-summarizer
"""

import re
import json
import subprocess
import requests
from typing import Optional, List, Dict
from pathlib import Path

try:
    from douyin_tiktok_scraper.scraper import Scraper as DouyinScraperLib
    DOUYIN_LIB_AVAILABLE = True
except ImportError:
    print("⚠️  douyin-tiktok-scraper 未安装")
    DOUYIN_LIB_AVAILABLE = False

from .base import BaseExtractor, ContentData


class EnhancedDouyinExtractor(BaseExtractor):
    """增强版抖音提取器"""

    def __init__(self):
        super().__init__()
        self.platform = "抖音 (Douyin)"

        if DOUYIN_LIB_AVAILABLE:
            self.scraper = DouyinScraperLib()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def can_handle(self, url: str) -> bool:
        """判断是否可以处理该URL"""
        return 'douyin.com' in url or 'v.douyin.com' in url

    def extract(self, url: str) -> Optional[ContentData]:
        """提取内容 - 三层回退机制"""

        print(f"\n{'='*70}")
        print(f"🎯 抖音内容提取（三层回退机制）")
        print(f"{'='*70}")

        # 第一层：使用专业库
        if DOUYIN_LIB_AVAILABLE:
            print("\n📍 第1层：尝试使用 Douyin_TikTok_Download_API...")
            result = self._extract_with_official_lib(url)
            if result:
                print("✅ 第1层成功：专业库提取完成")
                return result
            print("⚠️  第1层失败，尝试下一层...")

        # 第二层：使用 yt-dlp
        print("\n📍 第2层：尝试使用 yt-dlp...")
        result = self._extract_with_ytdlp(url)
        if result:
            print("✅ 第2层成功：yt-dlp 提取完成")
            return result
        print("⚠️  第2层失败，尝试下一层...")

        # 第三层：网页解析
        print("\n📍 第3层：尝试网页解析...")
        result = self._extract_with_web_parsing(url)
        if result:
            print("✅ 第3层成功：网页解析完成")
            return result

        print("❌ 所有方法均失败")
        return None

    def _extract_with_official_lib(self, url: str) -> Optional[ContentData]:
        """第1层：使用官方库提取"""
        try:
            import asyncio

            async def extract_async():
                result = await self.scraper.hybrid_parsing(url)
                return result

            data = asyncio.run(extract_async())

            if not data or 'status' not in data or data.get('status') != 'success':
                return None

            content_type = "video" if data.get('type') == 'video' else "image_text"

            content = ContentData()
            content.platform = self.platform
            content.content_type = content_type
            content.url = url

            content.title = data.get('desc', '未知标题')

            author_data = data.get('author', {})
            content.author = author_data.get('nickname', '未知作者')
            content.author_id = author_data.get('sec_uid', '')

            content.description = data.get('desc', '')

            statistics = data.get('statistics', {})
            content.like_count = statistics.get('digg_count', 0)
            content.comment_count = statistics.get('comment_count', 0)
            content.share_count = statistics.get('share_count', 0)
            content.view_count = statistics.get('play_count', 0)

            video_data = data.get('video_data', {})
            if isinstance(video_data, dict):
                content.video_url = video_data.get('nwm_video_url_HQ', '') or video_data.get('nwm_video_url', '')

            cover_data = data.get('cover_data', {})
            if isinstance(cover_data, dict):
                content.cover_url = cover_data.get('cover', '') or cover_data.get('dynamic_cover', '')

            return content

        except Exception as e:
            print(f"   官方库提取失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_with_ytdlp(self, url: str) -> Optional[ContentData]:
        """第2层：使用 yt-dlp 提取"""
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                url
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            if result.returncode != 0:
                return None

            info = json.loads(result.stdout)

            content = ContentData()
            content.platform = self.platform
            content.content_type = "video"
            content.url = url
            content.title = info.get('title', '未知标题')
            content.author = info.get('uploader', '未知作者')
            content.author_id = info.get('uploader_id', '')
            content.description = info.get('description', '')
            content.duration = info.get('duration', 0)
            content.view_count = info.get('view_count', 0)
            content.like_count = info.get('like_count', 0)
            content.comment_count = info.get('comment_count', 0)
            content.tags = info.get('tags', [])
            content.video_url = info.get('url', '')
            content.cover_url = info.get('thumbnail', '')

            return content

        except Exception as e:
            print(f"   yt-dlp 提取失败: {e}")
            return None

    def _extract_with_web_parsing(self, url: str) -> Optional[ContentData]:
        """第3层：网页解析（fallback）"""
        try:
            from bs4 import BeautifulSoup

            response = requests.head(url, headers=self.headers, allow_redirects=True, timeout=10)
            real_url = response.url

            if '/note/' in real_url:
                return self._parse_note(real_url)
            else:
                return self._parse_video_web(real_url)

        except Exception as e:
            print(f"   网页解析失败: {e}")
            return None

    def _parse_video_web(self, url: str) -> Optional[ContentData]:
        """解析视频页面"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            content = ContentData()
            content.platform = self.platform
            content.content_type = "video"
            content.url = url

            og_title = soup.find('meta', property='og:title')
            if og_title:
                content.title = og_title.get('content', '未知标题')

            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                content.description = og_desc.get('content', '')

            og_image = soup.find('meta', property='og:image')
            if og_image:
                content.cover_url = og_image.get('content', '')

            return content

        except Exception as e:
            print(f"   视频页面解析失败: {e}")
            return None

    def _parse_note(self, url: str) -> Optional[ContentData]:
        """解析图文页面"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            content = ContentData()
            content.platform = self.platform
            content.content_type = "image_text"
            content.url = url

            og_title = soup.find('meta', property='og:title')
            if og_title:
                content.title = og_title.get('content', '未知标题')

            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                content.description = og_desc.get('content', '')

            og_image = soup.find('meta', property='og:image')
            if og_image:
                content.cover_url = og_image.get('content', '')

            images = soup.find_all('img')
            for img in images:
                img_url = img.get('src') or img.get('data-src')
                if img_url and img_url.startswith('http'):
                    content.images.append(img_url)

            return content

        except Exception as e:
            print(f"   图文页面解析失败: {e}")
            return None

    def extract_subtitles(self, content: ContentData) -> List[str]:
        """提取字幕 - 使用Whisper作为回退"""
        # 抖音一般没有字幕，后续可以集成Whisper进行语音识别
        return []
