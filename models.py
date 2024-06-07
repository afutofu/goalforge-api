from datetime import datetime, timezone
from database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=True)
    signup_method = db.Column(db.String(120), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def __repr__(self):
        return "<User %r>" % self.email


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    period = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
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
