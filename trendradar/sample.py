from llm_handler import call_LLM

def main():
    # Specify the model you want to use
    model_name = 'openai'  # Example: 'openai', 'mistral', 'anthropic', etc.
    prompt_text = "Hello, can you tell me about the weather tomorrow?"

    # Make the call to the language model
    response = call_LLM(model_name, prompt_text)
    
    # Print the response from the LLM
    print("Response from LLM:", response)

if __name__ == "__main__":
    main()

