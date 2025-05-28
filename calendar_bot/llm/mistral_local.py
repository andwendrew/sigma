import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "mistral"

def prompt_mistral(prompt: str, model: str = MODEL_NAME) -> str:
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=data)
    response.raise_for_status()
    return response.json()["response"]

class MistralLLM:
    def __call__(self, prompt: str) -> str:
        return prompt_mistral(prompt)

def get_mistral_llm():
    return MistralLLM()

if __name__ == "__main__":
    print("Test the local Mistral LLM via Ollama.")
    while True:
        prompt = input("Enter a prompt (or 'exit' to quit): ")
        if prompt.lower() == 'exit':
            break
        try:
            response = prompt_mistral(prompt)
            print(f"Mistral response: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")
