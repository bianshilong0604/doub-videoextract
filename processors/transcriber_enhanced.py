"""
增强版语音转文字处理器
集成 faster-whisper 和回退机制
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    print("⚠️  faster-whisper 未安装")
    WHISPER_AVAILABLE = False


class EnhancedTranscriber:
    """增强版转录器"""

    def __init__(self, config: Optional[dict] = None):
        """
        初始化转录器

        Args:
            config: 配置字典
        """
        if config is None:
            config = {}

        self.enabled = config.get('enabled', True)  # 默认启用
        self.method = config.get('method', 'auto')
        self.whisper_model_size = config.get('whisper_model', 'base')
        self.language = config.get('language', 'zh')

        # 初始化 Whisper 模型（延迟加载）
        self.whisper_model = None

        if not self.enabled:
            print("⚠️  语音转文字功能未启用")
        elif not WHISPER_AVAILABLE:
            print("⚠️  faster-whisper 未安装，语音转文字功能不可用")
            self.enabled = False

    def _init_whisper_model(self):
        """延迟初始化 Whisper 模型"""
        if self.whisper_model is None and WHISPER_AVAILABLE:
            try:
                print(f"⏳ 正在加载 Whisper 模型（{self.whisper_model_size}）...")
                print("   首次运行会自动下载模型，请耐心等待...")

                self.whisper_model = WhisperModel(
                    self.whisper_model_size,
                    device="cpu",
                    compute_type="int8"
                )

                print(f"✅ Whisper 模型加载完成")

            except Exception as e:
                print(f"❌ Whisper 模型加载失败: {e}")
                self.enabled = False

    def transcribe_video_url(self, video_url: str) -> Optional[List[str]]:
        """
        从视频URL转录语音

        Args:
            video_url: 视频URL

        Returns:
            转录的文本列表
        """
        if not self.enabled:
            return None

        try:
            print(f"\n{'='*70}")
            print(f"🎙️  语音转文字")
            print(f"{'='*70}")

            print("\n📍 第1步：提取音频...")
            audio_file = self._extract_audio(video_url)
            if not audio_file:
                print("❌ 音频提取失败")
                return None

            print(f"✅ 音频提取成功: {audio_file}")

            print("\n📍 第2步：Whisper 语音识别...")
            self._init_whisper_model()

            if not self.whisper_model:
                print("❌ Whisper 模型未加载")
                return None

            segments, info = self.whisper_model.transcribe(
                str(audio_file),
                language=self.language,
                beam_size=5
            )

            print(f"✅ 检测语言: {info.language} (概率: {info.language_probability:.2f})")

            transcripts = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    transcripts.append(text)
                    print(f"   [{segment.start:.2f}s -> {segment.end:.2f}s] {text}")

            try:
                audio_file.unlink()
            except Exception:
                pass

            if transcripts:
                print(f"\n✅ 转录完成，共 {len(transcripts)} 段")
                return transcripts
            else:
                print("⚠️  未能提取到文本")
                return None

        except Exception as e:
            print(f"❌ 转录失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_audio(self, video_url: str) -> Optional[Path]:
        """使用 yt-dlp 提取音频"""
        try:
            temp_dir = Path(tempfile.gettempdir())
            audio_file = temp_dir / f"audio_{hash(video_url)}.wav"

            if audio_file.exists():
                audio_file.unlink()

            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'wav',
                '--audio-quality', '0',
                '--output', str(audio_file),
                video_url
            ]

            print(f"   执行命令: yt-dlp ...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300
            )

            if result.returncode == 0 and audio_file.exists():
                return audio_file
            else:
                print(f"   yt-dlp 错误: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print("   音频下载超时")
            return None
        except Exception as e:
            print(f"   音频提取错误: {e}")
            return None

    def transcribe_file(self, audio_file: Path) -> Optional[List[str]]:
        """
        从本地音频文件转录

        Args:
            audio_file: 音频文件路径

        Returns:
            转录的文本列表
        """
        if not self.enabled or not self.whisper_model:
            return None

        try:
            segments, info = self.whisper_model.transcribe(
                str(audio_file),
                language=self.language,
                beam_size=5
            )

            transcripts = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    transcripts.append(text)

            return transcripts if transcripts else None

        except Exception as e:
            print(f"❌ 文件转录失败: {e}")
            return None
