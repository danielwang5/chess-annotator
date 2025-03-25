# chatgpt_interface.py
import openai
from src.config import OPENAI_API_KEY

# Initialize the OpenAI client with your API key.
client = openai.Client(api_key=OPENAI_API_KEY)

def get_annotation_from_chatgpt(prompt: str) -> str:
    """
    Sends the prompt to the gpt-4o model via the new API (client.responses.create)
    and returns the generated annotation.
    """
    try:
        # Combine system instructions with the user prompt.
        combined_input = "You are a chess annotation expert. " + prompt

        # Call the API using the gpt-4o model.
        response = client.responses.create(
            input=combined_input,
            model="gpt-4o",
            temperature=0.7,
        )
        
        # Attempt to extract the generated text.
        try:
            # Try converting response.text to a dict and getting its "text" field.
            text_dict = response.text.to_dict()
            annotation = text_dict.get("text", "")
        except Exception:
            # Fallback: convert response.text to string.
            annotation = str(response.text)
        
        return annotation.strip()
    except Exception as e:
        print("Error calling ChatGPT API:", e)
        return "Annotation generation failed."

# For testing:
if __name__ == "__main__":
    sample_prompt = "Analyze the following chess position: FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    print(get_annotation_from_chatgpt(sample_prompt))
