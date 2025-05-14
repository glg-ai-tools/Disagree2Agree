# ==================== File: glg/agents/anchor.py ====================
"""
The Anchor agent: analyzes feasibility and scores ideas.
"""

from glg.agents.base_agent import BaseAgent


class AnchorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Anchor",
            personality="The Anchor is pragmatic and analytical, focusing on feasibility and scoring ideas with precision. It is methodical and grounded, ensuring every idea is evaluated thoroughly."
        )

    def execute(self, idea):
        """
        Execute the Anchor agent's primary function: analyze feasibility and score ideas.

        :param idea: The idea to analyze.
        :return: A dictionary containing the analysis and score.
        """
        import os
        import openai
        from glg.utils.prompts import ANCHOR_PROMPT

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return {
                "analysis": "Error: OpenAI API key not found or client could not be initialized.",
                "score": 0
            }

        openai.api_key = key
        prompt = ANCHOR_PROMPT.format(idea=idea)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content.strip()

            # Parsing logic for analysis and score
            analysis = "Could not parse analysis."  # Default
            score = 0  # Default

            score_marker = "Feasibility Score (0-100):"
            if score_marker in text:
                try:
                    score_text = text.split(score_marker, 1)[1].strip()
                    score_value_str = ''.join(filter(str.isdigit, score_text.split('\n')[0]))
                    if score_value_str:
                        score = int(score_value_str)
                        if not (0 <= score <= 100):
                            score = 0
                except ValueError:
                    score = 0

            if score_marker in text:
                analysis = text.split(score_marker, 1)[0].strip()
                analysis_marker = "Feasibility Analysis:"
                if analysis.startswith(analysis_marker):
                    analysis = analysis[len(analysis_marker):].strip()
            else:
                analysis = text
                analysis_marker = "Feasibility Analysis:"
                if analysis.startswith(analysis_marker):
                    analysis = analysis[len(analysis_marker):].strip()

            if not analysis.strip() or analysis == "Could not parse analysis.":
                analysis = f"Raw response: {text}"

            return {"analysis": analysis, "score": score}

        except Exception as e:
            return {
                "analysis": f"Error during API call to Anchor agent: {str(e)}",
                "score": 0
            }


