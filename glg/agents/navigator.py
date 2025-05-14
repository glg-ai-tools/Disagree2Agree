# ==================== File: glg/agents/navigator.py ====================
"""
Yellow Light Compass agent: makes Go/No-Go recommendations.
"""
# Name: Compass
# Personality: The Compass is strategic and resourceful, guiding the team through challenges and opportunities with precision.

from glg.agents.base_agent import BaseAgent
import os
import openai
from glg.utils.prompts import NAVIGATOR_PROMPT


class CompassAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Compass",
            personality="The Compass is strategic and resourceful, guiding the team through challenges and opportunities with precision."
        )

    def execute(self, project_plan):
        """
        Execute the Compass agent's primary function: provide strategic guidance.

        :param project_plan: The project plan to evaluate.
        :return: Strategic recommendations for the project.
        """
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = NAVIGATOR_PROMPT.format(plan=project_plan)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Compass agent: {str(e)}"


