import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "cred", ".env")
load_dotenv(dotenv_path=dotenv_path)

# Global environment variables
GOHIGHLEVEL_EMAIL = os.getenv("GOHIGHLEVEL_EMAIL", "")
GOHIGHLEVEL_PASSWORD = os.getenv("GOHIGHLEVEL_PASSWORD", "")
SUBACCOUNT_IDS = [sid.strip() for sid in os.getenv("SUBACCOUNT_IDS", "").split(",") if sid.strip()]

WORKFLOWS_TO_DELETE = [x.strip() for x in os.getenv("WORKFLOWS_TO_DELETE", "").split(",") if x.strip()]
SURVEYS_TO_DELETE = [x.strip() for x in os.getenv("SURVEYS_TO_DELETE", "").split(",") if x.strip()]
CUSTOM_FIELD_FOLDERS_TO_DELETE = [x.strip() for x in os.getenv("CUSTOM_FIELD_FOLDERS_TO_DELETE", "").split(",") if x.strip()]
CUSTOM_FIELDS_TO_DELETE = [x.strip() for x in os.getenv("CUSTOM_FIELDS_TO_DELETE", "").split(",") if x.strip()]


print(GOHIGHLEVEL_EMAIL, GOHIGHLEVEL_PASSWORD, SUBACCOUNT_IDS, WORKFLOWS_TO_DELETE, SURVEYS_TO_DELETE, CUSTOM_FIELD_FOLDERS_TO_DELETE, CUSTOM_FIELDS_TO_DELETE)