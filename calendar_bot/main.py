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
        <div class="message">
            <div class="message-content user-message">
                <div class="message-header">
                    <span class="sender">You</span>
                </div>
                <div class="message-text">{msg['user']}</div>
            </div>
            <div class="message-content assistant-message">
                <div class="message-header">
                    <span class="sender">Assistant</span>
                </div>
                <div class="message-text">{msg['assistant']}</div>
            </div>
        </div>
        """
    
    return f"""
    <html>
        <head>
            <title>Calendar Agent</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                :root {{
                    --primary-color: #2196F3;
                    --secondary-color: #E3F2FD;
                    --text-color: #333;
                    --border-radius: 8px;
                    --spacing: 16px;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                    color: var(--text-color);
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: var(--spacing);
                }}
                
                h2 {{
                    color: var(--primary-color);
                    margin-bottom: var(--spacing);
                    text-align: center;
                }}
                
                .conversation {{
                    background: white;
                    border-radius: var(--border-radius);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: var(--spacing);
                    margin-bottom: var(--spacing);
                    max-height: 70vh;
                    overflow-y: auto;
                }}
                
                .message {{
                    margin-bottom: var(--spacing);
                }}
                
                .message-content {{
                    padding: var(--spacing);
                    border-radius: var(--border-radius);
                    margin-bottom: 8px;
                }}
                
                .user-message {{
                    background-color: var(--primary-color);
                    color: white;
                    margin-left: 20%;
                }}
                
                .assistant-message {{
                    background-color: var(--secondary-color);
                    margin-right: 20%;
                }}
                
                .message-header {{
                    margin-bottom: 8px;
                    font-size: 0.9em;
                }}
                
                .sender {{
                    font-weight: bold;
                }}
                
                .message-text {{
                    white-space: pre-wrap;
                    word-break: break-word;
                }}
                
                .input-container {{
                    background: white;
                    padding: var(--spacing);
                    border-radius: var(--border-radius);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                form {{
                    display: flex;
                    gap: var(--spacing);
                    margin-bottom: var(--spacing);
                }}
                
                input[type="text"] {{
                    flex: 1;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: var(--border-radius);
                    font-size: 16px;
                    transition: border-color 0.3s;
                }}
                
                input[type="text"]:focus {{
                    outline: none;
                    border-color: var(--primary-color);
                }}
                
                button {{
                    padding: 12px 24px;
                    background-color: var(--primary-color);
                    color: white;
                    border: none;
                    border-radius: var(--border-radius);
                    cursor: pointer;
                    font-size: 16px;
                    transition: background-color 0.3s;
                }}
                
                button:hover {{
                    background-color: #1976D2;
                }}
                
                .clear-btn {{
                    background-color: #f44336;
                }}
                
                .clear-btn:hover {{
                    background-color: #d32f2f;
                }}
                
                .event-link {{
                    color: var(--primary-color);
                    text-decoration: none;
                    font-weight: bold;
                }}
                
                .event-link:hover {{
                    text-decoration: underline;
                }}
                
                @media (max-width: 600px) {{
                    .container {{
                        padding: 8px;
                    }}
                    
                    .message-content {{
                        margin-left: 0 !important;
                        margin-right: 0 !important;
                    }}
                    
                    form {{
                        flex-direction: column;
                    }}
                    
                    button {{
                        width: 100%;
                    }}
                }}
            </style>
            <script>
                // Auto-scroll to bottom of conversation
                function scrollToBottom() {{
                    const conversation = document.querySelector('.conversation');
                    conversation.scrollTop = conversation.scrollHeight;
                }}
                
                // Scroll to bottom when page loads
                window.onload = scrollToBottom;
                
                // Scroll to bottom after form submission
                document.addEventListener('DOMContentLoaded', function() {{
                    const form = document.querySelector('form');
                    form.addEventListener('submit', function() {{
                        setTimeout(scrollToBottom, 100);
                    }});
                }});
            </script>
        </head>
        <body>
            <div class="container">
                <h2>Calendar Agent</h2>
                <div class="conversation">
                    {history_html}
                </div>
                <div class="input-container">
                    <form action="/chat" method="post">
                        <input type="text" name="message" required placeholder="Type your message..." autocomplete="off" />
                        <button type="submit">Send</button>
                    </form>
                    <form action="/clear" method="post" style="display: inline;">
                        <button type="submit" class="clear-btn">Clear Conversation</button>
                    </form>
                </div>
            </div>
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
