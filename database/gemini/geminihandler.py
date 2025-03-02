from google import genai

import asyncio
import os
from dotenv import load_dotenv


class geminiHandler:
    def __init__(self, model:str = 'gemini-2.0-flash', prompt:str = 'This is a test', api_key:str=''):
        self.model = model
        self.prompt = prompt
        self.data = {}

        if not api_key:
            raise ValueError("Please provide a Gemini API key")
        self.api_key = api_key

    def set_prompt(self, prompt):
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt cannot be empty")
        self.prompt = prompt

    def update_data(self, key: str, value: str):
        if not key or not value or not isinstance(value, str):
            raise ValueError("Key and value must be non-empty strings")
        self.data[key] = value

    def send_prompt(self):
        try:
            client = genai.Client(api_key=self.api_key)
            contents = self.prompt
            if self.data:
                contents += f"Data: {self.data}"

            response = client.models.generate_content(
                model=self.model, contents=contents
            )

            return response.text

        except Exception as e:
            return f"An error occurred: {str(e)}"


if __name__ == "__main__":
    pass
