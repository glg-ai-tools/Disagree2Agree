import sqlite3
import os
from app.argument_evaluation_agent import evaluate_argument
from app.models import session, DebateTopic, DebateLog, DebateSummary, Base, engine  # Import Base and engine for schema creation
from agents.scribe import Scribe
from agents.auditor import Auditor

scribe = Scribe()
auditor = Auditor()

# Update the initialize_database function to create the schema
def initialize_database():
    # Reset database file for a fresh start
    if os.path.exists('debate_forum.db'):
        os.remove('debate_forum.db')
    Base.metadata.create_all(engine)  # Create all tables defined in the models
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    # Create additional tables if needed (legacy support)
    cursor.execute('''CREATE TABLE IF NOT EXISTS argument (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        status TEXT DEFAULT 'pending_review',
                        ai_feedback_to_user TEXT,
                        FOREIGN KEY (topic_id) REFERENCES debate_topic (id)
                      )''')

    conn.commit()
    conn.close()

def receptionist(topic_id):
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM argument WHERE topic_id = ? AND status = ?',
        (topic_id, 'approved')
    )
    count = cursor.fetchone()[0]
    conn.close()
    if count < 2:
        print("Debate is not ready: insufficient approved arguments.")
        return False
    return True

def show_topics():
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, status FROM debate_topic')
    topics = cursor.fetchall()
    print("\nDebate Topics:")
    for tid, title, status in topics:
        print(f"{tid}. {title} - {status}")
        if status == 'approved':
            cursor.execute(
                'SELECT content FROM argument WHERE topic_id = ? AND status = "approved"',
                (tid,)
            )
            args = cursor.fetchall()
            for idx, (content,) in enumerate(args, start=1):
                print(f"    {idx}. {content}")
    conn.close()

def add_topic():
    title = input("Enter the title of the debate topic: ")
    description = input("Enter the description of the debate topic: ")

    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO debate_topic (title, description) VALUES (?, ?)', (title, description))
    conn.commit()
    conn.close()

    print("Debate topic added successfully!")

def approve_topic():
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, status FROM debate_topic WHERE status = "pending"')
    topics = cursor.fetchall()

    if not topics:
        print("No pending topics to approve.")
        return

    print("\nPending Topics:")
    for topic in topics:
        print(f"- {topic[1]} (ID: {topic[0]}, Status: {topic[2]})")

    topic_id = input("Enter the ID of the topic to approve: ").strip()
    cursor.execute('UPDATE debate_topic SET status = "approved" WHERE id = ?', (topic_id,))

    # Auto-generate arguments for the approved topic
    cursor.execute('SELECT title FROM debate_topic WHERE id = ?', (topic_id,))
    topic_title = cursor.fetchone()[0]

    alpha_resp = evaluate_argument(f"Alpha's stance on: {topic_title}")
    beta_resp = evaluate_argument(f"Provide a counter-argument to: {topic_title}")
    # Use AI feedback as the argument content
    alpha_argument = alpha_resp.get('feedback', 'Default Alpha argument: EV Vehicles are beneficial.')
    beta_argument = beta_resp.get('feedback', 'Default Beta argument: EV Vehicles are harmful.')

    cursor.execute('INSERT INTO argument (topic_id, content, status) VALUES (?, ?, ?)', (topic_id, alpha_argument, 'approved'))
    cursor.execute('INSERT INTO argument (topic_id, content, status) VALUES (?, ?, ?)', (topic_id, beta_argument, 'approved'))

    conn.commit()
    conn.close()

    print("Topic approved successfully and arguments auto-generated!")
    # Immediately start debate on this topic
    start_debate(int(topic_id))

def start_debate(topic_id):
    if not receptionist(topic_id):
        return
    # Fetch topic status and title directly from DB
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, status FROM debate_topic WHERE id = ?', (topic_id,))
    row = cursor.fetchone()
    conn.close()
    if not row or row[1] != 'approved':
        print("Topic not found or not approved for debate.")
        return
    topic_title = row[0]

    print(f"Starting AI debate on topic: {topic_title}")

    # Generate arguments for Alpha and Beta
    alpha_arguments = [f"Alpha Argument {i+1}" for i in range(5)]  # Placeholder for AI-generated arguments
    beta_arguments = [f"Beta Argument {i+1}" for i in range(5)]  # Placeholder for AI-generated counterarguments

    round_number = 1
    for alpha_arg, beta_arg in zip(alpha_arguments, beta_arguments):
        print(f"Round {round_number}:")
        print(f"Alpha: {alpha_arg}")
        print(f"Beta: {beta_arg}")

        # Record the round
        scribe.record_round(round_number, alpha_arg, beta_arg, moderator_notes="Auto-generated round")

        round_number += 1

    logs = scribe.get_logs()
    summary = auditor.summarize_debate(logs)

    # Save logs and summary to the database
    for log in logs:
        debate_log = DebateLog(
            topic_id=topic_id,
            round_number=log['round_number'],
            alpha_argument=log['alpha_argument'],
            beta_argument=log['beta_argument'],
            moderator_notes=log['moderator_notes']
        )
        session.add(debate_log)

    debate_summary = DebateSummary(topic_id=topic_id, summary=summary)
    session.add(debate_summary)
    session.commit()

    print("AI Debate concluded. Summary:")
    print(summary)

def select_topic_by_title():
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, title FROM debate_topic')
    topics = cursor.fetchall()

    print("\nAvailable Topics:")
    for topic in topics:
        print(f"- {topic[1]} (ID: {topic[0]})")

    # Always prompt user for topic selection
    # (Remove auto-select to correctly consume test input)
    while True:
        user_input = input("Enter the topic title or ID: ").strip()

        if user_input.isdigit():
            cursor.execute('SELECT id FROM debate_topic WHERE id = ?', (int(user_input),))
        else:
            cursor.execute('SELECT id FROM debate_topic WHERE LOWER(title) = ?', (user_input.lower(),))

        result = cursor.fetchone()

        if result:
            conn.close()
            return result[0]
        else:
            print("Topic not found. Please try again.")

def main():
    initialize_database()

    while True:
        print("\nDebate Forum CLI")
        print("1. Show Topics and Arguments")
        print("2. Add Topic")
        print("3. Approve Topics")
        print("4. Start Debate")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()
        # Skip empty inputs (e.g., leading newlines in piped input)
        if not choice:
            continue

        if choice == '1':
            show_topics()
        elif choice == '2':
            add_topic()
        elif choice == '3':
            approve_topic()
        elif choice == '4':
            topic_id = select_topic_by_title()
            start_debate(topic_id)
        elif choice == '5':
            print("Exiting Debate Forum CLI. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
