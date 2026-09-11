from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]

TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def get_gmail_service():

    creds = None

    # Load existing OAuth token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Refresh expired token
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # No valid credentials → start OAuth browser flow
    if not creds or not creds.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES
        )

        creds = flow.run_local_server(
            port=0
        )

        # Save token for future runs
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    # Create Gmail API service
    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service