import os
import time
import random
import logging
from datetime import datetime
from dotenv import load_dotenv

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# === Local Imports ===
from webdriver_configration import driver_confrigration
from urls import WEBSITE_URL
from login_with_google_api import otp_get_from
from workflow_deletion import delete_workflows_for_subaccount
from survey_deletion import delete_surveys_from_subaccount
from custom_field_folder_deletion import delete_custom_fields_for_subaccount
from config import (
    GOHIGHLEVEL_EMAIL,
    GOHIGHLEVEL_PASSWORD,
    SUBACCOUNT_IDS,
    WORKFLOWS_TO_DELETE,
    SURVEYS_TO_DELETE,
    CUSTOM_FIELD_FOLDERS_TO_DELETE,
    CUSTOM_FIELDS_TO_DELETE,
)

from helper import clear_search_field
from workflow_deletion import delete_workflows_for_subaccount


# ------------------ LOGGER SETUP ------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# # ------------------ LOAD ENV VARIABLES ------------------
# dotenv_path = os.path.join(os.path.dirname(__file__), "cred", ".env")
# load_dotenv(dotenv_path=dotenv_path)

# GOHIGHLEVEL_EMAIL = os.getenv("GOHIGHLEVEL_EMAIL", "")
# GOHIGHLEVEL_PASSWORD = os.getenv("GOHIGHLEVEL_PASSWORD", "")

# WORKFLOWS_TO_DELETE = [x.strip() for x in os.getenv("WORKFLOWS_TO_DELETE", "").split(",") if x.strip()]
# SURVEYS_TO_DELETE = [x.strip() for x in os.getenv("SURVEYS_TO_DELETE", "").split(",") if x.strip()]
# CUSTOM_FIELD_FOLDERS_TO_DELETE = [x.strip() for x in os.getenv("CUSTOM_FIELD_FOLDERS_TO_DELETE", "").split(",") if x.strip()]
# CUSTOM_FIELDS_TO_DELETE = [x.strip() for x in os.getenv("CUSTOM_FIELDS_TO_DELETE", "").split(",") if x.strip()]

# Parse subaccount IDs
# SUBACCOUNT_IDS = os.getenv("SUBACCOUNT_IDS", "")



# ------------------ HELPER FUNCTION ------------------
# def clear_search_field(search_input):
#     """Clear a search input field robustly."""
#     try:
#         search_input.click()
#         time.sleep(0.3)
#         search_input.send_keys(Keys.CONTROL + "a")
#         search_input.send_keys(Keys.DELETE)
#         time.sleep(0.3)
#         if search_input.get_attribute("value"):
#             search_input.clear()
#         print("✅ Search field cleared.")
#     except Exception as e:
#         print(f"⚠️ Failed to clear search field: {e}")


# ------------------ MAIN AUTOMATION FUNCTION ------------------
def scrapping():
    """Logs into GoHighLevel and deletes workflows, surveys, and custom fields for all sub-accounts."""
    print("\n🚀 Starting Automation Script...")
    start_time = datetime.now()
    driver = None

    try:
        # === Validate Configuration ===
        if not GOHIGHLEVEL_EMAIL or not GOHIGHLEVEL_PASSWORD:
            print("❌ Missing login credentials in .env file.")
            return
        # if not subaccount_ids:
        #     print("❌ No Subaccount IDs found in .env file.")
        #     return

        # print(f"✅ Loaded Sub-Accounts: {subaccount_ids}")

        # === Launch Chrome Driver ===
        print("🌐 Launching ChromeDriver...")
        driver = driver_confrigration()
        wait = WebDriverWait(driver, 30)
        print("✅ ChromeDriver initialized successfully!")

        # === Login ===
        print("🔑 Navigating to login page...")
        driver.get(WEBSITE_URL)

        email_input = wait.until(EC.element_to_be_clickable((By.ID, "email")))
        email_input.send_keys(GOHIGHLEVEL_EMAIL)

        password_input = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        password_input.send_keys(GOHIGHLEVEL_PASSWORD)

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(., "Sign in")]')))
        login_button.click()
        print("✅ Credentials submitted.")

        # === OTP Verification ===
        send_code_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Send Security Code")]')))
        send_code_btn.click()
        print("📩 OTP requested...")

        time.sleep(10)
        otp_code = otp_get_from()

        if not otp_code:
            print("❌ Could not fetch OTP from Gmail. Exiting.")
            return

        print(f"✅ OTP received: {otp_code}")
        otp_inputs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "otp-input")))
        for i, digit in enumerate(str(otp_code)):
            otp_inputs[i].send_keys(digit)

        print("🔓 Logging into dashboard...")
        time.sleep(random.uniform(10, 12))

        # === Run Deletion Tasks ===
        total_workflow_deleted = 0
        total_survey_deleted = 0
        total_folder_deleted = 0
        total_field_deleted = 0
        for subaccount_id in SUBACCOUNT_IDS:
            print(f"\n===============================")
            print(f"🧭 Processing Sub-Account: {subaccount_id}")
            print(f"===============================")

            # 1️⃣ Workflows
            wf_deleted = delete_workflows_for_subaccount(driver, subaccount_id, wait, WORKFLOWS_TO_DELETE)
            total_workflow_deleted += wf_deleted

            # 2️⃣ Surveys
            survey_deleted = delete_surveys_from_subaccount(driver, subaccount_id, SURVEYS_TO_DELETE)
            total_survey_deleted += survey_deleted

            # 3️⃣ Custom Fields
            folder_deleted, field_deleted = delete_custom_fields_for_subaccount(
                driver,
                subaccount_id,
                wait,
                CUSTOM_FIELD_FOLDERS_TO_DELETE,
                CUSTOM_FIELDS_TO_DELETE
            )
            total_folder_deleted += folder_deleted
            total_field_deleted += field_deleted

        # === Summary ===
        print("\n🎯 === AUTOMATION SUMMARY ===")
        print(f"🧩 Workflows deleted: {total_workflow_deleted}")
        print(f"📝 Surveys deleted: {total_survey_deleted}")
        print(f"📁 Custom field folders deleted: {total_folder_deleted}")
        print(f"🏷️ Custom fields deleted: {total_field_deleted}")
        print("===============================")
        print("✅ All automation tasks completed successfully!")

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        if driver:
            driver.save_screenshot("unexpected_error.png")
            print("🖼️ Screenshot saved as unexpected_error.png")

    finally:
        if driver:
            # input("\nPress Enter to close browser...")
            driver.quit()
        end_time = datetime.now()
        print(f"\n⏰ Finished at: {end_time}")
        print(f"⏱️ Total Duration: {end_time - start_time}")


# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    print("🏁 Running main.py ...")
    scrapping()
    print("✅ Script execution ended.")
