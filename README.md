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

This project builds a real-time **Natural Language Processing (NLP)** system that detects **hate speech in reposts or retweets** on Twitter (now X).  
Given a tweet link, the app fetches all replies (reposts/retweets) and classifies whether they contain hate speech using a trained **Bi-LSTM model**.

---

## 📂 Dataset

- **Source**: [Kaggle – Indonesian Abusive and Hate Speech Twitter Text](https://www.kaggle.com/datasets/ilhamfp31/indonesian-abusive-and-hate-speech-twitter-text?select=data.csv)  
- **Format**: CSV  
- **Total Rows**: 13,169 tweets  
- **Language**: Bahasa Indonesia  

### 🔍 Preprocessing Steps:
- Normalize alay words using a custom dictionary
- Lowercasing
- Remove repeated characters and duplicate words
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
- **Saved Format**: `.h5` model and `tokenizer.pkl`

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
tweepy
python-dotenv
pandas
```

### Setup

```bash
# Clone this repository
git clone https://github.com/Keshinryan/NLP-Project
cd NLP-Project
```

---

## 🚀 Deploy

This app is deployed using **FastAPI** and Docker.

### 🔐 Environment Setup

1. Create a `.env` file in the root directory:
   ```env
   TWITTER_BEARER_TOKEN=your_twitter_api_bearer_token_here
   ```

2. Add `.env` to `.gitignore`:
   ```
   .env
   ```

---

### 🐳 Docker Instructions

1. Ensure `app/model.h5`, `app/tokenizer.pkl`, and `app/preprocess.py` are present.
2. Build the Docker image:
   ```bash
   docker build -t nlp-hatespeech .
   ```
3. Run the container (development):
   ```bash
   docker run -it --rm --env-file .env -p 8000:8000 nlp-hatespeech
   ```
4. Run the container (detached):
   ```bash
   docker run -d --env-file .env -p 8000:8000 nlp-hatespeech
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

- [x] Preprocess dataset (cleaning, stemming, alay normalization)
- [x] Train Bi-LSTM with Word2Vec
- [x] Export model (.h5) and tokenizer
- [x] Build FastAPI backend
- [x] Integrate with Twitter API v2
- [x] Deploy with Docker
- [ ] Build full frontend interface

---

## 👨‍💻 Author

**Jason Patrick**  
Natural Language Processing — Politeknik Caltex Riau

---

## 📄 License

Licensed under the MIT License.  
See the `LICENSE` file for full text.