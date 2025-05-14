from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import DebateTopic, Argument

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
    new_argument = Argument(topic_id=topic_id, content=content)
    db.session.add(new_argument)
    db.session.commit()

    # Placeholder for AI evaluation logic
    flash('Your argument has been submitted for review.', 'info')
    return redirect(url_for('view_topic', topic_id=topic_id))
