from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from preprocess import preprocess
import joblib

X, y, vectorizer = preprocess()

Xtrain, Xtest, ytrain, ytest = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


model = LogisticRegression(max_iter=1000)
model.fit(Xtrain, ytrain)

ypred = model.predict(Xtest)


joblib.dump(model, 'spam_model.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')


print("Accuracy:", accuracy_score(ytest, ypred))
print("Classification Report:\n", classification_report(ytest, ypred))

