"""OpenAI implementation for the calendar agent."""

import os
import logging
from typing import Optional
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def get_openai_llm():
    """Get an OpenAI LLM instance."""
    try:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        logger.info("Successfully initialized OpenAI client")
        return client
    except ImportError:
        logger.error("Failed to import OpenAI. Please install it with: pip install openai")
        raise
    except Exception as e:
        logger.error("Error initializing OpenAI client: %s", str(e))
        raise 