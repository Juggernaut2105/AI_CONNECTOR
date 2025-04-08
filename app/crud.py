# app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas

# --- User CRUD ---
# We don't have user routes in this example, but good to have for assignee FK
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# You'd add create_user, etc. here if needed

# --- Task CRUD ---
def get_task(db: Session, task_id: int):
    # Use options to load relationships eagerly if needed frequently
    # from sqlalchemy.orm import joinedload
    # return db.query(models.Task).options(joinedload(models.Task.assignee), joinedload(models.Task.suggestions)).filter(models.Task.id == task_id).first()
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    # Basic pagination example (add filtering/sorting as needed)
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        assignee_id=task.assignee_id,
        status=task.status or "pending" # Use default if not provided
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task) # Get the ID and other generated values like created_at
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None # Task not found

    # Get the update data as a dict, excluding unset values
    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.add(db_task) # Add the existing object to the session to track changes
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        return False # Indicate task not found
    db.delete(db_task)
    db.commit()
    return True # Indicate success

# --- AI Suggestion CRUD ---
def create_ai_suggestion(db: Session, suggestion: schemas.AISuggestionCreate, task_id: int):
    db_suggestion = models.AISuggestion(
        **suggestion.model_dump(), # Unpack Pydantic model fields
        task_id=task_id
    )
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion