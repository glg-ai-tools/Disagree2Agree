# ==================== File: glg/agents/hr_rep.py ====================
"""
The HR Representative agent: assesses team morale and personnel concerns.
"""
# Name: Harmony
# Personality: Harmony is empathetic and collaborative, fostering unity and ensuring the well-being of the team.

from glg.agents.base_agent import BaseAgent

class HarmonyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Harmony",
            personality="Harmony is empathetic and collaborative, fostering unity and ensuring the well-being of the team."
        )

    def execute(self, team_feedback):
        """
        Execute the Harmony agent's primary function: analyze team feedback and provide recommendations.

        :param team_feedback: Feedback from the team.
        :return: Recommendations for improving team well-being.
        """
        import os
        import openai
        from glg.utils.prompts import HR_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = HR_PROMPT.format(feedback=team_feedback)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Harmony agent: {str(e)}"
