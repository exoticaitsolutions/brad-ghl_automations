# workflow_deletion.py
import logging
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _clear_search_via_js(driver, search_element):
    """
    Clear an input reliably by setting its value with JS and dispatching an input event.
    This avoids problems where .clear() or send_keys() doesn't trigger the UI update.
    """
    try:
        driver.execute_script(
            "arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
            search_element,
        )
        # small pause to let UI react
        time.sleep(0.3)
    except Exception as e:
        logger.warning(f"JS clear failed: {e}")
        try:
            search_element.clear()
        except Exception:
            pass


def delete_workflows_for_subaccount(driver, subaccount_id, wait, workflows_to_delete):
    """
    Delete workflows for a specific sub-account.
    - re-finds the search input each loop
    - clears it via JS to ensure the app refreshes the list
    """
    deleted_count = 0
    try:
        logger.info(f"Navigating to workflows for sub-account: {subaccount_id}")
        driver.get(f"https://app.konnectd.io/v2/location/{subaccount_id}/automation/workflows?listTab=all")
        logger.info("URL loaded for workflows.")
        # initial wait
        time.sleep(random.uniform(8, 12))

        # switch to iframe if present
        try:
            iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            driver.switch_to.frame(iframe)
            logger.info("Switched to iframe.")
        except TimeoutException:
            logger.info("No iframe found, continuing in main context.")

        for workflow_name in workflows_to_delete:
            logger.info(f"--- Processing workflow: {workflow_name} ---")

            # re-find the search input for each workflow (avoid stale element)
            try:
                search_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input.n-input__input-el, input[type='search'], input[placeholder*='Search']"))
                )
            except TimeoutException:
                logger.warning("Search input not found; trying alternate selector and continuing.")
                # try alternate simple selector
                try:
                    search_input = driver.find_element(By.CSS_SELECTOR, "input.n-input__input-el")
                except Exception:
                    logger.error("Cannot locate search input. Skipping this workflow.")
                    continue

            # Clear input reliably
            _clear_search_via_js(driver, search_input)
            # ensure list resets
            try:
                search_input.send_keys(Keys.ENTER)
            except Exception:
                pass
            time.sleep(0.4)

            # Enter workflow name and search
            try:
                search_input.send_keys(workflow_name)
                search_input.send_keys(Keys.ENTER)
            except Exception:
                # fallback: set value via JS and dispatch input + enter
                driver.execute_script(
                    "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input',{ bubbles: true }));",
                    search_input,
                    workflow_name,
                )
                try:
                    search_input.send_keys(Keys.ENTER)
                except Exception:
                    pass

            # wait briefly for list to filter
            time.sleep(2)

            # ensure table is present
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.n-data-table.n-data-table--bottom-bordered, tbody.n-data-table-tbody")
                    )
                )
            except TimeoutException:
                logger.info(f"Table not found or no results for '{workflow_name}'. Clearing and continuing.")
                # clear before next iteration
                _clear_search_via_js(driver, search_input)
                try:
                    search_input.send_keys(Keys.ENTER)
                except Exception:
                    pass
                time.sleep(0.5)
                continue

            # find rows
            try:
                tbody = driver.find_element(By.CSS_SELECTOR, "tbody.n-data-table-tbody[data-n-id]")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
            except Exception:
                rows = []

            logger.info(f"Found {len(rows)} row(s) for '{workflow_name}'")

            if not rows:
                # none found => maybe already deleted
                _clear_search_via_js(driver, search_input)
                try:
                    search_input.send_keys(Keys.ENTER)
                except Exception:
                    pass
                time.sleep(0.5)
                continue

            # iterate rows and attempt deletion
            for i, row in enumerate(rows, start=1):
                try:
                    # try to open actions for the row (best-effort; selectors vary)
                    try:
                        actions_btn = row.find_element(By.CSS_SELECTOR, "td.actions-class-column button, button.n-button")
                    except Exception:
                        # fallback: find a button in the row
                        actions_btn = row.find_element(By.XPATH, ".//button[.//svg or contains(., 'Actions')][1]")

                    # bring into view and click
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", actions_btn)
                    ActionChains(driver).move_to_element(actions_btn).pause(0.2).click().perform()
                    time.sleep(0.7)

                    # click Delete Workflow option (text must match UI)
                    delete_option = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@data-dropdown-option='true' and (text()='Delete Workflow' or contains(text(),'Delete'))]"))
                    )
                    driver.execute_script("arguments[0].click();", delete_option)
                    time.sleep(0.6)

                    # confirm - type CONFIRM if required
                    try:
                        confirm_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'CONFIRM')]")))
                        confirm_input.clear()
                        confirm_input.send_keys("CONFIRM")
                    except TimeoutException:
                        # some dialogs may not require typing
                        pass

                    # click Delete confirm button
                    delete_confirm_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Delete') and not(contains(., 'Cancel'))]"))
                    )
                    driver.execute_script("arguments[0].click();", delete_confirm_button)

                    # wait until modal disappears
                    wait.until_not(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'modal') or contains(@class,'dialog')]")))
                    logger.info(f"Deleted workflow '{workflow_name}' (row {i})")
                    deleted_count += 1

                    # short pause to let table update
                    time.sleep(1.2)

                except Exception as e:
                    logger.warning(f"Failed deleting row {i} for '{workflow_name}': {e}")
                    # continue with next row if one row fails
                    continue

            # Clear search before next workflow (very important)
            try:
                # re-find input (in case DOM changed)
                search_input = driver.find_element(By.CSS_SELECTOR, "input.n-input__input-el, input[type='search'], input[placeholder*='Search']")
                _clear_search_via_js(driver, search_input)
                try:
                    search_input.send_keys(Keys.ENTER)
                except Exception:
                    pass
            except Exception:
                logger.debug("Could not re-find search input to clear; continuing.")

            time.sleep(0.6)

        # switch back to default content
        try:
            driver.switch_to.default_content()
        except Exception:
            pass

        logger.info(f"Completed workflow deletion for sub-account '{subaccount_id}'. Total deleted: {deleted_count}")

    except Exception as exc:
        logger.error(f"Error deleting workflows for {subaccount_id}: {exc}", exc_info=True)
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        if driver:
            driver.save_screenshot(f"workflow_error_{subaccount_id}.png")

    return deleted_count