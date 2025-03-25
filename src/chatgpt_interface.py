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
        # Debug print the full response.
        print("DEBUG: Full response object:", response)

        # Extract the generated text from the nested response structure.
        annotation = ""
        if hasattr(response, "output") and response.output:
            # Get the first message in the output list.
            first_message = response.output[0]
            if hasattr(first_message, "content") and first_message.content:
                # Get the first text object in the content list.
                first_text_obj = first_message.content[0]
                annotation = first_text_obj.text

        print("DEBUG: Extracted annotation:", annotation)
        return annotation.strip()
    except Exception as e:
        print("Error calling ChatGPT API:", e)
        return "Annotation generation failed."

# For testing:
if __name__ == "__main__":
    sample_prompt = "Analyze the following chess position: FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    output = get_annotation_from_chatgpt(sample_prompt)
    print("Final output annotation:", output)
