# ==================== File: glg/agents/auditor.py ====================
"""
The Sentinel agent: reviews summaries for accuracy.
"""

from glg.agents.base_agent import BaseAgent


class SentinelAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Sentinel",
            personality="The Sentinel is vigilant and precise, safeguarding compliance and ensuring accuracy with unwavering focus."
        )

    def execute(self, conversation_transcript, executive_summary):
        """
        Execute the Sentinel agent's primary function: review summaries for accuracy.

        :param conversation_transcript: The transcript of the conversation.
        :param executive_summary: The executive summary to review.
        :return: The result of the review.
        """
        import os
        import openai
        from glg.utils.prompts import AUDITOR_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = AUDITOR_PROMPT.format(summary=executive_summary, transcript=conversation_transcript)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Sentinel agent: {str(e)}"
