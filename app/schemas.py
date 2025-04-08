# app/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    # Add password field here in a real app
    pass

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True) # Allows creating schema from ORM model

# --- AI Suggestion Schemas ---
class AISuggestionBase(BaseModel):
    suggestion_text: str

class AISuggestionCreate(AISuggestionBase):
    pass # No extra fields needed for creation usually

class AISuggestion(AISuggestionBase):
    id: int
    task_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"

class TaskCreate(TaskBase):
    # We only need the ID of the assignee when creating
    assignee_id: Optional[int] = None

class TaskUpdate(TaskBase):
    # Allow updating all base fields, optionally
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    assignee_id: Optional[int] = None
    # Include assignee details and suggestions in the response model
    assignee: Optional[User] = None
    suggestions: List[AISuggestion] = []

    model_config = ConfigDict(from_attributes=True) # Enable ORM mode