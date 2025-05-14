# ==================== File: glg/agents/finance_lead.py ====================
"""
The Finance Lead agent: summarizes budget, cost estimates, and ROI.
"""

# Name: Ledger
# Personality: The Ledger is strategic and resourceful, mastering financial insights and ensuring fiscal responsibility.

import os
import openai
from glg.utils.prompts import FINANCE_LEAD_PROMPT

def the_finance_lead_agent(transcript: str):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return "Error: OpenAI API key not found or client could not be initialized."
    openai.api_key = key
    prompt = FINANCE_LEAD_PROMPT.format(transcript=transcript)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during API call to Finance Lead agent: {e}"
