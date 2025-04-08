# app/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas, ai_connector
from .dependencies import get_db, verify_token

# Create a router for tasks
# We add the authentication dependency to the router itself, so all routes in it are protected
router = APIRouter(
    prefix="/tasks",        # All routes here will start with /tasks
    tags=["Tasks"],         # Tag for Swagger UI grouping
    dependencies=[Depends(verify_token)] # Apply auth to all task routes
)

# POST /tasks - Create a new task
@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_new_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    Creates a new task in the system.
    Requires a valid Bearer token in the Authorization header.
    """
    # Optional: Check if assignee_id exists
    if task.assignee_id:
        db_user = crud.get_user(db, user_id=task.assignee_id)
        if not db_user:
            raise HTTPException(status_code=404, detail=f"Assignee user with id {task.assignee_id} not found")
            
    created_task = crud.create_task(db=db, task=task)
    # Eagerly load relationships for the response if not done in crud
    db.refresh(created_task, attribute_names=['assignee', 'suggestions']) 
    return created_task

# GET /tasks/{id} - Get a specific task
@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific task by its ID.
    Requires a valid Bearer token.
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # Ensure relationships are loaded if needed for the response model
    # db.refresh(db_task, attribute_names=['assignee', 'suggestions']) # Not strictly needed if Task schema is setup right
    return db_task

# PUT /tasks/{id} - Update an existing task
@router.put("/{task_id}", response_model=schemas.Task)
def update_existing_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """
    Updates an existing task by its ID.
    Allows partial updates (only fields provided are updated).
    Requires a valid Bearer token.
    """
    # Optional: Check if assignee_id exists if it's being updated
    if task_update.assignee_id is not None:
        db_user = crud.get_user(db, user_id=task_update.assignee_id)
        if not db_user:
            raise HTTPException(status_code=404, detail=f"Assignee user with id {task_update.assignee_id} not found")
            
    updated_task = crud.update_task(db=db, task_id=task_id, task_update=task_update)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Eagerly load relationships for the response
    db.refresh(updated_task, attribute_names=['assignee', 'suggestions']) 
    return updated_task

# DELETE /tasks/{id} - Delete a task
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(task_id: int, db: Session = Depends(get_db)):
    """
    Deletes a task by its ID.
    Requires a valid Bearer token.
    Returns 204 No Content on success.
    """
    success = crud.delete_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    # No content to return, FastAPI handles the 204 status

# POST /tasks/{id}/suggestions - Generate AI suggestion for a task
@router.post("/{task_id}/suggestions", response_model=schemas.AISuggestion, status_code=status.HTTP_201_CREATED)
def create_task_suggestion(task_id: int, db: Session = Depends(get_db)):
    """
    Generates an AI-powered suggestion for the specified task and saves it.
    Requires a valid Bearer token.
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Call our AI connector function
    suggestion_text = ai_connector.generate_ai_suggestion(
        task_title=db_task.title,
        task_description=db_task.description
    )

    if suggestion_text is None:
        raise HTTPException(status_code=500, detail="Failed to generate AI suggestion")

    # Create the suggestion schema object to pass to CRUD
    suggestion_create = schemas.AISuggestionCreate(suggestion_text=suggestion_text)
    
    # Save the suggestion to the database
    db_suggestion = crud.create_ai_suggestion(db=db, suggestion=suggestion_create, task_id=task_id)
    
    return db_suggestion

# Maybe add a GET /tasks/ endpoint later to list tasks
@router.get("/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of tasks with basic pagination.
    Requires a valid Bearer token.
    """
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    # Note: This might be slow if there are many tasks with many relationships.
    # Consider a simpler response model for lists or optimize queries.
    return tasks