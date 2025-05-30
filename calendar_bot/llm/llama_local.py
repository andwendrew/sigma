"""Llama 2 implementation for the calendar agent."""

import requests
import logging
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama2"

def prompt_llama(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = MODEL_NAME,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_k: int = 40,
    num_predict: int = 2048
) -> str:
    """
    Send a prompt to the Llama 2 model via Ollama.
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt to guide the model's behavior
        model: The model name to use
        temperature: Controls randomness (0.0 to 1.0)
        top_p: Nucleus sampling parameter (0.0 to 1.0)
        top_k: Number of tokens to consider for top-k sampling
        num_predict: Maximum number of tokens to generate
        
    Returns:
        The model's response as a string
    """
    try:
        # Format the full prompt if system prompt is provided
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        data = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": num_predict
            }
        }
        
        logger.info(f"Sending request to Llama 2 model: {model}")
        response = requests.post(OLLAMA_URL, json=data)
        response.raise_for_status()
        
        result = response.json()
        logger.info("Successfully received response from Llama 2 model")
        return result["response"]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Ollama server: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Llama 2 prompt: {str(e)}")
        raise

class LlamaLLM:
    """Wrapper class for Llama 2 LLM."""
    
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        num_predict: int = 2048
    ):
        """
        Initialize the Llama 2 LLM.
        
        Args:
            system_prompt: Optional system prompt to guide the model's behavior
            temperature: Controls randomness (0.0 to 1.0)
            top_p: Nucleus sampling parameter (0.0 to 1.0)
            top_k: Number of tokens to consider for top-k sampling
            num_predict: Maximum number of tokens to generate
        """
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.num_predict = num_predict
    
    def __call__(self, prompt: str) -> str:
        """Call the Llama 2 model with the given prompt."""
        return prompt_llama(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            num_predict=self.num_predict
        )

def get_llama_llm(
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_k: int = 40,
    num_predict: int = 2048
) -> LlamaLLM:
    """
    Get a Llama 2 LLM instance with the specified parameters.
    
    Args:
        system_prompt: Optional system prompt to guide the model's behavior
        temperature: Controls randomness (0.0 to 1.0)
        top_p: Nucleus sampling parameter (0.0 to 1.0)
        top_k: Number of tokens to consider for top-k sampling
        num_predict: Maximum number of tokens to generate
        
    Returns:
        A configured LlamaLLM instance
    """
    return LlamaLLM(
        system_prompt=system_prompt,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        num_predict=num_predict
    )

if __name__ == "__main__":
    print("Test the local Llama 2 8B LLM via Ollama.")
    llm = get_llama_llm(
        system_prompt="You are a helpful assistant that creates calendar events.",
        temperature=0.7
    )
    
    while True:
        prompt = input("\nEnter a prompt (or 'exit' to quit): ")
        if prompt.lower() == 'exit':
            break
        try:
            response = llm(prompt)
            print(f"\nLlama 2 response: {response}")
        except Exception as e:
            print(f"\nError: {e}") 