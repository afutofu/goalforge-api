from datetime import datetime, timezone
from database import db
from config import cipher_suite, hash_value, hash_password


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    encrypted_email = db.Column(db.String(120), unique=True, nullable=False)
    encrypted_name = db.Column(db.String(120), nullable=False)
    hashed_email = db.Column(db.String(120), nullable=False)
    hashed_password = db.Column(db.String(120), nullable=True)
    tasks = db.relationship("Task", backref="user", lazy="subquery")
    categories = db.relationship("Category", backref="user", lazy="subquery")
    activity_logs = db.relationship("ActivityLog", backref="user", lazy="subquery")
    signup_method = db.Column(db.String(120), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def __init__(self, email, name, signup_method, password=None) -> None:
        self.encrypted_email = cipher_suite.encrypt(email.encode()).decode()
        self.encrypted_name = cipher_suite.encrypt(name.encode()).decode()
        self.hashed_email = hash_value(email)
        self.signup_method = signup_method

        if password:
            self.hashed_password = hash_password(password)

    def __repr__(self):
        return "<User %r>" % self.email


# Establish a many-to-many relationship between tasks and categories
task_categories = db.Table(
    "task_categories",
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), primary_key=True),
    db.Column(
        "category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True
    ),
)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    period = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    categories = db.relationship(
        "Category",
        backref="task",
        lazy="subquery",
        secondary=task_categories,
    )
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def __repr__(self):
        return "<Task %r>" % self.text

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "completed": self.completed,
            "period": self.period,
            "categories": [
                {
                    "id": category.id,
                    "name": category.name,
                    "color": category.color,
                    "createdAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                for category in self.categories
            ],
            "createdAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    color = db.Column(db.String(120), nullable=False)
    tasks = db.relationship(
        "Task", backref="category", lazy="subquery", secondary=task_categories
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "tasks": [
                {
                    "text": task.text,
                    "completed": task.completed,
                    "period": task.period,
                    "createdAt": task.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                for task in self.tasks
            ],
            "createdAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def __repr__(self):
        return "<ActivityLog %r>" % self.text

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "createdAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
