import sqlite3
import os
from app.argument_evaluation_agent import evaluate_argument
from app.models import session, DebateTopic, DebateLog, DebateSummary
from agents.scribe import Scribe
from agents.auditor import Auditor

scribe = Scribe()
auditor = Auditor()

def initialize_database():
    conn = sqlite3.connect('debate_forum.db')
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS DebateTopic (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL
                      )''')

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

        choice = input("Enter your choice: ")

        if choice == '1':
            list_topics()
        elif choice == '2':
            add_topic()
        elif choice == '3':
            topic_id = int(input("Enter the topic ID: "))
            view_arguments(topic_id)
        elif choice == '4':
            topic_id = int(input("Enter the topic ID: "))
            submit_argument(topic_id)
        elif choice == '5':
            topic_id = int(input("Enter the topic ID: "))
            start_debate(topic_id)
        elif choice == '6':
            print("Exiting Debate Forum CLI. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
