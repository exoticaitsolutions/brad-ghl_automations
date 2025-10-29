import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# from email_setup import send_email_for_token_expire
from gernate_token_file import authenticate_gmail_api
from utils import *
from logging_setup import setup_logging
from dotenv import load_dotenv
# from email_setup import send_email, send_email_for_token_expire


logger = setup_logging()


# Load environment variables from the .env file
load_dotenv(dotenv_path='cred/.env')

# Access the google_credentials path from the .env file

def get_last_email_from_sender(service):
    """Get the last email from a specific sender."""
    try:
        query = 'from:noreply@*'
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            logger.info(f'No messages found from .')
            return None
        
        # Get the most recent message
        message_id = messages[0]['id']
        message = service.users().messages().get(userId='me', id=message_id).execute()

        # Get the email content
        snippet = message['snippet']
        logger.info(f'fethched message: {snippet}')
        return snippet

    except HttpError as error:
        logger.info(f'An error occurred: {error}')
        return None
    

def extract_otp(snippet):
    """Extract the OTP from the email snippet using regex."""
    # Regex pattern for a 6-digit number
    otp_pattern = r'\b\d{6}\b'
    match = re.search(otp_pattern, snippet)
    if match:
        return match.group(0)
    return None

def otp_get_from():
    try:
        service = authenticate_gmail_api()
        last_email = get_last_email_from_sender(service)
        otp = extract_otp(last_email)
        
        if last_email:
            logger.info('OTP fetched successfully')
            return otp
        else:
            logger.info('OTP not fetched successfully')
            return 000000
    except Exception as e:
        # send_email_for_token_expire()
        logger.error(f"An error occurred in otp_get_from: {e}")
