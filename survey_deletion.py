import os
import time
import logging
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# === Screenshot Directory ===
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(driver, filename_suffix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SCREENSHOT_DIR, f"{filename_suffix}_{timestamp}.png")
    driver.save_screenshot(filepath)
    logger.info(f"📸 Screenshot saved: {filepath}")
    return filepath


# ------------------ PAGE NAVIGATION ------------------
def navigate_to_survey_page(driver, subaccount_id):
    """Navigate to the survey builder page for a specific subaccount."""
    try:
        survey_url = f"https://app.konnectd.io/v2/location/{subaccount_id}/survey-builder/main"
        driver.get(survey_url)
        wait = WebDriverWait(driver, 25)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.n-data-table")))
        logger.info(f"✅ Navigated to Survey Builder page for subaccount: {subaccount_id}")
    except TimeoutException as te:
        logger.error(f"⏰ Timeout navigating to survey page for {subaccount_id}: {str(te)}")
        take_screenshot(driver, f"survey_nav_error_{subaccount_id}")
        raise


# ------------------ SEARCH + DELETE SURVEY ------------------
def search_and_delete_survey(driver, survey_name, max_retries=3):
    """Search for a survey and delete it."""
    wait = WebDriverWait(driver, 15)
    try:
        # Wait and locate search box
        search_box = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input.n-input__input-el[placeholder='Search for surveys']")
            )
        )
        search_box.clear()
        search_box.send_keys(survey_name)
        search_box.send_keys(Keys.ENTER)
        time.sleep(2)

        # Check if survey appears in the list
        survey_row = wait.until(
            EC.presence_of_element_located((By.XPATH, f"//tbody//tr[contains(., '{survey_name}')]"))
        )
        logger.info(f"📄 Found survey: {survey_name}")

        # --- Click on 3-dot Actions button ---
        try:
            three_dot_button = survey_row.find_element(By.XPATH, ".//button[contains(@class,'n-button')]")
            driver.execute_script("arguments[0].click();", three_dot_button)
        except Exception:
            ActionChains(driver).move_to_element(survey_row).perform()
            three_dot_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class,'n-button')]"))
            )
            driver.execute_script("arguments[0].click();", three_dot_button)
        time.sleep(1)

        # --- Click on Delete option in dropdown ---
        delete_option = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'n-dropdown-option') and text()='Delete']")
            )
        )
        driver.execute_script("arguments[0].click();", delete_option)
        logger.info("🗑️ Clicked delete option")
        time.sleep(1.5)

        # --- Confirm Deletion ---
        for attempt in range(max_retries):
            try:
                confirm_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Delete')]"))
                )
                driver.execute_script("arguments[0].click();", confirm_btn)
                logger.info(f"✅ Deleted survey: {survey_name}")
                break
            except (TimeoutException, ElementClickInterceptedException) as e:
                logger.warning(f"Retry {attempt + 1}/{max_retries} confirming delete: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1.5)

        # Wait until survey row disappears
        wait.until(EC.invisibility_of_element_located((By.XPATH, f"//tr[contains(., '{survey_name}')]")))
        return True

    except TimeoutException:
        logger.warning(f"🚫 Survey not found or already deleted: {survey_name}")
        return False

    except Exception as e:
        logger.error(f"💥 Unexpected error deleting {survey_name}: {str(e)}", exc_info=True)
        take_screenshot(driver, f"survey_delete_error_{survey_name.replace(' ', '_')}")
        return False

    finally:
        # Clear search field before next survey
        try:
            search_box = driver.find_element(
                By.CSS_SELECTOR, "input.n-input__input-el[placeholder='Search for surveys']"
            )
            search_box.send_keys(Keys.CONTROL, "a")
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(1)
        except Exception as clear_err:
            logger.warning(f"⚠️ Could not clear search field after {survey_name}: {clear_err}")


# ------------------ DELETE SURVEYS FOR SUBACCOUNT ------------------
def delete_surveys_from_subaccount(driver, subaccount_id, surveys_to_delete):
    """Main deletion handler for one subaccount."""
    success_count = 0
    logger.info(f"🚀 Starting survey deletion for subaccount: {subaccount_id}")

    try:
        navigate_to_survey_page(driver, subaccount_id)
        for survey_name in surveys_to_delete:
            if search_and_delete_survey(driver, survey_name):
                success_count += 1

        logger.info(f"🎯 Subaccount {subaccount_id}: {success_count}/{len(surveys_to_delete)} deleted.")
        return success_count

    except Exception as e:
        logger.error(f"💣 Error processing subaccount {subaccount_id}: {str(e)}", exc_info=True)
        take_screenshot(driver, f"subaccount_error_{subaccount_id}")
        return success_count


# ------------------ MULTI SUBACCOUNT RUNNER ------------------
def main_survey_deletion(driver, subaccounts_list, surveys_to_delete):
    """Run survey deletion for all subaccounts."""
    start_time = datetime.now()
    total_deleted = 0
    logger.info("🚀 Starting survey deletion automation...")

    for subaccount in subaccounts_list:
        total_deleted += delete_surveys_from_subaccount(driver, subaccount, surveys_to_delete)

    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"✅ Survey deletion completed. Total deleted: {total_deleted}. Duration: {duration:.2f}s")
