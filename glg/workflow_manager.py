# ==================== File: glg/workflow_manager.py ====================
"""
WorkflowManager: Manages workflows and agent execution.
"""

import json
from glg.agents.base_agent import BaseAgent

class WorkflowManager:
    def __init__(self, config_path):
        """
        Initialize the WorkflowManager with a configuration file.

        :param config_path: Path to the JSON configuration file defining workflows.
        """
        self.config_path = config_path
        self.workflows = self.load_workflows()

    def load_workflows(self):
        """
        Load workflows from the configuration file.

        :return: A dictionary of workflows.
        """
        with open(self.config_path, 'r') as file:
            return json.load(file)

    def execute_workflow(self, setting, agents):
        """
        Execute a workflow for a given setting.

        :param setting: The office setting (e.g., 'tv_scriptwriting').
        :param agents: A dictionary of agent instances.
        :return: The results of the workflow execution.
        """
        if setting not in self.workflows['settings']:
            raise ValueError(f"Setting '{setting}' not found in workflows.")

        workflow = self.workflows['settings'][setting]
        results = {}

        for agent_name in workflow:
            if agent_name not in agents:
                raise ValueError(f"Agent '{agent_name}' not found in provided agents.")

            agent = agents[agent_name]
            print(f"Executing {agent.name}...")
            results[agent_name] = agent.execute()

        return results

# Example usage:
# manager = WorkflowManager('config/teams.json')
# agents = {
#     'Anchor': AnchorAgent(),
#     'Luminary': LuminaryAgent(),
#     ...
# }
# results = manager.execute_workflow('tv_scriptwriting', agents)
