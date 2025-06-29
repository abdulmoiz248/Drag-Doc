import joblib
from preprocess import cleanText, removeHtmlAndLower

model = joblib.load('spam_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

while True:
    userInput = input("Enter your email content (or type 'exit' to quit): ")
    if userInput.lower() == 'exit':
        break

    cleaned = cleanText(removeHtmlAndLower(userInput))
    vectorized = vectorizer.transform([cleaned])
    prediction = model.predict(vectorized)

    print("Result:", "🚨 Spam" if prediction[0] == 1 else "✅ Not Spam")
