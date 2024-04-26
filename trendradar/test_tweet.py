import tweepy

# Replace 'your_bearer_token_here' with your actual bearer token
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAE09mgEAAAAA%2FgX3nPbAfZ1qUbE26sgx8DkhRwU%3DMaKXxhAsSFNzCpHtaXtaoehPcPZnjPywEsfcfuNGsMwROQTGKY'
client = tweepy.Client(bearer_token)

# Assuming results is a list
results = []

twitter_usernames = [
    'WIRED'
]

for username in twitter_usernames:
    # Fetch user ID using the username
    user_response = client.get_user(username=username)
    if user_response.data:
        user_id = user_response.data.id
        print(f"Printing latest 2 tweets from {username} (ID: {user_id})")
        print("="*50)

        # Get the latest 2 tweets from the user's timeline using their ID
        tweets_response = client.get_users_tweets(id=user_id, max_results=5)
        if tweets_response.data:
            for i, tweet in enumerate(tweets_response.data):
                print(f"Tweet {i+1}: {tweet.text}")
                # Add summaries to the list
                results.append(tweet.text)
        else:
            print("No tweets found for this user.")

        print("\n")
    else:
        print(f"No user found with username {username}")

# Optionally print all results if needed
print(results)

