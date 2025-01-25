# auth.py
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_user(client_secrets_file='credentials.json'):
    """Authenticate the user and return the credentials."""
    creds = None

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
        creds = flow.run_local_server(port=8080)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def main():
    """Return the authenticated Gmail API service object."""
    creds = authenticate_user()
    service = build('gmail', 'v1', credentials=creds)
    return service
