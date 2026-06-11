import os
import json
from groq import Groq
from dotenv import load_dotenv
import yaml
from pathlib import Path


class Agent:
    def __init__(self, content: str ):
        # Base paths
        self.BASE_DIR = Path(__file__).resolve().parents[3]
        env_path = self.BASE_DIR / ".env"

        load_dotenv(env_path)

        self.API_KEY = os.getenv("GROQ_API_KEY")
        self.MODEL = "llama-3.3-70b-versatile"

        # Load prompts once
        with open(self.BASE_DIR / "prompts.yaml", "r", encoding="utf-8") as f:
            self.prompts = yaml.safe_load(f)

        if not self.API_KEY:
            raise ValueError("GROQ_API_KEY is missing")

        # Initialize client once (better performance)
        self.client = Groq(api_key=self.API_KEY)

        self.content = self.prompts[content]["content"]

    def _LLM(self, prompt: str, content: str) -> str:
        """
        Internal LLM call
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt is empty")

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": content
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0
            )

            raw_output = response.choices[0].message.content
            return str(raw_output)
        
        except Exception as e:
            print(f"Error during LLM call: {e}")
            return str(e)

    def run(self, prompt: str) -> dict:
        """
        Public method to call LLM
        """
        return self._LLM(prompt, self.content)

if __name__ == "__main__":
    relevance_agent = Agent(content="relevance_agent")
    print(relevance_agent.run("Is it a good idea to visit Paris in winter?"))