"""
AI内容总结器
支持多种AI API（兼容OpenAI接口格式）
"""

import json
import requests
from typing import Optional, Dict
from extractors.base import ContentData


class Summarizer:
    """AI总结器"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化总结器

        Args:
            config: 配置字典，包含 api_key, base_url, model 等
        """
        if config is None:
            config = {}

        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', 'https://api.deepseek.com/v1')
        self.model = config.get('model', 'deepseek-chat')
        self.enabled = bool(self.api_key)

        if not self.enabled:
            print("⚠️  AI总结功能未启用（未配置API Key）")

    def summarize(self, content: ContentData) -> Dict[str, str]:
        """
        总结内容

        Args:
            content: 要总结的内容

        Returns:
            包含摘要、要点、关键词的字典
        """
        if not self.enabled:
            return {
                'summary': '未启用AI总结',
                'key_points': [],
                'keywords': [],
                'error': 'API key not configured'
            }

        try:
            content_text = self._prepare_content_text(content)
            result = self._call_ai_api(content_text)
            return result

        except Exception as e:
            print(f"❌ AI总结失败: {e}")
            return {
                'summary': f'总结失败: {str(e)}',
                'key_points': [],
                'keywords': [],
                'error': str(e)
            }

    def _prepare_content_text(self, content: ContentData) -> str:
        """准备要总结的内容文本"""
        parts = []

        parts.append(f"标题：{content.title}")
        parts.append(f"平台：{content.platform}")
        parts.append(f"类型：{content.content_type}")

        if content.author:
            parts.append(f"作者：{content.author}")

        stats = []
        if content.view_count > 0:
            stats.append(f"播放量{content.view_count:,}")
        if content.like_count > 0:
            stats.append(f"点赞{content.like_count:,}")
        if content.comment_count > 0:
            stats.append(f"评论{content.comment_count:,}")

        if stats:
            parts.append(f"数据：{' | '.join(stats)}")

        if content.description:
            parts.append(f"\n📄 描述：\n{content.description}")

        if content.text_content:
            parts.append(f"\n📝 正文内容：\n{content.text_content}")

        if content.subtitles:
            subtitle_text = ' '.join(content.subtitles)
            parts.append(f"\n💬 视频内容/字幕：\n{subtitle_text}")
            parts.append("\n⚠️ 重点：请重点分析上面的【视频内容/字幕】部分，这是视频的核心内容")

        if content.tags:
            parts.append(f"\n🏷️ 标签：{', '.join(content.tags)}")

        return "\n".join(parts)

    def _call_ai_api(self, content_text: str) -> Dict[str, str]:
        """调用AI API进行总结"""

        system_prompt = """你是一个专业的视频内容深度分析专家。你的任务是对视频内容进行**极其详细和充分**的分析总结。

**核心原则**：
1. 如果有【视频内容/字幕】，这是最重要的信息源，必须逐句分析
2. 总结要**详细充分**，不要简短概括，要展开说明
3. 每个要点都要**具体展开**，包含实例、数据、方法
4. 不要泛泛而谈，要深入细节

请按以下格式输出（使用JSON格式）：
{
  "summary": "详细的内容摘要（至少200字），要完整还原视频核心内容，包括：主题、背景、核心观点、关键结论。不要简短概括，要充分展开。",

  "key_points": [
    "要点1：[具体标题] - 详细说明（至少50字），包括：是什么、为什么重要、怎么做、有什么例子或数据支撑",
    "要点2：[具体标题] - 详细说明（至少50字）...",
    "要点3：...",
    "要点4：...",
    "要点5：...",
    "要点6：...",
    "要点7：...",
    "要点8：..."
  ],

  "detailed_analysis": {
    "background": "背景分析（至少100字）- 为什么会有这个内容？解决什么问题？针对什么场景？",
    "core_content": "核心内容详解（至少200字）- 主要讲了什么？有哪些具体方法、步骤、技巧？",
    "examples": "具体案例和数据（至少100字）- 视频中提到的具体例子、数据、对比、演示",
    "actionable": "可执行建议（至少100字）- 看完后能做什么？具体的行动步骤是什么？",
    "insights": "深度见解（至少100字）- 内容背后的深层逻辑、规律、趋势是什么？"
  },

  "keywords": [
    "关键词1", "关键词2", "关键词3", "关键词4", "关键词5",
    "关键词6", "关键词7", "关键词8", "关键词9", "关键词10"
  ],

  "audience": "目标受众详细分析（至少80字）- 谁最适合看？需要什么基础？能解决他们什么问题？",

  "value": "内容价值详细说明（至少100字）- 学完能获得什么具体能力？能解决什么实际问题？为什么值得学习？",

  "learning_path": "学习路径建议（至少80字）- 如何最有效地吸收这个内容？需要配合学习什么？",

  "content_type": "内容类型（教程/经验分享/技术评测/行业分析/案例拆解等）",

  "difficulty": "难度等级（入门/进阶/高级/专家）",

  "time_value": "时间价值评估 - 用一句话说明为什么值得花时间看这个视频"
}

**严格要求**：
1. ⚠️ **summary必须至少200字**，要完整、详细、充分
2. ⚠️ **每个key_point必须至少50字**，要展开说明，不要只写一句话
3. ⚠️ **detailed_analysis的每个字段都要详细填写**，不能简短
4. ⚠️ **提取8-10个关键要点**，不要只提取3-5个
5. ⚠️ **所有分析都要基于视频实际内容**，不要根据标题推测
6. ⚠️ **避免空洞的描述**，要具体、有细节、有例子

如果没有字幕，也要根据标题、描述、统计数据进行合理的详细分析。"""

        user_prompt = f"""请分析以下内容：

{content_text}

请按要求输出JSON格式的分析结果。"""

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.7
            }

            print(f"⏳ 正在调用AI进行总结...")
            print(f"   API: {self.base_url}")
            print(f"   模型: {self.model}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 429:
                error_msg = "API请求频率限制"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', error_msg)
                        error_code = error_data['error'].get('code', '')

                        if error_code == '1113' or '余额不足' in error_msg:
                            print(f"\n❌ 账户余额不足！")
                            print(f"   错误代码: {error_code}")
                            print(f"   错误信息: {error_msg}")
                            raise Exception(f"余额不足: {error_msg}")
                except Exception:
                    pass
                raise Exception(error_msg)

            response.raise_for_status()
            result = response.json()

            ai_content = result['choices'][0]['message']['content']

            try:
                ai_content = ai_content.strip()
                if ai_content.startswith('```json'):
                    ai_content = ai_content[7:]
                if ai_content.startswith('```'):
                    ai_content = ai_content[3:]
                if ai_content.endswith('```'):
                    ai_content = ai_content[:-3]

                ai_content = ai_content.strip()

                summary_data = json.loads(ai_content)
                print(f"✅ AI总结完成")

                return summary_data

            except json.JSONDecodeError:
                print(f"⚠️  AI返回非JSON格式，使用原始文本")
                return {
                    'summary': ai_content,
                    'key_points': [],
                    'keywords': [],
                    'raw_response': ai_content
                }

        except requests.exceptions.RequestException as e:
            print(f"❌ API请求失败: {e}")
            raise

        except Exception as e:
            print(f"❌ 总结过程出错: {e}")
            raise

    def format_summary_markdown(self, summary_data: Dict) -> str:
        """将总结数据格式化为Markdown"""
        lines = []

        lines.append("## 🤖 AI智能深度分析\n")

        if 'summary' in summary_data:
            lines.append("### 📋 内容摘要\n")
            lines.append(summary_data['summary'])
            lines.append("")

        if 'key_points' in summary_data and summary_data['key_points']:
            lines.append("### 🎯 关键要点详解\n")
            for i, point in enumerate(summary_data['key_points'], 1):
                lines.append(f"#### {i}. {point}\n")
            lines.append("")

        if 'detailed_analysis' in summary_data:
            lines.append("### 📊 深度分析\n")
            analysis = summary_data['detailed_analysis']

            if 'background' in analysis:
                lines.append("#### 📌 背景分析\n")
                lines.append(analysis['background'])
                lines.append("")

            if 'core_content' in analysis:
                lines.append("#### 💡 核心内容详解\n")
                lines.append(analysis['core_content'])
                lines.append("")

            if 'examples' in analysis:
                lines.append("#### 🔍 具体案例和数据\n")
                lines.append(analysis['examples'])
                lines.append("")

            if 'actionable' in analysis:
                lines.append("#### ✅ 可执行建议\n")
                lines.append(analysis['actionable'])
                lines.append("")

            if 'insights' in analysis:
                lines.append("#### 🧠 深度见解\n")
                lines.append(analysis['insights'])
                lines.append("")

        if 'keywords' in summary_data and summary_data['keywords']:
            lines.append("### 🔑 关键词\n")
            lines.append(", ".join(f"`{kw}`" for kw in summary_data['keywords']))
            lines.append("")

        if 'audience' in summary_data:
            lines.append("### 👥 目标受众\n")
            lines.append(summary_data['audience'])
            lines.append("")

        if 'value' in summary_data:
            lines.append("### 💡 内容价值\n")
            lines.append(summary_data['value'])
            lines.append("")

        if 'learning_path' in summary_data:
            lines.append("### 📚 学习路径建议\n")
            lines.append(summary_data['learning_path'])
            lines.append("")

        meta_info = []
        if 'content_type' in summary_data:
            meta_info.append(f"**内容类型**: {summary_data['content_type']}")
        if 'difficulty' in summary_data:
            meta_info.append(f"**难度等级**: {summary_data['difficulty']}")
        if 'time_value' in summary_data:
            meta_info.append(f"**时间价值**: {summary_data['time_value']}")

        if meta_info:
            lines.append("### 📌 元信息\n")
            lines.append(" | ".join(meta_info))
            lines.append("")

        return "\n".join(lines)
