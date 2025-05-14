# ==================== File: glg/agents/base_agent.py ====================
"""
BaseAgent: A standardized base class for all agents.
"""

class BaseAgent:
    def __init__(self, name, personality):
        """
        Initialize the agent with a name and personality.

        :param name: The name of the agent.
        :param personality: A brief description of the agent's personality.
        """
        self.name = name
        self.personality = personality

    def execute(self, *args, **kwargs):
        """
        Execute the agent's primary function. This method should be overridden by subclasses.

        :param args: Positional arguments for the agent's function.
        :param kwargs: Keyword arguments for the agent's function.
        :return: The result of the agent's execution.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")

    def __repr__(self):
        """
        Return a string representation of the agent.

        :return: A string describing the agent.
        """
        return f"{self.name}: {self.personality}"
