base_prompt = """
You are a helpful career learning assistant.

The user has the following goal:
- {goal}

Known skills:
- {known_skills}

Missing skills to improve:
- {missing_skills}

Learning preferences:
- Format: {format}
- Style: {style}
- Avoid styles: {avoid_styles}

Recent feedback history (structured data):
{feedback_log}

Once you have the course list, pick the 3 best options based on their goal, preferences, and feedback. Respond in this JSON format:

[
  {{
    "title": "...",
    "justification": "...",
    "course_id": "..."
  }},
  ...
]

For each recommendation, the field called 'justification' briefly explains *why* it fits—especially considering past feedback.

"""
