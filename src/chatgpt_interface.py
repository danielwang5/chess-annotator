import openai
import concurrent.futures
from src.config import OPENAI_API_KEY

# Initialize the OpenAI client with your API key.
client = openai.Client(api_key=OPENAI_API_KEY)

def get_annotation_from_chatgpt(prompt: str) -> str:
    """
    Sends the given prompt (with internal context) to the GPT-4o model
    using the new API (client.responses.create) and returns the generated annotation.
    """
    try:
        response = client.responses.create(
            input=prompt,
            model="gpt-4o",
            temperature=0.7,
        )
        # Extract the annotation from the response's nested structure.
        annotation = ""
        if hasattr(response, "output") and response.output:
            first_message = response.output[0]
            if hasattr(first_message, "content") and first_message.content:
                first_text_obj = first_message.content[0]
                annotation = first_text_obj.text
        return annotation.strip()
    except Exception as e:
        print("Error calling ChatGPT API:", e)
        return "Annotation generation failed."

def get_annotation_with_timeout(prompt: str, timeout: int = 60) -> str:
    """
    Wraps get_annotation_from_chatgpt in a timeout.
    If the API call takes longer than 'timeout' seconds, returns a timeout message.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_annotation_from_chatgpt, prompt)
        try:
            result = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"API call timed out after {timeout} seconds.")
            result = "Annotation generation timed out."
        return result

if __name__ == "__main__":
    sample_prompt = "Analyze the following chess position: FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    output = get_annotation_with_timeout(sample_prompt, timeout=60)
    print("Final output annotation:", output)
