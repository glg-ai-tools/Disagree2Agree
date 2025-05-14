from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import DebateTopic, Argument, DebateLog, DebateSummary
from app.argument_evaluation_agent import evaluate_argument
from agents.scribe import Scribe
from agents.auditor import Auditor

scribe = Scribe()
auditor = Auditor()

@app.route('/')
def list_topics():
    topics = DebateTopic.query.all()
    return render_template('list_topics.html', topics=topics)

@app.route('/topic/<int:topic_id>')
def view_topic(topic_id):
    topic = DebateTopic.query.get_or_404(topic_id)
    arguments = Argument.query.filter_by(topic_id=topic_id, status='approved').all()
    return render_template('view_topic.html', topic=topic, arguments=arguments)

@app.route('/submit_topic', methods=['GET', 'POST'])
def submit_topic():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_topic = DebateTopic(title=title, description=description)
        db.session.add(new_topic)
        db.session.commit()
        flash('Debate topic submitted successfully!', 'success')
        return redirect(url_for('list_topics'))
    return render_template('submit_topic_form.html')

@app.route('/submit_argument/<int:topic_id>', methods=['POST'])
def submit_argument(topic_id):
    content = request.form['content']
    new_argument = Argument(topic_id=topic_id, content=content, status='pending_review')
    db.session.add(new_argument)
    db.session.commit()

    # Evaluate the argument using the AI agent
    evaluation = evaluate_argument(content)
    new_argument.status = evaluation['status']
    new_argument.ai_feedback_to_user = evaluation['feedback']
    db.session.commit()

    if evaluation['status'] == 'approved':
        flash('Your argument has been approved and is now visible.', 'success')
    elif evaluation['status'] == 'needs_revision':
        flash(f'Your argument needs revision: {evaluation["feedback"]}', 'warning')
    else:
        flash(f'Your argument was rejected: {evaluation["feedback"]}', 'danger')

    return redirect(url_for('view_topic', topic_id=topic_id))

@app.route('/start_debate/<int:topic_id>', methods=['GET', 'POST'])
def start_debate(topic_id):
    topic = DebateTopic.query.get(topic_id)
    if not topic:
        return "Topic not found", 404

    if request.method == 'POST':
        round_number = int(request.form['round_number'])
        alpha_argument = request.form['alpha_argument']
        beta_argument = request.form['beta_argument']
        moderator_notes = request.form['moderator_notes']

        scribe.record_round(round_number, alpha_argument, beta_argument, moderator_notes)

        continue_debate = request.form.get('continue_debate')
        if continue_debate != 'yes':
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
                db.session.add(debate_log)

            debate_summary = DebateSummary(topic_id=topic_id, summary=summary)
            db.session.add(debate_summary)
            db.session.commit()

            return render_template('debate_summary.html', summary=summary)

        return redirect(url_for('start_debate', topic_id=topic_id))

    return render_template('start_debate.html', topic=topic)
