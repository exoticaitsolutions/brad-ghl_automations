# custom_field_folder_deletion.py

import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
import os
from dotenv import load_dotenv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from urls import WEBSITE_URL
from webdriver_configration import driver_confrigration

# ------------------ LOGGER SETUP ------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------ LOAD ENV VARIABLES WITH FALLBACKS ------------------
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')  # Adjust if .env is in parent dir
load_dotenv(dotenv_path=dotenv_path)



def delete_custom_fields_for_subaccount(driver, subaccount_id, wait,CUSTOM_FIELD_FOLDERS_TO_DELETE,CUSTOM_FIELDS_TO_DELETE):
    """Delete specific custom field folders and fields for a sub-account."""
    deleted_folders = 0
    deleted_fields = 0
    iframe_switched = False
    try:
        print(f"\nNavigating to Custom Fields page for sub-account: {subaccount_id}")
        driver.get(f"https://app.konnectd.io/v2/location/{subaccount_id}/settings/fields")
        time.sleep(random.uniform(15, 20))
        print("✅ Custom Fields page loaded successfully.")

        # Try switching to iframe (similar to workflows/surveys)
        try:
            iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            driver.switch_to.frame(iframe)
            iframe_switched = True
            print("Switched to iframe for custom fields.")
        except TimeoutException:
            print("No iframe found; staying in main context.")

        # --- Locate Search Input ---
        try:
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search']"))
            )
            print("🔍 Located search input field.")
        except TimeoutException:
            print("❌ Search input not found. Skipping this sub-account.")
            return 0, 0

        # --- Define folders and fields to delete from env ---
        FIELDS_TO_DELETE = CUSTOM_FIELDS_TO_DELETE or []  # From .env, fallback empty
        FOLDERS_TO_DELETE = CUSTOM_FIELD_FOLDERS_TO_DELETE or []  # From .env, fallback empty

        # # ================================================================
        # # 🧩 STEP 1: DELETE FIELDS FIRST (All Fields tab)
        # # ================================================================
        if FIELDS_TO_DELETE:
            print("\n🧩 Starting field deletion process...")
            # Click on All Fields tab
            print("Locating All Fields tab...")
            all_fields_tab = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//div[contains(@class,'text-gray-900') and .//span[normalize-space()='All Fields']]"
            )))
            print("Found the All Fields tab ----------------")
            all_fields_tab.click()
            time.sleep(5)
            print("✅ All Fields tab clicked successfully.")

            for field in FIELDS_TO_DELETE:
                try:
                    # Clear previous text
                    search_input.clear()
                    time.sleep(1)
                    search_input.send_keys(field)
                    time.sleep(5)
                    print(f"Searching for field: {field}")

                    # Find rows and select checkbox in matching row
                    rows = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))
                    selected = False
                    for row in rows:
                        row_text = row.text.lower()
                        if field.lower() in row_text:
                            try:
                                checkbox = row.find_element(By.CSS_SELECTOR, "input[type='checkbox'].cursor-pointer")
                                if not checkbox.is_selected():
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                                    checkbox.click()
                                    print(f"☑️ Selected field checkbox: {field} in row")
                                    selected = True
                                    time.sleep(1)
                                    break
                            except NoSuchElementException:
                                continue

                    if not selected:
                        print(f"⚠️ No checkbox found for field '{field}' — skipping.")
                        continue

                    # Click Bulk Actions
                    bulk_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(@class, 'bg-blue-600') and contains(., 'Bulk Actions')]"
                    )))
                    bulk_btn.click()
                    print("📦 Clicked on Bulk Actions button.")
                    time.sleep(2)

                    # Click Delete option
                    delete_option = wait.until(EC.element_to_be_clickable((
                        By.XPATH,
                        "//div[contains(@class,'flex-grow') and normalize-space(text())='Delete']"
                    )))
                    delete_option.click()
                    print("🗑️ Clicked on Delete option.")
                    time.sleep(2)
                    

                    confirm_ok = wait.until(EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[text()='Ok']"
                    )))
                    confirm_ok.click()
                    print(f"✅ Field deleted: {field}")
                    deleted_fields += 1
                    time.sleep(4)

                except TimeoutException:
                    print(f"⚠️ Timeout deleting field '{field}' — likely not found.")
                except Exception as e:
                    print(f"⚠️ Error deleting field '{field}': {e}")
                finally:
                    # Reset search box
                    try:
                        search_input.clear()
                        time.sleep(1)
                    except:
                        pass

                # =========================
        # STEP 2: DELETE FOLDERS
        # =========================
        if FOLDERS_TO_DELETE:
            print("\n🗂️ Starting folder deletion process...")

            # Click on Folders tab
            folder_tab = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//div[contains(@class,'text-gray-900') and .//span[normalize-space()='Folders']]"
            )))
            folder_tab.click()
            print("✅ Folders tab clicked successfully.")
            time.sleep(2)

            # Locate Folders search input
            try:
                folder_search_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search']"))
                )
                print("🔍 Located Folders search input field.")
            except TimeoutException:
                print("❌ Folders search input not found. Using general search input.")
                folder_search_input = search_input  # fallback

            for folder in FOLDERS_TO_DELETE:
                try:
                    # Clear previous text and search
                    folder_search_input.clear()
                    folder_search_input.send_keys(folder)
                    print(f"Searching for folder: {folder}")
                    time.sleep(2)

                    # Click first 3-dot menu for the folder
                    menu_buttons = wait.until(EC.presence_of_all_elements_located(
                        (By.XPATH, "//button[@id='menu-button']")
                    ))
                    if menu_buttons:
                        wait.until(EC.element_to_be_clickable(menu_buttons[0])).click()
                        print("Clicked 3-dot menu for folder.")
                    time.sleep(1)

                    # Click Delete option
                    delete_button = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//div[contains(@class,'flex-grow') and normalize-space(text())='Delete']"
                    )))
                    delete_button.click()
                    print("Clicked Delete option.")
                    time.sleep(1)

                    # Optional: handle iframe if confirmation modal is inside one
                    try:
                        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
                        driver.switch_to.frame(iframe)
                        print("Switched to iframe for confirmation.")
                    except TimeoutException:
                        pass

                    # Click Ok button in confirmation popup
                    confirm_ok = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "/html/body/div[9]/div[2]/div/div/div[2]/div/div[2]/button[2]")))
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", confirm_ok)
                    try:
                        confirm_ok.click()
                        print(f"✅ Folder deleted: {folder}")
                    except:
                        driver.execute_script("arguments[0].click();", confirm_ok)
                        print(f"✅ Folder deleted via JS click: {folder}")

                    # Switch back to main content if iframe used
                    driver.switch_to.default_content()
                    time.sleep(2)

                    # --- Close the final modal popup ---
                    try:
                        close_button = wait.until(EC.element_to_be_clickable((
                            By.CSS_SELECTOR, "#cmp-apt-modal__btn--close"
                        )))
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", close_button)
                        try:
                            close_button.click()
                            print("✅ Closed the confirmation modal.")
                        except:
                            driver.execute_script("arguments[0].click();", close_button)
                            print("✅ Closed the confirmation modal via JS click.")
                    except TimeoutException:
                        print("⚠️ Close button not found; maybe modal already closed.")

                except Exception as e:
                    print(f"⚠️ Error deleting folder '{folder}': {e}")

                    for row in rows:
                        row_text = row.text.lower()
                        if folder.lower() in row_text:
                            try:
                                # Try checkbox first
                                checkbox = row.find_element(By.CSS_SELECTOR, "input[type='checkbox'].cursor-pointer")
                                if not checkbox.is_selected():
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                                    checkbox.click()
                                    print(f"☑️ Selected folder checkbox: {folder}")
                                    selected = True
                                    time.sleep(1)
                                    break
                            except NoSuchElementException:
                                # Fallback to 3-dot menu (button containing specific SVG)
                                try:
                                    menu_svg = row.find_element(By.XPATH, ".//svg[@class='h-6 w-6' and .//path[@d='M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z']]")
                                    menu_button = menu_svg.find_element(By.XPATH, "..")  # Parent button of SVG
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                                    menu_button.click()
                                    print(f"Clicked 3-dot menu (SVG icon) for folder: {folder}")
                                    time.sleep(2)

                                    # Click Delete in menu
                                    delete_option = wait.until(EC.element_to_be_clickable((
                                        By.XPATH,
                                        "//div[contains(@class,'flex-grow') and normalize-space(text())='Delete']"
                                    )))
                                    delete_option.click()
                                    print("🗑️ Clicked Delete from menu.")
                                    time.sleep(2)

                                    # Confirm with Ok button (specific class)
                                    confirm_ok = wait.until(EC.element_to_be_clickable((
                                        By.XPATH,
                                        "//button[contains(@class,'hl-btn') and contains(@class,'bg-curious-blue-500') and normalize-space(text())='Ok']"
                                    )))
                                    confirm_ok.click()
                                    print(f"✅ Folder deleted via menu: {folder}")
                                    deleted_folders += 1
                                    selected = True
                                    time.sleep(4)
                                    break
                                except NoSuchElementException:
                                    continue

                    if not selected:
                        print(f"⚠️ No selection possible for folder '{folder}' — skipping.")

                except TimeoutException:
                    print(f"⚠️ Timeout deleting folder '{folder}' — likely not found.")
                except Exception as e:
                    print(f"⚠️ Error deleting folder '{folder}': {e}")
                finally:
                    # Reset search box
                    try:
                        folder_search_input.clear()
                        time.sleep(1)
                    except:
                        pass

        print(f"\n✅ Custom Field cleanup completed for {subaccount_id}")
        print(f"🗂️ Folders deleted: {deleted_folders}")
        print(f"🧩 Fields deleted: {deleted_fields}")

    except Exception as e:
        print(f"❌ Error during deletion for {subaccount_id}: {e}")
        driver.save_screenshot(f"error_delete_custom_fields_{subaccount_id}.png")

    finally:
        if iframe_switched:
            driver.switch_to.default_content()

    return deleted_folders, deleted_fields