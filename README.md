# Project Name  
## Konnected-GHL-Automation  

---

# Setup Instructions  

## Installation  

### 🐍 Python Installation  
Before proceeding, ensure Python is installed on your system.  
If not, download and install it from [python.org](https://www.python.org/downloads/).  

### 🧩 Setting up a Virtual Environment  
It’s recommended to use a virtual environment.  
You can follow the official [Python venv guide](https://docs.python.org/3/tutorial/venv.html) or use:  

```bash
python -m venv venv
venv\Scripts\activate  # (Windows)
source venv/bin/activate  # (Linux/Mac)
```

---

## Getting Started  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/exoticaitsolutions/brad-ghl_automations.git
```

### 2️⃣ Navigate to the Project Directory  
```bash
cd brad-ghl_automations
```

---

## 📦 Install Dependencies  

### Using requirements.txt  
```bash
pip install -r requirements.txt
```

### Or install individually:
***Selenium***  
```bash
pip install selenium
```

***Webdriver Manager***  
```bash
pip install webdriver-manager
```

***python-dotenv (for environment variables)***  
```bash
pip install python-dotenv
```

***Logging / Utilities***  
```bash
pip install google-auth google-auth-oauthlib
```

---

## ⚙️ Setup `.env` File  

Create a `.env` file in the project root and add your configuration:  

```bash
GOHIGHLEVEL_EMAIL=example@gmail.com
GOHIGHLEVEL_PASSWORD=Example@123
TOKEN_PATH=brad/ghl_automation/cred/token.json
CLIENT_SECRET_PATH=brad/ghl_automation/cred/credentials.json

WORKFLOWS_TO_DELETE=Example Workflow 1,Example Workflow 2
SURVEYS_TO_DELETE=Example Survey 1,Example Survey 2
CUSTOM_FIELD_FOLDERS_TO_DELETE=Example Folder 1,Example Folder 2
CUSTOM_FIELDS_TO_DELETE=Example Custom Field 1,Example Custom Field 2

SUBACCOUNT_IDS=subID1,subID2
```

> ⚠️ Important: Never commit `.env` or credentials to GitHub.  
Add them to `.gitignore` file.

---

## 🔑 Generate `token.json` File (Google API Authentication)  

If you do not have a `token.json` for Gmail API authentication, follow these steps:  

1. **Download Google OAuth Credentials**  
   - Go to [Google Cloud Console](https://console.cloud.google.com/).  
   - Create a **New Project → Enable Gmail API**.  
   - Navigate to **APIs & Services → Credentials → Create Credentials → OAuth Client ID**.  
   - Choose **Desktop App**.  
   - Download the `credentials.json` file.  
   - Place it here:  
     ```
     brad/ghl_automation/cred/credentials.json
     ```

2. **Generate `token.json` Automatically**  
   Run the Gmail authentication script to generate the token file:  
   ```bash
   python login_with_google_api.py
   ```
   or if you have a separate file:
   ```bash
   python generate_token_file.py
   ```

   This will open a browser → log in to your Gmail → authorize access → token.json will be created automatically in:
   ```
   brad/ghl_automation/cred/token.json
   ```

---

## 🧠 Project Structure  

```
brad-ghl_automations/
│
├── brad/
│   └── ghl_automation/
│       ├── cred/
│       │   ├── credentials.json
│       │   └── token.json
│       ├── login_with_google_api.py
│       ├── workflow_deletion.py
│       ├── survey_deletion.py
│       ├── custom_field_deletion.py
│       └── main.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## 🚀 Run Project  

To start the automation, run:  
```bash
python main.py
```

The script will:
- Log in to GoHighLevel using your Google account (OTP automated)
- Navigate through each subaccount ID from `.env`
- Delete workflows, surveys, and custom fields as specified
