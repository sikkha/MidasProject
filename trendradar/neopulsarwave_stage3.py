import sqlite3
import os
import requests
import re
import openai
from openai import OpenAI
from llm_handler import call_LLM




def update_categorization(cur, tweet_id, tweet_text, context_for_scoring):
    prompt = f"{context_for_scoring}\n\nTweet: {tweet_text}"
    new_categorization = call_LLM("gemini-pro", prompt).strip()  # Assuming this function returns the new categorization
    cur.execute('''
        UPDATE PresentationTweets
        SET categorization = ?
        WHERE id = ?
    ''', (new_categorization, tweet_id))

def update_ring_layer(cur, tweet_id, tweet_text, context_for_ringing):
    prompt = f"{context_for_ringing}\n\nTweet: {tweet_text}"
    new_ring_layer = call_LLM("gemini-pro", prompt).strip()  # Assuming this function returns the new ring layer
    cur.execute('''
        UPDATE PresentationTweets
        SET ring_layer = ?
        WHERE id = ?
    ''', (new_ring_layer, tweet_id))

def print_final_output():
    # Connect to the SQLite database
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()

    # Execute the join query to fetch necessary details
    cur.execute('''
    SELECT 
        P.categorization,
        P.ring_layer,
        T.summary,
        T.url
    FROM 
        PresentationTweets P
    JOIN 
        Tweets T ON P.id = T.id
    ''')

    # Fetch the results
    results = cur.fetchall()

    # Print results in the specified format
    for result in results:
        # Construct the output string as specified
        output_string = f"{result[0]}, {result[1]}, {result[2]}, {result[3]}, True, 0\n"
        print(output_string)

    # Close the connection
    conn.close()


def main():
    context_for_scoring = "do categorize the following tweet quadrant 0 is \"societal and cultural\", 1 is \"innovation and law\", 2 is \"politics and security\", 3 is \"economics\""
    
    context_for_ringing = """
    Given that all tweets have a score of 85 or above and are thus considered highly important, classify each tweet into one of four urgency levels based on its content and importance:

    - Ring 0: 'Engage' - Immediate action or response required. Represents the highest priority within already important tweets.
    - Ring 1: 'Monitor' - Important to keep a close watch due to potential developments or impacts.
    - Ring 2: 'Observe' - Less immediate, observe as part of routine checks.
    - Ring 3: 'Acknowledge' - Recognize the information but it requires the least immediate action.

    Remember to print out only number. Use this criteria to determine the appropriate ring for the following tweet:
    """
    
    # Connect to the SQLite database
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()

    # Execute the join query to fetch necessary tweet details
    cur.execute('''
    SELECT 
        T.id,
        T.item  
    FROM 
        PresentationTweets P
    JOIN 
        Tweets T ON P.id = T.id
    ''')

    # Fetch the results
    tweets_to_process = cur.fetchall()

    # Process and update each tweet's categorization and ring layer
    for tweet in tweets_to_process:
        tweet_id = tweet[0]
        tweet_text = tweet[1]

        # Update categorization
        update_categorization(cur, tweet_id, tweet_text, context_for_scoring)
        # Update ring layer
        update_ring_layer(cur, tweet_id, tweet_text, context_for_ringing)

        conn.commit()  # Commit changes after updating both fields for a tweet

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()
    print_final_output()

