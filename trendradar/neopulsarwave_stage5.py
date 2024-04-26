import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason, Tool
import vertexai.preview.generative_models as generative_models

def generate():
    vertexai.init(project="flaskgeopolitics", location="us-central1")
    tools = [
        Tool.from_google_search_retrieval(
            google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(disable_attribution=False)
        ),
    ]
    model = GenerativeModel("gemini-1.5-pro-preview-0409", tools=tools)
    responses = model.generate_content(
        [text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    # Initialize an empty string to collect all generated text
    all_text = ""

    for response in responses:
        if not response.candidates:
            print("No candidates found in response.")
            continue

        first_candidate = response.candidates[0]
        if first_candidate.finish_reason != FinishReason.FINISH_REASON_UNSPECIFIED:
            continue

        if hasattr(first_candidate, 'content') and hasattr(first_candidate.content, 'text'):
            all_text += first_candidate.content.text  # Append text to the all_text string
        else:
            print("No content parts found in response.")
            

    return all_text  # Return the accumulated text

# Usage example
text1 = """try to search more information of the following inquiry "Potential military escalation Iran Israel"""
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}
safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

# Call the function and store the result
generated_output = generate()
print("Generated Output:")
print(generated_output)

