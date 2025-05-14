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
    Base.metadata.create_all(engine)  # Create all tables defined in the models
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    # Create additional tables if needed (legacy support)
    cursor.execute('''CREATE TABLE IF NOT EXISTS Argument (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        status TEXT DEFAULT 'pending_review',
                        ai_feedback_to_user TEXT,
                        FOREIGN KEY (topic_id) REFERENCES DebateTopic (id)
                      )''')

    conn.commit()
    conn.close()

def list_topics():
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM DebateTopic')
    topics = cursor.fetchall()

    print("\nDebate Topics:")
    for topic in topics:
        print(f"{topic[0]}. {topic[1]} - {topic[2]}")

    conn.close()

def add_topic():
    title = input("Enter the title of the debate topic: ")
    description = input("Enter the description of the debate topic: ")

    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO DebateTopic (title, description) VALUES (?, ?)', (title, description))
    conn.commit()
    conn.close()

    print("Debate topic added successfully!")

def approve_topic():
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, status FROM DebateTopic WHERE status = "pending"')
    topics = cursor.fetchall()

    if not topics:
        print("No pending topics to approve.")
        return

    print("\nPending Topics:")
    for topic in topics:
        print(f"- {topic[1]} (ID: {topic[0]}, Status: {topic[2]})")

    topic_id = input("Enter the ID of the topic to approve: ").strip()
    cursor.execute('UPDATE DebateTopic SET status = "approved" WHERE id = ?', (topic_id,))
    conn.commit()
    conn.close()

    print("Topic approved successfully!")

def view_arguments(topic_id):
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Argument WHERE topic_id = ? AND status = "approved"', (topic_id,))
    arguments = cursor.fetchall()

    print("\nApproved Arguments:")
    for argument in arguments:
        print(f"- {argument[2]}")

    conn.close()

def submit_argument(topic_id):
    content = input("Enter your argument: ")

    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Argument (topic_id, content) VALUES (?, ?)', (topic_id, content))
    conn.commit()

    # Evaluate the argument
    evaluation = evaluate_argument(content)
    status = evaluation['status']
    feedback = evaluation['feedback']

    cursor.execute('UPDATE Argument SET status = ?, ai_feedback_to_user = ? WHERE id = ?',
                   (status, feedback, cursor.lastrowid))
    conn.commit()
    conn.close()

    if status == 'approved':
        print("Your argument has been approved and is now visible.")
    elif status == 'needs_revision':
        print(f"Your argument needs revision: {feedback}")
    else:
        print(f"Your argument was rejected: {feedback}")

def start_debate(topic_id):
    topic = session.query(DebateTopic).get(topic_id)
    if not topic:
        print("Topic not found.")
        return

    print(f"Starting debate on topic: {topic.title}")
    round_number = 1
    while True:
        alpha_argument = input(f"Round {round_number} - Alpha's argument: ")
        beta_argument = input(f"Round {round_number} - Beta's argument: ")
        moderator_notes = input("Moderator notes: ")

        scribe.record_round(round_number, alpha_argument, beta_argument, moderator_notes)

        continue_debate = input("Continue to next round? (yes/no): ").strip().lower()
        if continue_debate != 'yes':
            break

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

    print("Debate concluded. Summary:")
    print(summary)

def start_ai_debate(topic_id):
    topic = session.query(DebateTopic).get(topic_id)
    if not topic or topic.status != 'approved':
        print("Topic not found or not approved for debate.")
        return

    print(f"Starting AI debate on topic: {topic.title}")

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

    cursor.execute('SELECT id, title FROM DebateTopic')
    topics = cursor.fetchall()

    print("\nAvailable Topics:")
    for topic in topics:
        print(f"- {topic[1]} (ID: {topic[0]})")

    title = input("Enter the topic title: ").strip().lower()
    cursor.execute('SELECT id FROM DebateTopic WHERE LOWER(title) = ?', (title,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        print("Topic not found. Please try again.")
        return select_topic_by_title()

def main():
    initialize_database()

    while True:
        print("\nDebate Forum CLI")
        print("1. List Topics")
        print("2. Add Topic")
        print("3. View Arguments for a Topic")
        print("4. Submit an Argument")
        print("5. Start a Debate")
        print("6. Exit")
        print("7. Approve Topics")
        print("8. Start AI Debate")

        choice = input("Enter your choice: ")

        if choice == '1':
            list_topics()
        elif choice == '2':
            add_topic()
        elif choice == '3':
            topic_id = select_topic_by_title()
            view_arguments(topic_id)
        elif choice == '4':
            topic_id = select_topic_by_title()
            submit_argument(topic_id)
        elif choice == '5':
            topic_id = select_topic_by_title()
            start_debate(topic_id)
        elif choice == '6':
            print("Exiting Debate Forum CLI. Goodbye!")
            break
        elif choice == '7':
            approve_topic()
        elif choice == '8':
            topic_id = select_topic_by_title()
            start_ai_debate(topic_id)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
