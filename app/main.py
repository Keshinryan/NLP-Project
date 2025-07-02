from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import pickle
from keras.preprocessing.sequence import pad_sequences
from app.preprocess import preprocess_text
from dotenv import load_dotenv
import os
import tweepy
import re
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Initialize Twitter API client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and tokenizer
model = tf.keras.models.load_model("app/model.h5")
tokenizer = pickle.load(open("app/tokenizer.pkl", "rb"))
MAX_LEN = 50

# Rate limit tracking
last_twitter_call_time = None
cooldown_duration = timedelta(minutes=15)


def extract_tweet_id(tweet_url):
    match = re.search(r"status/(\d+)", tweet_url)
    return match.group(1) if match else None


def extract_username(tweet_url):
    match = re.search(r"x\.com/([^/]+)/status/", tweet_url)
    return match.group(1) if match else None


def fetch_replies(tweet_url, limit=100):
    global last_twitter_call_time
    now = datetime.utcnow()

    # Check 15-minute cooldown
    if last_twitter_call_time and now - last_twitter_call_time < cooldown_duration:
        reset_time = last_twitter_call_time + cooldown_duration
        remaining = reset_time - now
        return {
            "error": "Twitter API rate limit active.",
            "reset_time": reset_time.isoformat() + "Z",
            "remaining_seconds": int(remaining.total_seconds()),
            "message": f"Try again in {remaining.seconds // 60}m {remaining.seconds % 60}s"
        }

    tweet_id = extract_tweet_id(tweet_url)
    username = extract_username(tweet_url)
    if not tweet_id or not username:
        return {"error": "Invalid tweet URL format."}

    query = f"conversation_id:{tweet_id} to:{username}"
    replies = []

    try:
        for tweet in tweepy.Paginator(
            client.search_recent_tweets,
            query=query,
            tweet_fields=["text"],
            max_results=100,
        ).flatten(limit=limit):
            replies.append(tweet.text)

        last_twitter_call_time = now  # Update if successful

    except tweepy.errors.TooManyRequests:
        last_twitter_call_time = now  # Still update to enforce cooldown
        reset_time = last_twitter_call_time + cooldown_duration
        remaining = reset_time - now
        return {
            "error": "Twitter API rate limit hit.",
            "reset_time": reset_time.isoformat() + "Z",
            "remaining_seconds": int(remaining.total_seconds()),
            "message": f"Try again in {remaining.seconds // 60}m {remaining.seconds % 60}s"
        }

    except Exception as e:
        print(f"Twitter API error: {e}")
        return {"error": "Twitter API call failed."}

    return replies


@app.get("/")
def home():
    return {"message": "NLP Hate Speech API is running."}


@app.get("/predict")
def predict(tweet_url: str = Query(...)):
    replies = fetch_replies(tweet_url, limit=100)

    if isinstance(replies, dict) and "error" in replies:
        return replies

    if not replies:
        return {"error": "No replies found or invalid tweet URL."}

    hate_count = 0
    for reply in replies:
        cleaned = preprocess_text(reply)
        sequence = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(sequence, maxlen=MAX_LEN, padding="post")
        prediction = model.predict(padded)[0][0]
        if prediction > 0.5:
            hate_count += 1

    total = len(replies)
    hate_percentage = (hate_count / total) * 100
    not_hate_percentage = 100 - hate_percentage

    return {
        "tweet_url": tweet_url,
        "total_replies": total,
        "hate_speech_percent": round(hate_percentage, 2),
        "non_hate_speech_percent": round(not_hate_percentage, 2),
    }
