# 🚨 Hate Speech Classification using Bi-LSTM for Twitter / X

## Table of Contents
- [Project Overview](#project-overview)
- [Dataset](#dataset)
- [Model](#model)
- [Installation](#installation)
- [Deploy](#deploy)
- [Detection Demo](#detection-demo)
- [Next Steps](#next-steps)
- [Author](#author)
- [License](#license)

---

## 📌 Project Overview 

This project builds a real-time **Natural Language Processing (NLP)** system that detects **hate speech in reposts or replies** on Twitter (now X).  
Given a tweet link, the app fetches all replies (including deep-level ones) and classifies whether they contain hate speech using a trained **Bi-LSTM model**.

---

## 📂 Dataset

- **Source**: [Kaggle – Indonesian Abusive and Hate Speech Twitter Text](https://www.kaggle.com/datasets/ilhamfp31/indonesian-abusive-and-hate-speech-twitter-text?select=data.csv)  
- **Format**: CSV  
- **Total Rows**: 13,169 tweets  
- **Language**: Bahasa Indonesia  

### 🔍 Preprocessing Steps:
- Normalize alay words using a custom dictionary
- Lowercasing
- Remove duplicate words
- Stemming using PorterStemmer
- Remove stopwords (Indonesian)
- Tokenization and padding
- Word2Vec (skip-gram) embedding

---

## 🧠 Model

- **Model Type**: Bi-LSTM (Bidirectional LSTM)
- **Framework**: TensorFlow / Keras
- **Input Length**: 50 tokens
- **Embedding**: Word2Vec (vector size = 50)
- **Output**: Binary classification (Hate / Not Hate)
- **Saved Format**: `.h5` model (NLP), `model` (Word2Vec), and `tokenizer.pkl`

---

## ⚙️ Installation

### Requirements

```bash
Python >= 3.10
TensorFlow >= 2.11
nltk
gensim
contractions
fastapi
uvicorn
python-dotenv
pandas
playwright
bs4
```

### Setup

```bash
# Clone this repository
git clone https://github.com/Keshinryan/NLP-Project
cd NLP-Project
```

---

## 🔐 Login and Cookie Save (Playwright)

To access replies from Twitter (X) in headless mode, you need to log in manually once using Playwright.

### 📥 Step 1: Install Playwright

Make sure Playwright is installed on your **local machine (not in Docker)**:

```bash
pip install playwright
playwright install
```
📝 This will install the required browser binaries like Chromium.

---

### 🗝️ Step 2: Run Login Script (Once)

Run this script **once outside Docker** to store your Twitter session:

 `python login_save_cookies.py`

```python
from playwright.sync_api import sync_playwright
import os

STATE_PATH = "app/state.json"

def main():
    os.makedirs("app", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("🔑 Silakan login ke X.com secara manual...")
        page.goto("https://x.com/login")
        input("✅ Tekan ENTER setelah selesai login...")
        
        context.storage_state(path=STATE_PATH)
        print(f"✅ Session login berhasil disimpan ke: {STATE_PATH}")
        browser.close()

if __name__ == "__main__":
    main()
```

## 🚀 Deploy
This app is deployed using **FastAPI** and Docker.

### 🐳 Docker Instructions

1. Ensure `app/model.h5`, `app/tokenizer.pkl`, and `app/preprocess.py` are present.
2. Build the Docker image:
   ```bash
   docker build -t nlp-hatespeech .
   ```
3. Run the container (development):
   ```bash
   docker run -it --rm -p 8000:8000 nlp-hatespeech
   ```
4. Run the container (detached):
   ```bash
   docker run -d -p 8000:8000 nlp-hatespeech
   ```

---

### 🧪 API Test Example

```bash
curl "http://localhost:8000/predict?tweet_url=https://x.com/someuser/status/123456789"
```

---

## 📊 Detection Demo

### 🔗 Input (Tweet URL):
```
https://x.com/someuser/status/123456789
```

### 📤 Output (Example):
```json
{
  "tweet_url": "https://x.com/someuser/status/123456789",
  "total_replies": 65,
  "hate_speech_percent": 29.23,
  "non_hate_speech_percent": 70.77
}
```

---

## ✅ Next Steps

✅ Preprocess dataset (cleaning, stemming, alay normalization)
✅ Train Bi-LSTM with Word2Vec
✅ Export model (.h5) and tokenizer
✅ Build FastAPI backend
✅Integrate with Twitter API v2
✅ Deploy with Docker
✅ Build full frontend interface

---

## 👨‍💻 Author

**Finggi Azhara, Jason Patrick ,Muhammad Rafli**  
Natural Language Processing — Politeknik Caltex Riau

---

## 📄 License

Licensed under the MIT License.  
See the `LICENSE` file for full text.