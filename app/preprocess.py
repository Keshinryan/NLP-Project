# app/preprocess.py
import re
import string
import contractions #type: ignore
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')
nltk.download('stopwords')

alay_dict = pd.read_csv('app/alay_dict.csv', encoding='latin-1', header=None)
alay_dict_map = dict(zip(alay_dict[0], alay_dict[1]))

stop_words = stopwords.words('indonesian')
stop_words.append('yg')

stemmer = PorterStemmer()

def normalize_alay(text):
    return ' '.join([alay_dict_map.get(word, word) for word in text.split()])

def remove_repeated_words(text):
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    return text

def preprocess_text(text):
    text = text.lower()
    text = normalize_alay(text)
    text = contractions.fix(text)
    text = re.sub('[^a-zA-Z\s]', ' ', text)
    text = remove_repeated_words(text)
    text = "".join([word for word in text if word not in string.punctuation])
    text = " ".join([stemmer.stem(word) for word in text.split()])
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if not word.startswith('x') and len(word) > 1 and word not in stop_words]
    return " ".join(tokens)
