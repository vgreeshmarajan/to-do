import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reminder = db.Column(db.DateTime)
    priority = db.Column(db.String(10), default='medium')  # high, medium, low
    category = db.Column(db.String(20), default='today')  # today, tomorrow, later

# Initialize database
with app.app_context():
    # Drop existing tables if they exist
    db.drop_all()
    # Create new tables
    db.create_all()
    # Add some sample data
    sample_todos = [
        Todo(title="Complete project report", 
             description="Finish writing and reviewing the project report", 
             priority="high",
             category="today"),
        Todo(title="Team meeting", 
             description="Prepare for tomorrow's team meeting", 
             priority="medium",
             category="tomorrow"),
        Todo(title="Send email updates", 
             description="Send weekly update emails to stakeholders", 
             priority="low",
             category="later")
    ]
    db.session.add_all(sample_todos)
    db.session.commit()

@app.route('/')
def index():
    # Get all todos ordered by category, priority, and creation date
    todos = Todo.query.order_by(
        case(
            (Todo.category == 'today', 1),
            (Todo.category == 'tomorrow', 2),
            (Todo.category == 'later', 3)
        ),
        Todo.priority.desc(),
        Todo.created_at.desc()
    ).all()
    
    # Calculate statistics
    total_todos = len(todos)
    completed_todos = len([t for t in todos if t.completed])
    pending_todos = total_todos - completed_todos
    
    # Calculate percentages
    if total_todos > 0:
        completed_percent = (completed_todos / total_todos) * 100
        pending_percent = (pending_todos / total_todos) * 100
    else:
        completed_percent = 0
        pending_percent = 0
    
    return render_template('index.html', 
                         todos=todos,
                         completed_percent=completed_percent,
                         pending_percent=pending_percent,
                         total_todos=total_todos)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority', 'medium')
    category = request.form.get('category', 'today')
    reminder = request.form.get('reminder')
    
    if not title:
        flash('Title is required!', 'error')
        return redirect(url_for('index'))
    
    todo = Todo(
        title=title,
        description=description,
        priority=priority,
        category=category,
        reminder=reminder and datetime.strptime(reminder, '%Y-%m-%dT%H:%M')
    )
    db.session.add(todo)
    db.session.commit()
    flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

def check_reminders():
    while True:
        with app.app_context():
            now = datetime.utcnow()
            # Check for todos with reminders in the next 1 hour that haven't been completed
            upcoming_reminders = Todo.query.filter(
                Todo.reminder >= now,
                Todo.reminder <= now + timedelta(hours=1),
                Todo.completed == False
            ).all()
            
            for todo in upcoming_reminders:
                flash(f'Reminder: {todo.title} is due at {todo.reminder.strftime("%Y-%m-%d %H:%M")}', 'info')
        time.sleep(60)  # Check every minute

@app.route('/update_category', methods=['POST'])
def update_category():
    todo_id = request.form.get('todo_id')
    category = request.form.get('category')
    
    todo = Todo.query.get_or_404(todo_id)
    todo.category = category
    db.session.commit()
    
    return {'success': True}
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Start reminder checking thread
        reminder_thread = threading.Thread(target=check_reminders, daemon=True)
        reminder_thread.start()
    
    app.run(host='127.0.0.1', port=5001, debug=True)
