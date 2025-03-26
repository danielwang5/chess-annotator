# chatgpt_interface.py
import openai
import concurrent.futures
from src.config import OPENAI_API_KEY

# Set your API key for the OpenAI module.
openai.api_key = OPENAI_API_KEY

def get_annotation_from_chatgpt(prompt: str) -> str:
    """
    Sends the given prompt (with internal context) to the GPT-4 model using the new
    ChatCompletion.create API and returns the generated annotation.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # Use a model you have access to (e.g., "gpt-4")
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150  # Adjust as needed for brevity.
        )
        # Extract the annotation from the response.
        annotation = response.choices[0].message.content
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
