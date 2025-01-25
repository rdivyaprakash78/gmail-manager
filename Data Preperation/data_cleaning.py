import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
from bs4 import BeautifulSoup
import re


nltk.download('punkt_tab')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))  # You can specify other languages like 'french' or 'spanish'

def remove_stopwords(text):
    words = word_tokenize(text) 
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def clean_email_content(text):
    text = str(text)
    html_pattern = re.compile(r'<[a-zA-Z/][^>]*>')

    def is_html(content):
        """Check if the content is HTML."""
        if isinstance(content, float):
            # Convert float to string if it's a float
            content = str(content)
        
        # Now, content will be a string, so you can safely use search
        return bool(html_pattern.search(content))
    
    # If content is HTML, clean it using BeautifulSoup
    if is_html(text):
        soup = BeautifulSoup(text, "html.parser")
        cleaned_text = soup.get_text()  # Extract plain text from HTML
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Clean extra whitespaces
    else:
        # If plain text, return as is
        cleaned_text = text.strip()

    def remove_space(text):
        """
        Strips unnecessary spaces, newlines, and extra white spaces from the text.
        """
        if isinstance(text, str):  # Ensure the content is a string
            # Remove leading/trailing spaces and newlines
            text = text.strip()
            # Replace multiple spaces with a single space
            text = ' '.join(text.split())
        return text
    
    cleaned_text = remove_space(cleaned_text)

    return cleaned_text


raw_data = pd.read_csv("emails.csv")

raw_data["cleaned_body"] = raw_data["body"].apply(clean_email_content)
raw_data["cleaned_subject"] = raw_data["subject"].apply(clean_email_content)
raw_data["stopwords_removed_body"] = raw_data["cleaned_body"].apply(remove_stopwords)
raw_data["stopwords_removed_subject"] = raw_data["cleaned_subject"].apply(remove_stopwords)


raw_data.drop(columns=['subject', 'body', 'cleaned_body', 'cleaned_subject'], inplace=True)
raw_data.rename(columns={'stopwords_removed_body': 'body', 'stopwords_removed_subject': 'subject'}, inplace=True)

raw_data.to_csv("cleaned_emails.csv", index = True)
 
