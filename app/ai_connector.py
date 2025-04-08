# app/ai_connector.py

import os
from openai import OpenAI, OpenAIError
from .database import settings # Get settings like the key file path

# --- OpenAI API Key Handling ---
def get_openai_api_key() -> str | None:
    """Reads the OpenAI API key from the file specified in settings."""
    key_file_path = settings.openai_api_key_file
    try:
        # Ensure the path is absolute or relative to the execution dir
        # If running from the project root, './openai_api_key.txt' works.
        # If running from app/, you might need '../openai_api_key.txt'
        # Using an absolute path derived from the script location can be safer.
        # script_dir = os.path.dirname(__file__)
        # key_file_path = os.path.join(script_dir, '..', settings.openai_api_key_file) # Example if script is in app/
        
        # Let's assume the path in .env is relative to the project root where you run uvicorn
        if not os.path.exists(key_file_path):
             print(f"Warning: API key file not found at {key_file_path}")
             return None
             
        with open(key_file_path, 'r') as f:
            api_key = f.read().strip()
            if not api_key:
                print(f"Warning: API key file '{key_file_path}' is empty.")
                return None
            return api_key
    except Exception as e:
        print(f"Error reading OpenAI API key from {key_file_path}: {e}")
        return None

# Initialize OpenAI client (only if key is available)
# It's often better to initialize the client *when needed* rather than globally,
# especially if the key might not be present at startup.
def get_openai_client():
    """Initializes and returns the OpenAI client if the key is available."""
    api_key = get_openai_api_key()
    if api_key:
        return OpenAI(api_key=api_key)
    else:
        print("OpenAI client could not be initialized: API key missing.")
        return None

# --- AI Suggestion Generation ---

# --- Option 1: Simple Placeholder (as requested initially) ---
# def generate_ai_suggestion_stub(task_title: str, task_description: str | None) -> str:
#     """A simple placeholder for AI suggestions."""
#     print(f"Generating stub suggestion for task: {task_title}")
#     # You could make this slightly more dynamic if you wanted
#     # suggestion = f"Consider optimizing the workflow for '{task_title}'."
#     suggestion = "Optimize this task for better efficiency." # Fixed text
#     return suggestion

# --- Option 2: Actual OpenAI Integration ---
def generate_ai_suggestion(task_title: str, task_description: str | None) -> str | None:
    """Generates a suggestion for a task using the OpenAI API."""
    client = get_openai_client()
    if not client:
        # Fallback to stub if OpenAI client isn't available
        print("OpenAI client not available, falling back to stub suggestion.")
        return "Optimize this task for better efficiency. (AI unavailable)" 
        # return None # Or just return None if no suggestion can be made

    prompt = f"Provide one short, actionable suggestion (less than 20 words) to improve or clarify the following task:\n"
    prompt += f"Title: {task_title}\n"
    if task_description:
        prompt += f"Description: {task_description}\n"
    prompt += "Suggestion:"

    print(f"Sending prompt to OpenAI for task: {task_title}")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or another suitable model
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing task suggestions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50, # Limit the length of the suggestion
            n=1,           # Get just one suggestion
            stop=None,     # Let the model decide when to stop
            temperature=0.7, # A bit creative but not too random
        )
        suggestion = response.choices[0].message.content.strip()
        print(f"Received suggestion from OpenAI: {suggestion}")
        return suggestion
    except OpenAIError as e:
        print(f"Error calling OpenAI API: {e}")
        # Fallback or error indication
        return "Could not generate AI suggestion due to an API error." 
        # return None
    except Exception as e:
        print(f"An unexpected error occurred during AI suggestion generation: {e}")
        return "An unexpected error occurred while generating the suggestion."
        # return None