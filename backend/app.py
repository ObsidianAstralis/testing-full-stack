from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)  # Optional field
    priority = db.Column(db.Integer, nullable=False, default=1)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    due_date = db.Column(db.DateTime, nullable=True)  # Optional field

    def __repr__(self):
        return f"<Task {self.id} - {self.description}>"

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([
        {
            "id": t.id,
            "description": t.description,
            "category": t.category,
            "priority": t.priority,
            "completed": t.completed,
            "dateCreated": t.date_created.isoformat(),
            "dueDate": t.due_date.isoformat() if t.due_date else None
        } for t in tasks
    ])

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    new_task = Task(
        description=data["description"],
        category=data.get("category"),
        priority=data.get("priority", 1),  # Default to 1 if not provided
        due_date=datetime.fromisoformat(data["dueDate"]) if data.get("dueDate") else None
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({
        "id": new_task.id,
        "description": new_task.description,
        "category": new_task.category,
        "priority": new_task.priority,
        "completed": new_task.completed,
        "dateCreated": new_task.date_created.isoformat(),
        "dueDate": new_task.due_date.isoformat() if new_task.due_date else None
    })

@app.route("/tasks/<int:id>", methods=["PATCH"])
def toggle_task(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return jsonify({
        "id": task.id,
        "description": task.description,
        "category": task.category,
        "priority": task.priority,
        "completed": task.completed,
        "dateCreated": task.date_created.isoformat(),
        "dueDate": task.due_date.isoformat() if task.due_date else None
    })

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)