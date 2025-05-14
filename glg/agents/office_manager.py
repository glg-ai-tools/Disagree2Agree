# ==================== File: glg/agents/office_manager.py ====================
"""
The Steward agent: coordinates resources and schedules action items.
"""

from glg.agents.base_agent import BaseAgent

class StewardAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Steward",
            personality="The Steward is organized and dependable, ensuring smooth day-to-day operations with efficiency and care."
        )

    def execute(self, office_tasks):
        """
        Execute the Steward agent's primary function: manage office operations.

        :param office_tasks: A list of office tasks to manage.
        :return: A report on task completion and efficiency.
        """
        import os
        import openai
        from glg.utils.prompts import OFFICE_MANAGER_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = OFFICE_MANAGER_PROMPT.format(tasks=office_tasks)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Steward agent: {str(e)}"
