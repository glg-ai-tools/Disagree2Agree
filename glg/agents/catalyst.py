# ==================== File: glg/agents/catalyst.py ====================
"""
The Spark agent: ignites innovation and drives the team forward.
"""

# Name: Spark
# Personality: The Spark is dynamic and inspiring, igniting innovation and driving the team forward with boundless energy.

import os
import openai
from glg.utils.prompts import CATALYST_PROMPT


def the_catalyst_agent(red_light_idea):  # Changed parameter name
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return "Error: OpenAI API key not found or client could not be initialized."  # Consistent error message
    openai.api_key = key
    prompt = CATALYST_PROMPT.format(idea=red_light_idea)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during API call to catalyst agent: {str(e)}"


