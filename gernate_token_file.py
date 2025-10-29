from dotenv import load_dotenv
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import Request
from google.auth.transport.requests import Request

# Load environment variables from the .env file


env_path = os.path.join(os.path.dirname(__file__), "cred", ".env")
load_dotenv(dotenv_path=env_path)

# Now read your variables
GOHIGHLEVEL_EMAIL = os.getenv("GOHIGHLEVEL_EMAIL")
GOHIGHLEVEL_PASSWORD = os.getenv("GOHIGHLEVEL_PASSWORD")
TOKEN_PATH = os.getenv("TOKEN_PATH")
CLIENT_SECRET_PATH = os.getenv("CLIENT_SECRET_PATH")


TOKEN_PATH = os.getenv('TOKEN_PATH')

CLIENT_SECRET_PATH = os.getenv('CLIENT_SECRET_PATH')
print(f"CLIENT_SECRET_PATH: {CLIENT_SECRET_PATH}")
# If modifying the API, set SCOPES
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail_api():
    """Authenticate and return the Gmail API service."""
    creds = None

    # The file token.json stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0,access_type='offline', prompt='consent')
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

authenticate_gmail_api()