# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager

from . import models, routes, crud, schemas # Import necessary modules from our app
from .database import engine, create_db_tables, SessionLocal, get_db, settings # Import db stuff
from .dependencies import verify_token # Import auth dependency if needed globally


# --- Database Initialization ---
# This function will attempt to create tables when the app starts.
# In production, you'd likely use migrations (like Alembic).
def initialize_database():
    print("Initializing database...")
    create_db_tables()
    # Optional: Create a default user if none exist (for testing FKs)
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, username="default_user")
        if not user:
            print("Creating default user 'default_user'...")
            default_user = schemas.UserCreate(username="default_user", email="user@example.com")
            # You would need a crud.create_user function for this
            # crud.create_user(db, default_user) # Assume you created this function in crud.py
            # For now, let's just create it directly if crud function isn't there
            user_model = models.User(username="default_user", email="user@example.com")
            db.add(user_model)
            db.commit()
            print("Default user created.")
        else:
            print("Default user already exists.")
    except Exception as e:
        print(f"Could not create default user: {e}") # Might fail if DB isn't ready yet
        db.rollback() # Rollback in case of error
    finally:
        db.close()


# --- Lifespan Management (for setup/teardown) ---
# Recommended way for startup/shutdown events in modern FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("--- Application Startup ---")
    initialize_database()
    print("--- Startup Complete ---")
    yield
    # Code to run on shutdown
    print("--- Application Shutdown ---")

# Create the FastAPI app instance with lifespan management
app = FastAPI(
    title="Task Management API",
    description="API for managing tasks with AI suggestions.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Include Routers ---
# Include the routes defined in routes.py
app.include_router(routes.router)

# --- Root Endpoint (Optional) ---
@app.get("/", tags=["Root"])
async def read_root():
    """A simple root endpoint to check if the API is running."""
    return {"message": "Welcome to the Task Management API!"}

# --- Health Check Endpoint (Good Practice) ---
# Unauthenticated endpoint to verify service health
@app.get("/health", tags=["Health"])
async def health_check():
    """Checks basic connectivity (e.g., database)."""
    try:
        # Try to get a db session as a basic check
        db = SessionLocal()
        db.connection() # Try establishing connection
        db.close()
        db_status = "connected"
    except Exception as e:
        print(f"Health check DB connection failed: {e}")
        db_status = "error"
        # Depending on severity, you might want to return 503 Service Unavailable
        # raise HTTPException(status_code=503, detail="Database connection failed")

    return {"status": "ok", "database": db_status, "auth_token_loaded": bool(settings.api_auth_token), "openai_key_file_set": bool(settings.openai_api_key_file)}

# --- Add other routers or global dependencies if needed ---
# Example: Add a simple user creation endpoint (not required by task spec)
# Needs a User model, schema, and CRUD function
# @app.post("/users/", response_model=schemas.User, tags=["Users"])
# def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_username(db, username=user.username)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
#     # You need to implement crud.create_user
#     # return crud.create_user(db=db, user=user)
#     # Quick hack for example:
#     user_model = models.User(**user.model_dump())
#     db.add(user_model)
#     db.commit()
#     db.refresh(user_model)
#     return user_model