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

Available courses:
{course_block}

Pick the top 3 courses that best support the user's goal and preferences.
For each, briefly explain *why* it fits—especially considering past feedback.
"""
