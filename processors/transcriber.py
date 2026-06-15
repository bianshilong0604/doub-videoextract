"""
语音转文字处理器
支持多种方式：Whisper本地、OpenAI API、硅基流动等
"""

import subprocess
from typing import Optional


class Transcriber:
    """语音转文字处理器"""

    def __init__(self, config: Optional[dict] = None):
        """
        初始化转录器

        Args:
            config: 配置字典，包含 method, api_key 等
        """
        if config is None:
            config = {}

        self.method = config.get('method', 'auto')  # auto, whisper, openai, siliconflow
        self.enabled = config.get('enabled', False)
        self.api_key = config.get('api_key', '')
        self.whisper_model = config.get('whisper_model', 'base')

        if not self.enabled:
            print("⚠️  语音转文字功能未启用")

    def transcribe_video(self, video_url: str) -> Optional[str]:
        """
        转录视频语音为文字

        Args:
            video_url: 视频URL

        Returns:
            转录的文字内容
        """
        if not self.enabled:
            return None

        try:
            if self.method == 'whisper' or self.method == 'auto':
                return self._transcribe_with_whisper(video_url)
            elif self.method == 'openai':
                return self._transcribe_with_openai_api(video_url)
            elif self.method == 'siliconflow':
                return self._transcribe_with_siliconflow(video_url)
            else:
                print(f"⚠️  不支持的转录方法: {self.method}")
                return None

        except Exception as e:
            print(f"❌ 语音转文字失败: {e}")
            return None

    def _transcribe_with_whisper(self, video_url: str) -> Optional[str]:
        """使用本地Whisper转录"""
        try:
            print(f"⏳ 使用Whisper转录语音（模型: {self.whisper_model}）...")

            cmd = [
                'whisper',
                video_url,
                '--model', self.whisper_model,
                '--language', 'zh',
                '--output_format', 'txt'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300
            )

            if result.returncode == 0:
                print("✅ Whisper转录完成")
                return result.stdout
            else:
                print(f"❌ Whisper转录失败: {result.stderr}")
                return None

        except FileNotFoundError:
            print("❌ Whisper未安装，请运行: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"❌ Whisper转录出错: {e}")
            return None

    def _transcribe_with_openai_api(self, video_url: str) -> Optional[str]:
        """使用OpenAI API转录"""
        print("⚠️  OpenAI API转录功能待实现")
        return None

    def _transcribe_with_siliconflow(self, video_url: str) -> Optional[str]:
        """使用硅基流动API转录"""
        print("⚠️  硅基流动API转录功能待实现")
        return None
