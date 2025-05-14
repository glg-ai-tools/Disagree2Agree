# ==================== File: glg/agents/office_jester.py ====================
"""
The Muse agent: adds light-hearted humor and creativity based on transcript.
"""

# Name: Muse
# Personality: The Muse is witty and lighthearted, boosting morale and fostering a positive atmosphere with humor and creativity.

from glg.agents.base_agent import BaseAgent

class MuseAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Muse",
            personality="The Muse is witty and lighthearted, boosting morale and fostering a positive atmosphere with humor and creativity."
        )

    def execute(self, transcript: str):
        """
        Execute the Muse agent's primary function: add humor and creativity based on a transcript.

        :param transcript: The transcript to analyze and enhance with humor.
        :return: A humorous and creative response.
        """
        import os
        import openai
        from glg.utils.prompts import OFFICE_JESTER_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = OFFICE_JESTER_PROMPT.format(transcript=transcript)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Muse agent: {str(e)}"
