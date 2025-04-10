# Task Management API with AI Suggestions

A RESTful API built with FastAPI for managing tasks, integrated with OpenAI to provide AI-powered suggestions for tasks. Uses PostgreSQL for data storage and basic token authentication.

---

## Features

*   **Task Management:** CRUD operations (Create, Read, Update, Delete) for tasks.
*   **Database:** Uses PostgreSQL with SQLAlchemy ORM for data persistence.
*   **AI Integration:** Generates task suggestions using the OpenAI API (specifically, the Chat Completions endpoint with a model like `gpt-3.5-turbo`).
*   **Suggestion Storage:** Saves generated AI suggestions linked to their respective tasks in the database.
*   **Authentication:** Basic security using a static Bearer token in the `Authorization` header.
*   **Async:** Built with FastAPI, leveraging Python's `async` capabilities.
*   **API Docs:** Automatic interactive API documentation via Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## Technology Stack

*   **Backend Framework:** FastAPI
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy
*   **PG Driver:** psycopg2-binary
*   **Server:** Uvicorn
*   **Data Validation:** Pydantic
*   **AI:** OpenAI Python Library (`openai`)
*   **Configuration:** python-dotenv, pydantic-settings
*   **Language:** Python 3.8+

---

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd task_manager_api
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up PostgreSQL:**
    *   Ensure you have PostgreSQL installed and running.
    *   Create a database (e.g., `taskdb`).
    *   Create a user and grant privileges on the database (e.g., `user` with `password`).

5.  **Configure Environment Variables:**
    *   Create a file named `.env` in the project root directory (`task_manager_api/`).
    *   Copy the contents from the example below and **replace the placeholders** with your actual database connection details and a chosen secret token.

    ```dotenv
    # .env - DO NOT COMMIT THIS FILE IF IT CONTAINS REAL SECRETS!

    # Replace with your actual PostgreSQL connection string
    # Format: postgresql://username:password@host:port/database_name
    DATABASE_URL=postgresql://user:password@localhost:5432/taskdb

    # Choose a secure secret token for API authentication
    API_AUTH_TOKEN=supersecrettoken

    # Path to the file containing the OpenAI API key (relative to project root)
    OPENAI_API_KEY_FILE=./openai_api_key.txt
    ```

6.  **Set up OpenAI API Key:**
    *   Create a file named `openai_api_key.txt` in the project root directory (`task_manager_api/`).
    *   Paste **only** your OpenAI API key into this file. Nothing else!
    *   **IMPORTANT:** Ensure both `.env` and `openai_api_key.txt` are listed in your `.gitignore` file to prevent accidentally committing secrets.

---

## Running the Application

1.  **Start the Server:**
    From the project root directory (`task_manager_api/`), run:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `--reload`: Enables auto-reloading for development. Remove this in production.
    *   `--host 0.0.0.0`: Makes the API accessible on your network. Use `127.0.0.1` for local access only.

2.  **Access the API:**
    The API will be available at `http://localhost:8000`.

3.  **Database Initialization:**
    The application attempts to create the necessary database tables on startup (defined in `app/models.py`). For production environments, consider using a migration tool like Alembic.

---

## API Documentation

Interactive API documentation is automatically generated by FastAPI:

*   **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

These interfaces allow you to explore and test the API endpoints directly from your browser.

---

## API Endpoints Overview

*   `GET /`: Root endpoint.
*   `GET /health`: Health check endpoint.
*   `POST /tasks/`: Create a new task.
*   `GET /tasks/`: List tasks (basic pagination).
*   `GET /tasks/{task_id}`: Retrieve a specific task.
*   `PUT /tasks/{task_id}`: Update a specific task (partial updates allowed).
*   `DELETE /tasks/{task_id}`: Delete a specific task.
*   `POST /tasks/{task_id}/suggestions`: Generate and save an AI suggestion for a task.

**Authentication:** All `/tasks/*` endpoints require a Bearer token in the `Authorization` header. Use the token defined in your `.env` file (`API_AUTH_TOKEN`).


---

## Example Usage (cURL)

**(Replace `supersecrettoken` with your actual token from `.env`)**

1.  **Create a Task (assuming user with ID 1 exists):**
    ```bash
    curl -X POST "http://localhost:8000/tasks/" \
    -H "Authorization: Bearer supersecrettoken" \
    -H "Content-Type: application/json" \
    -d '{"title": "Setup Project Readme", "description": "Create a comprehensive README file", "assignee_id": 1}'
    ```
    *(Note the returned task ID, e.g., `1`)*

2.  **Get Task 1:**
    ```bash
    curl -X GET "http://localhost:8000/tasks/1" \
    -H "Authorization: Bearer supersecrettoken"
    ```

3.  **Update Task 1:**
    ```bash
    curl -X PUT "http://localhost:8000/tasks/1" \
    -H "Authorization: Bearer supersecrettoken" \
    -H "Content-Type: application/json" \
    -d '{"status": "in_progress", "description": "Create a comprehensive README file with setup instructions."}'
    ```

4.  **Generate AI Suggestion for Task 1:**
    ```bash
    curl -X POST "http://localhost:8000/tasks/1/suggestions" \
    -H "Authorization: Bearer supersecrettoken"
    ```
    *(This will call OpenAI and save the suggestion)*

5.  **Get Task 1 again (to see the suggestion):**
    ```bash
    curl -X GET "http://localhost:8000/tasks/1" \
    -H "Authorization: Bearer supersecrettoken"
    ```

6.  **Delete Task 1:**
    ```bash
    curl -X DELETE "http://localhost:8000/tasks/1" \
    -H "Authorization: Bearer supersecrettoken"
    ```

---

## Future Improvements / Notes

*   **Authentication:** Implement more robust authentication (e.g., JWT with user logins).
*   **User Management:** Add endpoints for managing users (CRUD).
*   **Error Handling:** Enhance global error handling and provide more specific error responses.
*   **Testing:** Add unit and integration tests.
*   **Migrations:** Integrate Alembic for database schema migrations.
*   **Pagination/Filtering:** Implement more advanced pagination, filtering, and sorting for the task list endpoint.
*   **Rate Limiting:** Add rate limiting to protect the API and AI usage.
*   **Configuration:** Improve configuration management for different environments (dev, staging, prod).

---
