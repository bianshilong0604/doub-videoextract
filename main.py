#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能视频图文内容提取与总结工具 - 主程序
"""

import sys
import io
import argparse
import json
from pathlib import Path
from typing import List, Optional

# 设置标准输出编码为 UTF-8 (Windows)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from extractors import BilibiliExtractor, ContentData
from extractors.douyin_enhanced import EnhancedDouyinExtractor
from processors import Summarizer
from processors.transcriber_enhanced import EnhancedTranscriber
from utils import sanitize_filename, ensure_dir, save_json, read_urls_from_file


class ContentExtractorApp:
    """内容提取应用"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化应用

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)

        self.extractors = [
            EnhancedDouyinExtractor(),
            BilibiliExtractor(),
        ]

        self.summarizer = Summarizer(self.config.get('ai_api', {}))
        self.transcriber = EnhancedTranscriber(self.config.get('transcribe', {}))

        output_dir = self.config.get('output', {}).get('dir', './output')
        self.output_dir = ensure_dir(Path(output_dir))

    def _load_config(self, config_path: Optional[str]) -> dict:
        """加载配置文件"""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")

        return {
            'ai_api': {
                'api_key': '',
                'base_url': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat'
            },
            'transcribe': {
                'enabled': False,
                'method': 'auto'
            },
            'output': {
                'dir': './output',
                'format': 'markdown'
            }
        }

    def detect_extractor(self, url: str):
        """检测合适的提取器"""
        for extractor in self.extractors:
            if extractor.can_handle(url):
                return extractor
        return None

    def process_url(self, url: str, summarize: bool = True) -> Optional[dict]:
        """
        处理单个URL

        Args:
            url: 要处理的URL
            summarize: 是否进行AI总结

        Returns:
            处理结果字典
        """
        print(f"\n{'='*70}")
        print(f"📎 处理URL: {url}")
        print(f"{'='*70}\n")

        extractor = self.detect_extractor(url)
        if not extractor:
            print(f"❌ 不支持的平台: {url}")
            return None

        print(f"✓ 使用提取器: {extractor.platform}")

        content = extractor.extract(url)
        if not content:
            print(f"❌ 内容提取失败")
            return None

        if content.content_type == 'video' and self.transcriber.enabled:
            if not content.subtitles:
                print(f"\n{'='*70}")
                print(f"⚠️  未检测到字幕，启动语音转文字...")
                print(f"{'='*70}")

                if content.video_url:
                    transcripts = self.transcriber.transcribe_video_url(content.video_url)
                    if transcripts:
                        content.subtitles = transcripts
                        print(f"✅ 语音转文字完成，提取到 {len(transcripts)} 段内容")
                    else:
                        print(f"⚠️  语音转文字失败，将继续处理其他内容")
                else:
                    print(f"⚠️  未获取到视频URL，无法进行语音转文字")
            else:
                print(f"✅ 已有字幕，跳过语音转文字")

        summary_data = None
        if summarize and self.summarizer.enabled:
            print(f"\n⏳ 正在进行AI总结...")
            summary_data = self.summarizer.summarize(content)

        result = self._save_result(content, summary_data)

        print(f"\n✅ 处理完成!")
        print(f"📁 保存位置: {result['output_file']}")

        return result

    def _save_result(self, content: ContentData, summary_data: Optional[dict]) -> dict:
        """保存处理结果"""
        filename = sanitize_filename(content.title)

        markdown_lines = []
        markdown_lines.append(content.to_markdown())

        if summary_data:
            markdown_lines.append("\n---\n")
            markdown_lines.append(self.summarizer.format_summary_markdown(summary_data))

        markdown_content = "\n".join(markdown_lines)

        md_file = self.output_dir / f"{filename}.md"
        md_file.write_text(markdown_content, encoding='utf-8')

        json_file = self.output_dir / f"{filename}.json"
        json_data = {
            'content': content.to_dict(),
            'summary': summary_data
        }
        save_json(json_data, json_file)

        return {
            'title': content.title,
            'platform': content.platform,
            'content_type': content.content_type,
            'output_file': str(md_file),
            'json_file': str(json_file)
        }

    def process_batch(self, urls: List[str], summarize: bool = True) -> List[dict]:
        """批量处理URL"""
        results = []

        total = len(urls)
        print(f"\n🚀 开始批量处理 {total} 个链接\n")

        for i, url in enumerate(urls, 1):
            print(f"\n{'#'*70}")
            print(f"进度: {i}/{total}")
            print(f"{'#'*70}")

            result = self.process_url(url, summarize)
            if result:
                result['index'] = i
                result['url'] = url
                result['status'] = 'success'
            else:
                result = {
                    'index': i,
                    'url': url,
                    'status': 'failed'
                }

            results.append(result)

        self._generate_batch_report(results)

        return results

    def _generate_batch_report(self, results: List[dict]):
        """生成批量处理报告"""
        report_lines = []

        report_lines.append("# 批量处理报告\n")

        total = len(results)
        success = sum(1 for r in results if r['status'] == 'success')
        failed = total - success

        report_lines.append(f"## 📊 处理统计\n")
        report_lines.append(f"- 总计: {total}")
        report_lines.append(f"- 成功: {success}")
        report_lines.append(f"- 失败: {failed}")
        report_lines.append(f"- 成功率: {success/total*100:.1f}%\n")

        if success > 0:
            report_lines.append(f"## ✅ 成功列表\n")
            for r in results:
                if r['status'] == 'success':
                    report_lines.append(f"### {r['index']}. {r['title']}\n")
                    report_lines.append(f"- 平台: {r['platform']}")
                    report_lines.append(f"- 类型: {r['content_type']}")
                    report_lines.append(f"- 文件: [{r['output_file']}]({r['output_file']})")
                    report_lines.append("")

        if failed > 0:
            report_lines.append(f"## ❌ 失败列表\n")
            for r in results:
                if r['status'] == 'failed':
                    report_lines.append(f"{r['index']}. {r['url']}")

        report_file = self.output_dir / "batch_report.md"
        report_file.write_text("\n".join(report_lines), encoding='utf-8')

        print(f"\n\n📊 批量处理报告: {report_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能视频图文内容提取与总结工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单个链接
  python main.py "https://v.douyin.com/xxx"

  # 批量处理
  python main.py urls.txt --batch

  # 不进行AI总结
  python main.py "https://v.douyin.com/xxx" --no-summary

  # 指定配置文件
  python main.py "https://v.douyin.com/xxx" --config config.json
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='URL或包含URL的文件路径'
    )

    parser.add_argument(
        '--config',
        '-c',
        help='配置文件路径'
    )

    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='不进行AI总结'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='批量处理模式（输入为文件）'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='输出目录'
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print("🎬 智能视频图文内容提取与总结工具")
    print("="*70)

    app = ContentExtractorApp(args.config)

    if args.output:
        app.output_dir = ensure_dir(Path(args.output))

    print(f"\n📁 输出目录: {app.output_dir}")
    print(f"🤖 AI总结: {'启用' if app.summarizer.enabled else '未启用'}")
    print(f"🎙️  语音转文字: {'启用' if app.transcriber.enabled else '未启用'}")

    if not args.input:
        print("\n💡 交互模式 - 输入URL或文件路径（输入 'q' 退出）\n")

        while True:
            try:
                user_input = input("请输入URL: ").strip()

                if user_input.lower() in ['q', 'quit', 'exit']:
                    print("\n👋 再见!")
                    break

                if not user_input:
                    continue

                app.process_url(user_input, summarize=not args.no_summary)

            except KeyboardInterrupt:
                print("\n\n👋 再见!")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")

    elif args.batch:
        urls = read_urls_from_file(args.input)
        print(f"\n📝 从文件读取到 {len(urls)} 个URL")
        app.process_batch(urls, summarize=not args.no_summary)

    else:
        app.process_url(args.input, summarize=not args.no_summary)

    print("\n✨ 完成!\n")


if __name__ == "__main__":
    main()
