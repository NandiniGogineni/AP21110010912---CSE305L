import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import pickle

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Load the dataset
data_path = 'C:/Users/DELL/Desktop/SE PROJECT/project/bug.csv' 
data = pd.read_csv(data_path)

# Data preprocessing
stop_words = set(stopwords.words('english'))

def clean_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    return ' '.join(filtered_tokens)

data['cleaned_summary'] = data['Summary'].apply(clean_text)

# Splitting the dataset
X_train, X_test, y_train, y_test = train_test_split(data['cleaned_summary'], data['Severity'], test_size=0.2, random_state=42)

# Feature extraction
vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Model building and evaluation
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)
predictions = model.predict(X_test_tfidf)

# Generate and print classification report
report = classification_report(y_test, predictions)
print(report)

# Calculate accuracy
accuracy = accuracy_score(y_test, predictions)
print("Accuracy:", accuracy)

# Confusion Matrix
cm = confusion_matrix(y_test, predictions)
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(cm)
ax.grid(False)
ax.set_xlabel('Predicted outputs', color='black')
ax.set_ylabel('Actual outputs', color='black')
ax.xaxis.set(ticks=range(len(set(y_train))))
ax.yaxis.set(ticks=range(len(set(y_train))))
ax.set_xticklabels(set(y_train))
ax.set_yticklabels(set(y_train))
plt.show()

# Feature importance for each class
feature_names = vectorizer.get_feature_names_out()
for i, class_label in enumerate(model.classes_):
    top_features = np.argsort(model.coef_[i])[-10:]  # Top 10 features
    print(f"Top features for class {class_label}:")
    print([feature_names[j] for j in top_features])

# Save the model to a file
with open('your_model.pkl', 'wb') as file:
    pickle.dump(model, file)

# Save the vectorizer to a file
with open('your_vectorizer.pkl', 'wb') as file:
    pickle.dump(vectorizer, file)
