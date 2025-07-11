from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from keras.preprocessing.sequence import pad_sequences
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import tensorflow as tf
import pickle
import os
import re
from .preprocess import preprocess_text

MAX_LEN = 50

# Load model dan tokenizer
model = tf.keras.models.load_model("app/model.h5")
tokenizer = pickle.load(open("app/tokenizer.pkl", "rb"))

# Init FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Extract tweet ID
def extract_tweet_id(tweet_url: str):
    match = re.search(r"status/(\d+)", tweet_url)
    return match.group(1) if match else None

# Classify reply text
def classify_reply(text: str):
    cleaned = preprocess_text(text)
    seq = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(seq, maxlen=MAX_LEN, padding="post")
    prediction = float(model.predict(padded)[0][0])
    return prediction

# Scrape tweet + replies
async def scrape_tweet_and_replies(tweet_url: str):
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup

    replies_set = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")
        context = await browser.new_context(storage_state=STATE_PATH)
        page = await context.new_page()
        await page.goto(tweet_url, timeout=60000)

        last_count = 0
        attempts = 0

        while len(replies_set) < 100 and attempts < 20:
            # Scroll to bottom
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

            # Click all "Show more replies" buttons
            buttons = await page.query_selector_all("div[role='button']")
            for btn in buttons:
                try:
                    text = await btn.inner_text()
                    if "Show" in text or "Lihat" in text:
                        await btn.click()
                        await page.wait_for_timeout(2000)
                except:
                    continue

            # Extract text content
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            divs = soup.find_all("div", {"data-testid": "tweetText"})
            texts = [div.get_text(strip=True) for div in divs]

            # Store unique replies
            for t in texts[1:]:
                replies_set.add(t)
                if len(replies_set) >= 100:
                    break

            # Break if no more replies are loading
            if len(replies_set) == last_count:
                attempts += 1
            else:
                attempts = 0  # reset attempts if new replies are found

            last_count = len(replies_set)

        await browser.close()

        if not texts:
            raise RuntimeError("Gagal mengambil tweet dan reply")

        tweet_text = texts[0]
        replies = list(replies_set)

        return tweet_text, replies

@app.get("/")
def home():
    return {"message": "API Hate Speech Twitter/X is running."}

@app.get("/predict")
async def predict(tweet_url: str = Query(..., description="Tweet URL from x.com")):
    tweet_id = extract_tweet_id(tweet_url)
    if not tweet_id:
        return {"error": "Invalid tweet URL format."}

    try:
        tweet_text, replies = await scrape_tweet_and_replies(tweet_url)

        hate_replies = []
        not_hate_replies = []

        for reply in replies[:100]:
            score = classify_reply(reply)
            if score > 0.5:
                hate_replies.append((reply, score))
            else:
                not_hate_replies.append((reply, score))

        total = len(replies)
        return {
            "tweet_url": tweet_url,
            "tweet_id": tweet_id,
            "tweet_text": tweet_text,
            "total_replies": total,
            "hate_speech_percent": round(len(hate_replies) / total * 100, 2) if total else 0,
            "non_hate_speech_percent": round(len(not_hate_replies) / total * 100, 2) if total else 0,
            "top_5_hate_replies": [
                {"text": r[0], "score": round(r[1], 3)} for r in sorted(hate_replies, key=lambda x: x[1], reverse=True)[:5]
            ],
            "top_5_non_hate_replies": [
                {"text": r[0], "score": round(r[1], 3)} for r in sorted(not_hate_replies, key=lambda x: x[1])[:5]
            ],
        }

    except Exception as e:
        return {"error": str(e)}
