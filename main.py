import sys
import os
import argparse
import json
from glg.agents.receptionist import the_receptionist_agent
from pathlib import Path
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from glg.core import run_full_glg_workflow, API_KEY

def main():
    if not API_KEY:
        print("Error: OPENAI_API_KEY not set. Please export it before running.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Green Light Go CLI")
    parser.add_argument("--profile", "-p", default="default", help="Team profile to use (default: %(default)s)")
    parser.add_argument("--output", "-o", help="Optional path to save results (JSON or .md)")
    parser.add_argument("topic", nargs="*", help="Initial topic/idea to process")
    args = parser.parse_args()

    # Determine raw prompt
    if args.topic:
        topic = " ".join(args.topic).strip()
    else:
        print("Welcome to the Green Light Go AI Assistant!")
        topic = input("Please enter your initial idea or topic to start the process: ").strip()
        if not topic:
            print("No idea provided. Exiting.")
            return

    # Receptionist interpretations step
    transcript = f"Initial Topic: {topic}\n"
    while True:
        rec_out = the_receptionist_agent(transcript)
        print("\nReceptionist interpretations:")
        print(rec_out)
        choice = input("Select 1 or 2 to confirm interpretation, 3 to re-enter prompt, or 4 to exit: ").strip()
        if choice == '4':
            print("Exiting office. Goodbye.")
            return
        if choice == '3':
            topic = input("Please re-enter your topic: ").strip()
            transcript = f"Initial Topic: {topic}\n"
            continue
        if choice in ('1', '2'):
            # Extract chosen interpretation
            lines = rec_out.splitlines()
            for line in lines:
                if line.startswith(f"{choice}."):
                    # remove leading '1.' or '2.' and whitespace
                    topic = line.split('.', 1)[1].strip()
                    transcript = f"Initial Topic: {topic}\n"
                    break
            break

    # Execute workflow with chosen profile
    result = run_full_glg_workflow(topic, profile_name=args.profile)
    # Output structured JSON to console
    print(json.dumps(result, indent=2))
    # Archive the conversation transcript
    logs_dir = Path(__file__).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    transcript_file = logs_dir / f"transcript_{ts}.txt"
    with open(transcript_file, 'w') as f:
        f.write("".join(result.get('full_transcript', [])))
    print(f"Transcript archived to {transcript_file}")
    # Append run to history log for iterative learning
    history_file = logs_dir / 'history.json'
    try:
        history = json.load(open(history_file))
    except FileNotFoundError:
        history = []
    run_entry = {
        'timestamp': ts,
        'profile': args.profile,
        'initial_topic': result.get('initial_topic'),
        'ideas': result.get('ideas', []),
        'anchor_assessments': result.get('anchor_assessments', []),
        'navigator_decisions': result.get('navigator_decisions', []),
        'executive_summary': result.get('executive_summary', ''),
        'auditor_review': result.get('auditor_review', '')
    }
    history.append(run_entry)
    with open(history_file, 'w') as hf:
        json.dump(history, hf, indent=2)
    print(f"Run logged to {history_file}")
    # Optionally save to file
    if args.output:
        output_path = args.output
        ext = os.path.splitext(output_path)[1].lower()
        # Prepare markdown or JSON
        if ext in ('.md', '.markdown'):
            md = []
            md.append(f"# Green Light Go Result for '{result.get('initial_topic')}'")
            # Normalize anchor and navigator outputs to lists
            anchors = result.get('anchor_assessments', [])
            if isinstance(anchors, dict):
                anchors = [anchors]
            navs = result.get('navigator_decisions', [])
            if isinstance(navs, dict):
                navs = [navs]
            md.append("\n## Ideas\n")
            for idx, idea in enumerate(result.get('ideas', []), start=1):
                md.append(f"### Idea {idx}: {idea}\n")
                # Feasibility
                if idx <= len(anchors):
                    ass = anchors[idx-1]
                    md.append(f"- Feasibility Analysis: {ass.get('analysis','')}\n")
                    md.append(f"- Score: {ass.get('score','')}\n")
                # Recommendation
                if idx <= len(navs):
                    nav = navs[idx-1]
                    md.append(f"- Recommendation: {nav.get('recommendation','')}\n")
                    md.append(f"- Justification: {nav.get('justification','')}\n")
                    md.append(f"- Strategic Steps: {nav.get('strategic_steps','')}\n")
                md.append("")
            md.append("## Executive Summary\n")
            md.append(result.get('executive_summary','') + "\n")
            md.append("## Auditor Review\n")
            md.append(result.get('auditor_review','') + "\n")
            md.append("## Full Transcript\n")
            md.extend(result.get('full_transcript', []))
            with open(output_path, 'w') as f:
                f.write("\n".join(md))
        else:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
        print(f"Results saved to {output_path}")

if __name__ == '__main__':
    main()