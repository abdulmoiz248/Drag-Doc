from merge import merged_Dataset
from bs4 import BeautifulSoup
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer

def removeHtmlAndLower(text):
    text = text.lower()
    text = BeautifulSoup(text, "html.parser").get_text()
    return text

def cleanText(text):
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text

def vectorizeTexts(texts):
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words='english',
        max_features=3000
    )
    X = vectorizer.fit_transform(texts)
    return X, vectorizer

def preprocess():
    df = merged_Dataset()
    df['text'] = df['text'].apply(removeHtmlAndLower).apply(cleanText)
    X, vectorizer = vectorizeTexts(df['text'])
    return X, df['target'], vectorizer
