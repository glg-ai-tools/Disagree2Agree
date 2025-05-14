import os
import argparse
import json
import importlib
from dotenv import load_dotenv

load_dotenv()  # load from .env if exists

API_KEY = os.getenv("OPENAI_API_KEY")

def load_team_profile(name='default'):
    path = os.path.join(os.path.dirname(__file__), '..', 'config', 'teams.json')
    try:
        data = json.load(open(path))
        profile = data.get(name)
        # Support either a list of agents or a dict with 'agents'
        if isinstance(profile, list):
            return profile
        if isinstance(profile, dict) and 'agents' in profile:
            return profile['agents']
        return []
    except Exception:
        return []

def run_full_glg_workflow(initial_topic: str, profile_name: str = 'default'):
    """
    Runs the full Green Light Go workflow for a given initial topic.
    """
    print(f"\n🚀 Starting Green Light Go workflow for topic: \"{initial_topic}\"")
    # Domain compliance guardrail
    domains_cfg = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'config', 'domains.json')))
    allowed = domains_cfg.get('allowed_domains', [])
    if not any(d in initial_topic.lower() for d in allowed):
        print(f"❌ No-Go: Topic '{initial_topic}' outside allowed domains. Allowed: {allowed}")
        # Return full context structure to avoid missing keys
        return {
            'initial_topic': initial_topic,
            'ideas': [],
            'anchor_assessments': [],
            'navigator_decisions': [],
            'red_light_ideas': [],
            'green_light_ideas': [],
            'yellow_light_ideas': [],
            'full_transcript': [f"Initial Topic: {initial_topic} (rejected - out of domain)\n"],
            'go_decision': 'No-Go',
            'reason': 'Topic outside allowed domains'
        }
    conversation_transcript = [f"Initial Topic: {initial_topic}\n"]
    # Load dynamic team sequence
    team = load_team_profile(profile_name)
    context = {
        'initial_topic': initial_topic,
        'ideas': [],
        'anchor_assessments': [],
        'navigator_decisions': [],
        'red_light_ideas': [],
        'green_light_ideas': [],
        'yellow_light_ideas': [],
        'full_transcript': conversation_transcript
    }

    # Execute each agent in sequence
    for agent_cfg in team:
        name = agent_cfg.get('name')
        mod_path, func_name = agent_cfg['path'].rsplit('.', 1)
        module = importlib.import_module(mod_path)
        func = getattr(module, func_name)
        args = []
        # prepare args from context
        for arg in agent_cfg.get('args', []):
            args.append(context.get(arg) or context.get(arg + 's') or context.get('initial_topic'))
        result = func(*args, **agent_cfg.get('kwargs', {}))
        # handle storing results
        if name == 'luminary':
            context['ideas'] = result
            # add to transcript
            conversation_transcript.append("Luminary Ideas:\n" + "\n".join(f"• {i}" for i in result))
        elif name == 'anchor':
            context['anchor_assessments'] = result
            # add to transcript
            conversation_transcript.append(
                f"Anchor Analysis:\n{result.get('analysis')}\nFeasibility Score (0-100): {result.get('score')}"
            )
        elif name == 'navigator':
            context['navigator_decisions'] = result
            # add to transcript
            conversation_transcript.append("Navigator Recommendations:\n" + "\n".join(f"• {d}" for d in result))
        elif name == 'catalyst':
            # only run on red_light
            context['red_light_ideas'] = result
            # add to transcript
            conversation_transcript.append("Catalyst Ideas:\n" + "\n".join(f"• {i}" for i in result))
        elif name == 'scribe':
            context['executive_summary'] = result
            # add to transcript
            conversation_transcript.append("Executive Summary:\n" + result)
        elif name == 'auditor':
            context['auditor_review'] = result
            # add to transcript
            conversation_transcript.append("Auditor Review:\n" + result)
    return context

def main():
    if not API_KEY:
        print("Error: OPENAI_API_KEY not set. Please export it before running.")
        return

    # Prompt the user for their idea interactively
    print("Welcome to the Green Light Go AI Assistant!")
    initial_idea_input = input("Please enter your initial idea or topic to start the process: ").strip()

    if not initial_idea_input:
        print("No idea provided. Exiting.")
        return

    result = run_full_glg_workflow(initial_idea_input)
    # print out results
    print("\nResult:", result)

if __name__ == '__main__':
    main()

