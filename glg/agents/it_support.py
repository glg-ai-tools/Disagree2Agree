# ==================== File: glg/agents/it_support.py ====================
"""
The IT Support agent: identifies technical blockers and proposes system solutions.
"""

from glg.agents.base_agent import BaseAgent

class NexusAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Nexus",
            personality="The Nexus is tech-savvy and dependable, seamlessly connecting the team to solutions and ensuring smooth operations."
        )

    def execute(self, issue_description):
        """
        Execute the Nexus agent's primary function: resolve technical issues.

        :param issue_description: A description of the technical issue.
        :return: The resolution or troubleshooting steps.
        """
        import os
        import openai
        from glg.utils.prompts import IT_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return "Error: OpenAI API key not found or client could not be initialized."

        openai.api_key = key
        prompt = IT_PROMPT.format(issue=issue_description)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during API call to Nexus agent: {str(e)}"
