SYSTEM_PROMPT = """你是一位经验丰富的学科教师，负责根据指定要求出题。
你必须严格按照JSON格式输出题目，不要包含任何JSON之外的内容。不要使用代码块标记。

输出格式示例：
{
  "questions": [
    {
      "type": "选择题",
      "stem": "题目内容...",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "B",
      "explanation": "解析..."
    }
  ]
}

规则：
- 选择题必须提供4个选项
- 填空题的answer字段为数组
- 简答题额外提供scoring_points字段（数组）
- 题目难度要匹配，知识点要准确
- 题目内容使用中文"""


def build_question_prompt(subject: str, knowledge_point: str, difficulty: str, question_type: str, count: int, random_mode: bool = False) -> list[dict]:
    if random_mode:
        user_msg = f"""请生成{count}道{subject}的{question_type}。
该年级学科的知识点包括：{knowledge_point}

重要：每道题覆盖不同的知识点，从上面列表中随机选取，不要重复。
这样学生可以综合复习多个知识点。
难度：{difficulty}"""
    else:
        user_msg = f"""请生成{count}道{subject}的{question_type}。
知识点：{knowledge_point}
难度：{difficulty}"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
