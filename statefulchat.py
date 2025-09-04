import os
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    print("Stateful Chatbot - Responses API - (type 'exit' to quit)")
    previous_response_id = None
    model = "gpt-4o-mini"
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        # Show conversation context (the last response id and model) without calling the API
        if user_input.strip().lower() == "context":
            print(f"Context -> previous_response_id: {previous_response_id}, model: {model}")
            continue
        params = {
            "model": model,
            "input": user_input,
            "instructions": "You are a helpful assistant. Remember facts the user tells you and reference them in future responses."
        }
        if previous_response_id:
            params["previous_response_id"] = previous_response_id
        try:
            response = client.responses.create(**params)
            text = response.output[0].content[0].text
            print(f"Bot: {text}")
            previous_response_id = response.id
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
