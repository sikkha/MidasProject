import sqlite3
import requests
import openai
import google.generativeai as genai
from llm_handler import call_LLM


import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason, Tool
import vertexai.preview.generative_models as generative_models

import sqlite3

def setup_enhanced_knowledge_database():
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()
    # Redefine the EnhancedKnowledge table to use the same id as in PresentationTweets and Tweets
    cur.execute('''
        CREATE TABLE IF NOT EXISTS EnhancedKnowledge (
            id INTEGER PRIMARY KEY,
            summary TEXT,
            enhanced_context TEXT,
            FOREIGN KEY (id) REFERENCES PresentationTweets(id)
        )
    ''')
    conn.commit()
    return conn

import requests
from bs4 import BeautifulSoup

def scrape_content(url):
    """
    Fetches and prints the entire HTML content from the given URL.

    :param url: URL of the webpage to scrape
    :return: HTML content of the webpage as a string
    """
    try:
        # Sending a request to the specified URL
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad requests

        # Printing the entire HTML content
        print(response.text)

        return response.text
    except requests.RequestException as e:
        print(f"Error during requests to {url}: {e}")
        return None


# Configure the Google API Key
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model configuration and safety settings
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


import requests
from requests.exceptions import HTTPError


def scrape_web_content(url):
    """Fetches web content from the specified URL."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        return response.text
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"Other error occurred: {err}")
        return None

def summarize_content(html_content):
    """Summarizes the provided HTML content using an AI model."""
    if not html_content:
        return "No content to summarize."
    context = "Extract meaningful content from the following web scraping:"
    analysis_prompt = f"{context}\n\n{html_content}"
    convo = model.start_chat(history=[])
    convo.send_message(analysis_prompt)
    # <<< DEBUG
    print("Analysis Prompt: ", analysis_prompt)
    if convo.last and hasattr(convo.last, 'text'):
        return convo.last.text
    return "No summary could be generated."

def get_enhanced_inquiry(summary):
    """Generates a refined inquiry prompt based on the summarized content."""
    context_prompt = "try to search more information of the following inquiry: "
    full_prompt = f"{context_prompt}\n\n{summary}"
    output_inquiry = call_LLM("gemini-pro", full_prompt)
    return output_inquiry

def perform_further_research(query):
    """
    This function uses Vertex AI's generative model with Google search retrieval
    to conduct research based on a given query and compile the findings into a coherent text.
    """
    # Initialize Vertex AI with your project and location details
    vertexai.init(project="flaskgeopolitics", location="us-central1")

    # Configure the tools to be used with the model (Google Search Retrieval)
    tools = [
        Tool.from_google_search_retrieval(
            google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(disable_attribution=False)
        ),
    ]

    # Initialize the Generative Model with the appropriate tools
    model = GenerativeModel("gemini-1.5-pro-preview-0409", tools=tools)

    # Configuration settings for generating content
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
    }

    # Safety settings to avoid generating harmful content
    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    # Generate content based on the query
    responses = model.generate_content(
        [query],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    # Initialize an empty string to collect all generated text
    all_text = ""

    # Process each response to collect the generated text
    for response in responses:
        if not response.candidates:
            print("No candidates found in response.")
            continue

        # Take the first candidate from the response
        first_candidate = response.candidates[0]
        if first_candidate.finish_reason != FinishReason.FINISH_REASON_UNSPECIFIED:
            continue

        # Check for text content and append it
        if hasattr(first_candidate, 'content') and hasattr(first_candidate.content, 'text'):
            all_text += first_candidate.content.text
        else:
            print("No content parts found in response.")

    return all_text or "No relevant research results found."

def validate_content(content):
    # Adjust the validation threshold or criteria based on typical content characteristics
    return len(content.split()) > 10  # Example: Ensure there are more than 10 words


def process_high_score_tweets():
    conn = sqlite3.connect('tweets.db')
    try:
        cur = conn.cursor()
        cur.execute('SELECT PresentationTweets.id, Tweets.item, Tweets.url FROM PresentationTweets JOIN Tweets ON PresentationTweets.id = Tweets.id')
        eligible_tweets = cur.fetchall()

        for tweet_id, item, url in eligible_tweets:
            cur.execute('SELECT id FROM EnhancedKnowledge WHERE id = ?', (tweet_id,))
            if cur.fetchone():
                print(f"Skipping insertion for already existing id {tweet_id}")
                continue

            content_to_use = scrape_web_content(url) or item
            if not validate_content(content_to_use):
                print(f"Content did not pass validation checks and will not be processed: {content_to_use}")
                inquiry = item
                continue
            else:
                print("hello!! ...", content_to_use)
                summary = summarize_content(content_to_use)
                
            inquiry = get_enhanced_inquiry(summary)
            research = perform_further_research(inquiry)

            try:
                with conn:
                    if research:
                        cur.execute('INSERT INTO EnhancedKnowledge (id, summary, enhanced_context) VALUES (?, ?, ?)', (tweet_id, summary, research))
                        # The commit is automatically managed by the context manager
                    else:
                        print("Failed to generate valid research output.")
                        raise Exception("Research output was not valid; transaction will not commit.")
            except sqlite3.DatabaseError as e:
                print(f"Database error prevented transaction: {e}")
            except Exception as e:
                print(f"An unexpected error occurred, transaction rolled back: {e}")

#   except Exception as e:
#       print(f"Unexpected error in processing tweets: {e}")
#        conn.rollback()
    finally:
        conn.close()


# Example usage
if __name__ == "__main__":
    print("start the wise project...")
    setup_enhanced_knowledge_database()
    process_high_score_tweets()
    print("end the wise project")

