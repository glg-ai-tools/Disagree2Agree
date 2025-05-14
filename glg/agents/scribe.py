# ==================== File: glg/agents/scribe.py ====================
"""
The Chronicle agent: synthesizes transcripts into executive summaries.
"""

from glg.agents.base_agent import BaseAgent


class ChronicleAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Chronicle",
            personality="The Chronicle is diligent and articulate, capturing and organizing information with precision and reliability."
        )

    def execute(self, meeting_notes):
        """
        Execute the Chronicle agent's primary function: document and organize information.

        :param meeting_notes: Notes from a meeting or discussion.
        :return: A well-organized summary of the notes.
        """
        import os
        import openai
        from glg.utils.prompts import SCRIBE_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = SCRIBE_PROMPT.format(notes=meeting_notes)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Chronicle agent: {str(e)}"
