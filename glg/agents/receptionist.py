# ==================== File: glg/agents/receptionist.py ====================
"""
The Gatekeeper agent: summarizes key decisions in bullet points.
"""

from glg.agents.base_agent import BaseAgent

class GatekeeperAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Gatekeeper",
            personality="The Gatekeeper is welcoming and resourceful, acting as the first point of contact and ensuring seamless communication."
        )

    def execute(self, visitor_log):
        """
        Execute the Gatekeeper agent's primary function: manage visitor interactions.

        :param visitor_log: A log of visitors and their inquiries.
        :return: A summary of visitor interactions and outcomes.
        """
        import os
        import openai
        from glg.utils.prompts import RECEPTIONIST_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = RECEPTIONIST_PROMPT.format(log=visitor_log)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Gatekeeper agent: {str(e)}"
