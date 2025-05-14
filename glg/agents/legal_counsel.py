# ==================== File: glg/agents/legal_counsel.py ====================
"""
The Shield agent: identifies compliance and contractual issues and suggests mitigations.
"""
# Name: Shield
# Personality: The Shield is protective and knowledgeable, ensuring every decision is legally sound and risk-free.

from glg.agents.base_agent import BaseAgent

class ShieldAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Shield",
            personality="The Shield is protective and knowledgeable, ensuring every decision is legally sound and risk-free."
        )

    def execute(self, legal_case):
        """
        Execute the Shield agent's primary function: provide legal analysis and advice.

        :param legal_case: The details of the legal case.
        :return: The legal analysis and advice.
        """
        import os
        import openai
        from glg.utils.prompts import LEGAL_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = LEGAL_PROMPT.format(case=legal_case)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Shield agent: {str(e)}"
