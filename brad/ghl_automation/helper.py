from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def clear_search_field(driver):
    """Clear the search input field before next search."""
    try:
        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search']")
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.DELETE)
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Could not clear search field: {e}")
