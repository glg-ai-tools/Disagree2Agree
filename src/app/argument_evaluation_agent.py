import os
from dotenv import load_dotenv
import openai
import logging

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def evaluate_argument(content):
    """
    Evaluate the argument using OpenAI's API.
    Returns a dictionary with the evaluation status and feedback.
    """
    # Example system prompt for the AI
    system_prompt = (
        "You are an AI assistant tasked with evaluating debate arguments. "
        "Assess the argument for relevance, clarity, and adherence to debate principles. "
        "Provide a status (approved, needs_revision, rejected) and constructive feedback."
    )

    try:
        # Call OpenAI API (replace with your API key and model)
        logger.debug("Sending request to OpenAI API with content: %s", content)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )

        # Log the raw response
        logger.debug("Received response from OpenAI API: %s", response)

        # Parse the response (example structure, adjust as needed)
        ai_output = response['choices'][0]['message']['content']
        logger.debug("Parsed AI output: %s", ai_output)

        # Extract status and feedback from the AI output
        if "Status:" in ai_output:
            status_line, feedback = ai_output.split("\n", 1)
            status = status_line.replace("Status:", "").strip().lower()
        else:
            status = "needs_revision"
            feedback = "Unable to parse status. Please revise the argument."

        # Example: Parse the AI output into a dictionary
        evaluation = {
            "status": status,
            "feedback": feedback.strip()
        }

        return evaluation

    except openai.error.AuthenticationError as e:
        logger.error("Authentication error: %s", e)
        return {"status": "rejected", "feedback": "Authentication error. Please check your API key."}

    except Exception as e:
        logger.error("An error occurred: %s", e)
        return {"status": "rejected", "feedback": "An unexpected error occurred. Please try again later."}
