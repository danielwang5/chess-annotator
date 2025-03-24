# chatgpt_interface.py
import openai
from src.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_annotation_from_chatgpt(prompt: str) -> str:
    """
    Sends the prompt to ChatGPT and returns the generated annotation.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a chess annotation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150  # Adjust token count as needed
        )
        annotation = response.choices[0].message['content'].strip()
        return annotation
    except Exception as e:
        print("Error calling ChatGPT API:", e)
        return "Annotation generation failed."

# For testing:
if __name__ == "__main__":
    sample_prompt = "Test prompt for chess annotation."
    print(get_annotation_from_chatgpt(sample_prompt))
