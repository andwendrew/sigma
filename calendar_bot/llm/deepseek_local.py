"""DeepSeek implementation for the calendar agent."""

import os
import logging
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def get_deepseek_llm():
    """Get a DeepSeek LLM instance."""
    try:
        # Check for API key
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
        # Initialize DeepSeek client
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        logger.info("Successfully initialized DeepSeek client")
        return client
    except ImportError:
        logger.error("Failed to import OpenAI. Please install it with: pip install openai")
        raise
    except Exception as e:
        logger.error("Error initializing DeepSeek client: %s", str(e))
        raise

def get_deepseek_response(client: OpenAI, prompt: str, system_prompt: str = "You are a helpful assistant") -> str:
    """Get a response from DeepSeek."""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error("Error getting DeepSeek response: %s", str(e))
        raise 