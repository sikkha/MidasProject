import sqlite3
import tweepy
from prettytable import PrettyTable, ALL

import re
from pydantic import BaseModel
from typing import Optional  # Import Optional for older Python versions

import datetime


def setup_database():
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Tweets (
            id INTEGER PRIMARY KEY,
            user_tweet TEXT,
            item TEXT,
            url TEXT DEFAULT NULL,
            summary TEXT DEFAULT NULL,
            score INTEGER DEFAULT NULL,
            timestamp TEXT DEFAULT NULL
        )
    ''')
    conn.commit()
    return conn



class TweetModel(BaseModel):
    id: int
    user_tweet: str
    item: str
    url: Optional[str] = None  # Use Optional for type hinting
    summary: Optional[str] = None
    score: Optional[int] = None
    timestamp: str


def extract_url(tweet_text):
    # This regex finds urls starting with "https://"
    urls = re.findall(r'https://t\.co/[a-zA-Z0-9]+', tweet_text)
    return urls[0] if urls else None


def fetch_tweets(username, conn):
    try:
        user_response = client.get_user(username=username)
        if user_response.data:
            user_id = user_response.data.id
            tweets_response = client.get_users_tweets(id=user_id, max_results=5, tweet_fields=["created_at"])
            if tweets_response.data:
                cur = conn.cursor()
                for tweet in tweets_response.data:
                    url = extract_url(tweet.text)
                    text_without_url = re.sub(r'https://t\.co/\S+', '', tweet.text).strip()
                    # Convert datetime to ISO format string
                    iso_timestamp = tweet.created_at.isoformat() if tweet.created_at else None
                    tweet_data = TweetModel(
                        id=tweet.id,
                        user_tweet=username,
                        item=text_without_url,
                        url=url,
                        timestamp=iso_timestamp
                    )
                    cur.execute('INSERT OR IGNORE INTO Tweets (id, user_tweet, item, url, summary, score, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                                (tweet_data.id, tweet_data.user_tweet, tweet_data.item, tweet_data.url, tweet_data.summary, tweet_data.score, tweet_data.timestamp))
                conn.commit()
            else:
                print("No tweets found for this user.")
    except Exception as e:
        print(f"An error occurred: {e}")



def fetch_tweets_from_database():
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()
#    cur.execute("SELECT id, user_tweet, item, url, summary, score, timestamp FROM Tweets")
#    rows = cur.fetchall()
#    table = PrettyTable()
#    table.field_names = ["ID", "User", "Tweet", "URL", "Summary", "Score", "Timestamp"]
    
    cur.execute("SELECT id, user_tweet, item, url, summary, score, timestamp FROM Tweets")
    rows = cur.fetchall()
    table = PrettyTable()
    table.field_names = ["ID", "User", "Tweet", "URL", "Summary", "Score", "Timestamp"]
    
    table.max_width['Tweet'] = 30
    table.align["Tweet"] = "l"
    table.hrules = ALL
    if rows:
        for row in rows:
            table.add_row(row)
        print(table)
    else:
        print("No tweets found in the database.")
    conn.close()

def main():
    # Twitter API client setup
    bearer_token = 'YOUR_TWITTER_BEARER_TOKEN'
    global client
    client = tweepy.Client(bearer_token)

    # Database setup
    conn = setup_database()

    # List of Twitter usernames to fetch tweets from
    twitter_usernames = ['TheAtlantic']

    # Fetch tweets for each username and store them in the database
    for username in twitter_usernames:
        fetch_tweets(username, conn)

    # Display all tweets from the database
    fetch_tweets_from_database()

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()

