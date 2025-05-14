# ==================== File: glg/agents/luminary.py ====================
"""
The Luminary agent: generates creative ideas.
"""

from glg.agents.base_agent import BaseAgent


class LuminaryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Luminary",
            personality="The Luminary is visionary and insightful, providing strategic direction and inspiration. It is forward-thinking and innovative."
        )

    def execute(self, challenge):
        """
        Execute the Luminary agent's primary function: provide visionary insights.

        :param challenge: The challenge or topic to address.
        :return: The visionary insights provided by the agent.
        """
        import os
        import openai
        from glg.utils.prompts import LUMINARY_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = LUMINARY_PROMPT.format(challenge=challenge)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Luminary agent: {str(e)}"


