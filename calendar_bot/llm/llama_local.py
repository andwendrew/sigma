"""Llama 3 implementation for the calendar agent."""

import requests
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"

def prompt_llama(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = MODEL_NAME,
    temperature: float = 0.2,  # Lower temperature for more deterministic responses
    top_p: float = 0.3,       # Lower top_p for more focused responses
    top_k: int = 20,          # Lower top_k for more precise token selection
    num_predict: int = 512    # Reduced max tokens since calendar events are concise
) -> str:
    """
    Send a prompt to the Llama model via Ollama API.
    
    Args:
        prompt: The user's prompt
        system_prompt: Optional system prompt to guide the model's behavior
        model: The model name to use
        temperature: Controls randomness (0.0 to 1.0)
            - Lower values (0.1-0.3) for more deterministic responses
            - Higher values (0.7-1.0) for more creative responses
        top_p: Nucleus sampling parameter (0.0 to 1.0)
            - Lower values (0.1-0.3) for more focused responses
            - Higher values (0.7-1.0) for more diverse responses
        top_k: Top-k sampling parameter
            - Lower values (10-20) for more focused token selection
            - Higher values (40-100) for more variety
        num_predict: Maximum number of tokens to predict
            - Lower values for concise responses
            - Higher values for longer, more detailed responses
        
    Returns:
        The model's response as a string
    """
    try:
        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": num_predict
            }
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt
        
        # Send the request to Ollama
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        # Extract and return the response
        return response.json()["response"]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Ollama API: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

class LlamaLLM:
    """Wrapper class for the Llama model."""
    
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,  # Lower temperature for more deterministic responses
        top_p: float = 0.3,       # Lower top_p for more focused responses
        top_k: int = 20,          # Lower top_k for more precise token selection
        num_predict: int = 512    # Reduced max tokens since calendar events are concise
    ):
        """
        Initialize the Llama LLM wrapper.
        
        Args:
            system_prompt: Optional system prompt
            temperature: Controls randomness
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            num_predict: Maximum number of tokens to predict
        """
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.num_predict = num_predict
    
    def __call__(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call the Llama model with the given prompt.
        
        Args:
            prompt: The user's prompt
            system_prompt: Optional system prompt to override the default
            
        Returns:
            The model's response
        """
        # Use provided system prompt or fall back to the default
        system_prompt = system_prompt or self.system_prompt
        
        return prompt_llama(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            num_predict=self.num_predict
        )

def get_llama_llm(
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,  # Lower temperature for more deterministic responses
    top_p: float = 0.3,       # Lower top_p for more focused responses
    top_k: int = 20,          # Lower top_k for more precise token selection
    num_predict: int = 512    # Reduced max tokens since calendar events are concise
) -> LlamaLLM:
    """
    Get an instance of the Llama LLM wrapper.
    
    Args:
        system_prompt: Optional system prompt
        temperature: Controls randomness
        top_p: Nucleus sampling parameter
        top_k: Top-k sampling parameter
        num_predict: Maximum number of tokens to predict
        
    Returns:
        An instance of LlamaLLM
    """
    return LlamaLLM(
        system_prompt=system_prompt,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        num_predict=num_predict
    )

if __name__ == "__main__":
    # Test the Llama model
    llm = get_llama_llm()
    
    print("Testing Llama 3 model. Type 'quit' to exit.")
    while True:
        user_input = input("\nEnter your prompt: ")
        if user_input.lower() == 'quit':
            break
        try:
            from calendar_bot.agent.components.prompts import DATE_REFERENCE_TRANSFORMER_PROMPT
            from datetime import datetime
            from calendar_bot.agent.components.calendar_analyzer import get_next_two_weeks_dates
            system_prompt = DATE_REFERENCE_TRANSFORMER_PROMPT.format(
                today=datetime.now().strftime("%Y-%m-%d"),
                day_of_week=datetime.now().strftime("%A"),
                conversation_history="",
                date_mapping=get_next_two_weeks_dates(datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%A"))
            )
            print(system_prompt)
            response = llm(user_input, system_prompt=system_prompt)
            print("\nResponse:", response)
        except Exception as e:
            print(f"Error: {str(e)}") 