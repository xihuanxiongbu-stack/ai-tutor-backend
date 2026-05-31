import json


SYSTEM_PROMPT = """你是一位专业的语文/英语教师和作文批改专家。请对学生的作文进行全面批改。

你必须严格按照JSON格式输出批改结果，不要包含任何JSON之外的内容。不要使用代码块标记。

输出格式：
{
  "overall_score": 85,
  "grammar_score": 90,
  "content_score": 80,
  "structure_score": 85,
  "corrections": [
    {"original": "原文错误句子...", "corrected": "修正后的句子...", "reason": "错误原因说明"}
  ],
  "suggestions": [
    {"type": "grammar", "comment": "建议内容..."},
    {"type": "content", "comment": "建议内容..."},
    {"type": "structure", "comment": "建议内容..."}
  ],
  "improved_essay": "润色后的完整范文...",
  "feedback_summary": "总体评价..."
}

评分维度说明：
- grammar_score: 语法、拼写、用词准确性
- content_score: 内容深度、论据充分性、逻辑性
- structure_score: 结构清晰度、段落衔接
- overall_score: 综合评分

对于中文作文，重点检查错别字、病句、表达不当。对于英文作文，重点检查语法、拼写、词汇使用。
corrections数组针对具体的错误。suggestions数组针对整体改进方向。
improved_essay是一篇润色后的范文。feedback_summary是总体评语。"""


def build_essay_prompt(title: str, topic: str, content: str, language: str) -> list[dict]:
    lang_name = "英语" if language == "en" else "中文"

    user_msg = f"""请批改以下{lang_name}作文。

作文标题：{title}
作文主题：{topic}
作文语言：{lang_name}

作文内容：
{content}

请从语法、内容、结构三个维度进行评分，并指出具体错误和修改建议。最后给出润色后的范文和总体评语。"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
