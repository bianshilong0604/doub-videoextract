"""
抖音内容提取器
支持：视频、图文作品
"""

import re
import json
import subprocess
import requests
from typing import Optional
from bs4 import BeautifulSoup

from .base import BaseExtractor, ContentData


class DouyinExtractor(BaseExtractor):
    """抖音提取器"""

    def __init__(self):
        super().__init__()
        self.platform = "抖音 (Douyin)"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def can_handle(self, url: str) -> bool:
        """判断是否可以处理该URL"""
        return 'douyin.com' in url or 'v.douyin.com' in url

    def detect_content_type(self, url: str) -> str:
        """检测内容类型"""
        try:
            response = requests.head(url, headers=self.headers, allow_redirects=True, timeout=10)
            real_url = response.url

            if '/note/' in real_url:
                return 'image_text'
            elif '/video/' in real_url:
                return 'video'
            else:
                return 'unknown'
        except:
            return 'unknown'

    def extract(self, url: str) -> Optional[ContentData]:
        """提取内容"""
        content_type = self.detect_content_type(url)

        if content_type == 'video':
            return self._extract_video(url)
        elif content_type == 'image_text':
            return self._extract_image_text(url)
        else:
            print(f"⚠️ 无法识别内容类型: {url}")
            return None

    def _extract_video(self, url: str) -> Optional[ContentData]:
        """提取视频内容"""
        try:
            print(f"⏳ 正在提取抖音视频...")

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
                print(f"❌ yt-dlp 提取失败")
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

            print(f"✅ 视频提取成功: {content.title}")
            return content

        except Exception as e:
            print(f"❌ 视频提取失败: {e}")
            return None

    def _extract_image_text(self, url: str) -> Optional[ContentData]:
        """提取图文内容"""
        try:
            print(f"⏳ 正在提取抖音图文...")

            response = requests.head(url, headers=self.headers, allow_redirects=True, timeout=10)
            real_url = response.url

            note_id_match = re.search(r'/note/(\d+)', real_url)
            if not note_id_match:
                print(f"❌ 无法提取note_id")
                return None

            note_id = note_id_match.group(1)
            print(f"✓ 提取到 note_id: {note_id}")

            response = requests.get(real_url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            content = ContentData()
            content.platform = self.platform
            content.content_type = "image_text"
            content.url = url

            og_title = soup.find('meta', property='og:title')
            if og_title:
                content.title = og_title.get('content', '未知标题')
            else:
                title_tag = soup.find('title')
                content.title = title_tag.text if title_tag else '未知标题'

            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                content.description = og_desc.get('content', '')

            og_image = soup.find('meta', property='og:image')
            if og_image:
                content.cover_url = og_image.get('content', '')

            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                except:
                    continue

            images = soup.find_all('img')
            for img in images:
                img_url = img.get('src') or img.get('data-src')
                if img_url and img_url.startswith('http'):
                    content.images.append(img_url)

            content_divs = soup.find_all(['p', 'div'], class_=re.compile(r'desc|content|text'))
            text_parts = []
            for div in content_divs:
                text = div.get_text(strip=True)
                if text and len(text) > 10:
                    text_parts.append(text)

            if text_parts:
                content.text_content = "\n\n".join(text_parts)
            else:
                content.text_content = content.description

            print(f"✅ 图文提取成功: {content.title}")
            print(f"   - 提取到 {len(content.images)} 张图片")

            return content

        except Exception as e:
            print(f"❌ 图文提取失败: {e}")
            import traceback
            traceback.print_exc()
            return None
