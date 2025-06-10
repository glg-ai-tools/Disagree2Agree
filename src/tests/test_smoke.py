import subprocess
import sys

def test_smoke_cli_flow():
    # Run the CLI and execute a simple flow
    process = subprocess.Popen(
        [sys.executable, 'debate_cli.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Prepare inputs: add topic, show, approve, show, start debate, exit
    inputs = """
2
SmokeTestTopic
Smoke test description
1
3
1
4
1
5
"""
    try:
        out, err = process.communicate(inputs, timeout=60)
    except subprocess.TimeoutExpired:
        process.kill()
        out, err = process.communicate()

    # Check for key outputs in the CLI flow
    assert "SmokeTestTopic" in out
    assert "pending" in out
    assert "approved" in out or "Topic approved successfully" in out
    # Verify that the AI-driven debate started
    assert "Starting AI debate on topic" in out
