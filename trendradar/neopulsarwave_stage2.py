import sqlite3
import os
import requests
import re
import openai
from openai import OpenAI

from llm_handler import call_LLM


# Set Twitter API
bearer_token = "YOUR_TWITTER_BEARER_TOKEN"

def fetch_tweets_for_processing():
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()
    cur.execute("SELECT id, item FROM Tweets")  # Fetches all tweets
    tweets = cur.fetchall()
    conn.close()
    return tweets


def update_tweets_in_database(tweet_updates):
    conn = sqlite3.connect('tweets.db')
    try:
        cur = conn.cursor()
        for tweet_id, summary, score in tweet_updates:
            print(f"Updating tweet ID {tweet_id} with Summary: {summary}, Score: {score}")
            cur.execute("UPDATE Tweets SET summary = ?, score = ? WHERE id = ?", (summary, score, tweet_id))
        conn.commit()
        print("Database update successful.")
    except Exception as e:
        print(f"Failed to update database: {e}")
        conn.rollback()  # Roll back any changes if there's an error
    finally:
        conn.close()


def get_summary(tweet_text):
    prompt = f"{context_for_summary}\n\nTweet: {tweet_text}"
    summary = call_LLM("openai", prompt).strip().strip('"')  # Remove any surrounding quotation marks
    print(f"Summary Output: {summary}")  # Debug output
    return summary


def get_score(tweet_text):
    prompt = f"{context_for_scoring}\n\nTweet: {tweet_text}"
    output = call_LLM("gemini-pro", prompt).strip()
    #output = call_LLM("openai", prompt).strip()
    print(f"Scoring Output: {output}")  # Debug output
    
    # Try to directly parse the output as an integer
    try:
        score = int(output)
        return score
    except ValueError:
        # If direct parsing fails, try regex to find a number
        match = re.search(r'\d+', output)
        if match:
            return int(match.group(0))  # Convert the captured score to an integer
        else:
            print(f"Defaulting to score of 0 for tweet ID due to failure to parse output: {output}")
            return 4  # Default score if parsing fails completely



def process_tweets():
    tweets = fetch_tweets_for_processing()
    tweet_updates = []
    
    for tweet_id, tweet_text in tweets:
        print("Processing tweet:", tweet_id)
        
        try:
            summary = get_summary(tweet_text)
            score = get_score(tweet_text)
            tweet_updates.append((tweet_id, summary, score))
            print(f"Updated: Summary - {summary}, Score - {score}")
        except Exception as e:
            print(f"Error processing tweet ID {tweet_id}: {str(e)}")
    
    update_tweets_in_database(tweet_updates)




context_for_summary = """
Provide a brief summary of the tweet in 3-4 words, capturing the essence of the message. Please do not use quotation marks in your response.
"""

context_for_scoring = """
As a seasoned media analyst, you have extensive experience in evaluating the relevance of news to global events and trends. Your task is to assess the importance of each tweet based on its potential impact on public discourse and policy. Please provide a precise numeric score from 0 to 100, where 0 indicates no relevance and 100 signifies maximum relevance. Use the full range of numbers to reflect subtle distinctions in importance. Do not round off scores to the nearest five or ten; provide exact numbers to best represent each tweet's impact.
Assess the importance of the tweet based on its relevance to current events, technological advancements, global issues, or social trends. Please provide a precise numeric score from 0 to 100, where 0 indicates no importance and 100 indicates maximum importance. Use the entire range and consider providing non-rounded numbers (e.g., 67, 82, 46) to reflect subtle variations in importance. Avoid rounding to the nearest five or ten unless it genuinely reflects the tweet's relevance. Do not include any textual explanation in your response; only the numeric score.
"""



if __name__ == "__main__":
    process_tweets()

