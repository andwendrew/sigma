from fastapi import FastAPI, Request, Form
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from calendar_bot.agent import process_command
from calendar_bot.llm.mistral_local import get_mistral_llm
from typing import List, Dict
import json

app = FastAPI()

# Store conversation history in memory (in production, you'd want to use a database)
conversation_history: List[Dict[str, str]] = []

# Simple HTML form for user input
def get_form_html():
    # Convert conversation history to HTML
    history_html = ""
    for msg in conversation_history:
        history_html += f"""
        <div style="margin: 10px 0; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <strong>You:</strong> {msg['user']}<br>
            <strong>Assistant:</strong> {msg['assistant']}
        </div>
        """
    
    return f"""
    <html>
        <head>
            <title>Calendar Agent</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                form {{ margin: 20px 0; }}
                input[type="text"] {{ padding: 8px; width: 300px; }}
                button {{ padding: 8px 16px; }}
                .conversation {{ margin: 20px 0; }}
                .clear-btn {{ margin-left: 10px; }}
            </style>
        </head>
        <body>
            <h2>Calendar Agent Conversation</h2>
            <div class="conversation">
                {history_html}
            </div>
            <form action="/create_event" method="post">
                <input type="text" name="command" required placeholder="Enter your command..." />
                <button type="submit">Send</button>
            </form>
            <form action="/clear" method="post" style="display: inline;">
                <button type="submit" class="clear-btn">Clear Conversation</button>
            </form>
        </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
def root():
    return get_form_html()

class CommandRequest(BaseModel):
    command: str = Field(..., description="The command to process")

@app.post("/create_event", response_class=HTMLResponse)
async def create_event(request: Request):
    try:
        form = await request.form()
        command = form.get("command")
        if not command:
            return HTMLResponse("<p>Error: No command provided</p><a href='/'>Back</a>")
        
        print(f"Received command: {command}")  # Log the command
        
        # Add user message to history
        conversation_history.append({"user": command})
        
        # Get response from LLM with conversation history
        result = process_command(command, conversation_history[:-1])  # Pass all history except current message
        print(f"LLM response: {result}")  # Log the response
        
        # Add assistant response to history
        conversation_history[-1]["assistant"] = result
        
        return HTMLResponse(get_form_html())
    except Exception as e:
        print(f"Error processing request: {str(e)}")  # Log any errors
        return HTMLResponse(f"<p>Error: {str(e)}</p><a href='/'>Back</a>")

@app.post("/clear", response_class=HTMLResponse)
async def clear_conversation():
    global conversation_history
    conversation_history = []
    return HTMLResponse(get_form_html())

# Add a catch-all route for 404s
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return HTMLResponse("<p>Page not found</p><a href='/'>Back to Home</a>", status_code=404)
