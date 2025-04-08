# app/models.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base # Import Base from our database setup

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Add hashed_password in a real app

    # Relationship: A user can be assigned many tasks
    tasks = relationship("Task", back_populates="assignee")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending") # e.g., pending, in_progress, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Can be unassigned

    # Relationship: Link back to the User model
    assignee = relationship("User", back_populates="tasks")
    # Relationship: A task can have many AI suggestions
    suggestions = relationship("AISuggestion", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}')>"

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    suggestion_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # Relationship: Link back to the Task model
    task = relationship("Task", back_populates="suggestions")

    def __repr__(self):
        return f"<AISuggestion(id={self.id}, task_id={self.task_id})>"