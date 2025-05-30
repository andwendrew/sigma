from fastapi import FastAPI, Request, Form
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from calendar_bot.agent.agent import Agent
from typing import List, Dict
import json

app = FastAPI()

# Initialize the agent
agent = Agent()

# Simple HTML form for user input
def get_form_html():
    # Convert conversation history to HTML
    history_html = ""
    for msg in agent.conversation_history if hasattr(agent, 'conversation_history') else []:
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
                .event-link {{ color: #0066cc; text-decoration: none; }}
                .event-link:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h2>Calendar Agent Conversation</h2>
            <div class="conversation">
                {history_html}
            </div>
            <form action="/chat" method="post">
                <input type="text" name="message" required placeholder="Type your message..." />
                <button type="submit">Send</button>
            </form>
            <form action="/clear" method="post" style="display: inline;">
                <button type="submit" class="clear-btn">Clear Conversation</button>
            </form>
        </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def root():
    return get_form_html()

@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    try:
        form = await request.form()
        message = form.get("message")
        if not message:
            return HTMLResponse("<p>Error: No message provided</p><a href='/'>Back</a>")
        
        print(f"Received message: {message}")  # Log the message
        
        # Process the message using our agent
        response = agent.process_message(message)
        print(f"Agent response: {response}")  # Log the response
        
        # Update conversation history
        if not hasattr(agent, 'conversation_history'):
            agent.conversation_history = []
        agent.conversation_history.append({
            'user': message,
            'assistant': response
        })
        
        return HTMLResponse(get_form_html())
    except Exception as e:
        print(f"Error processing request: {str(e)}")  # Log any errors
        return HTMLResponse(f"<p>Error: {str(e)}</p><a href='/'>Back</a>")

@app.post("/clear", response_class=HTMLResponse)
async def clear_conversation():
    if hasattr(agent, 'conversation_history'):
        agent.conversation_history = []
    return HTMLResponse(get_form_html())

# Add a catch-all route for 404s
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return HTMLResponse("<p>Page not found</p><a href='/'>Back to Home</a>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
