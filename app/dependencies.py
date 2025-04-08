# app/dependencies.py

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Annotated # Preferred for Depends nowadays

from .database import SessionLocal, settings

# Dependency to get a DB session (moved from database.py for clarity)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple API Key / Bearer Token Authentication
async def verify_token(authorization: Annotated[str | None, Header()] = None):
    """Checks for a valid Bearer token in the Authorization header."""
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = parts[1]
    # Compare with the token from our settings
    if token != settings.api_auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # If token is valid, we don't need to return anything, just let the request proceed.
    # In a real app, you'd decode a JWT here and return the user identity.
    # For now, this dependency just acts as a gatekeeper.