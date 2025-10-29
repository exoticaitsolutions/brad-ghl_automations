import re
import time
import traceback

from datetime import datetime

# from insert_data_bigquery import insert_data_into_workflow_actions_stats, insert_data_in_work_flow_actions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from logging_setup import setup_logging


def clean_and_convert(value):
    if isinstance(value, str):
        # Extract numeric value using regex, allowing for decimal points
        match = re.search(r'\d+(\.\d+)?', value)
        return match.group() if match else 0
    return round(value)

def get_current_utc_time():
    # Get the current system time in UTC
    current_utc_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return current_utc_time

# # Example usage
LastUpdatedTime = get_current_utc_time()

logger = setup_logging()

# modified date by 14-may-2025
def process_email(driver):
    email_stats_data = {}
    logger.info("Starting the scrapping process for email")
    stats = driver.find_element(By.XPATH, '//*[@id="cmp-email-act__tab--stats"]')
    # stats.click()
    driver.execute_script("arguments[0].click();", stats)
    time.sleep(10)

    details = driver.find_element(By.XPATH, '//div[@id="cmp-email-stats__link--details-delivered"]/a')
    driver.execute_script("arguments[0].click();", details)
    time.sleep(15)
    
    stats_email_count_total_click =  driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-total")
    stats_email_count_total_click.click()
    time.sleep(15)
    stats_email_total_count =  stats_email_count_total_click.text
    
    stats_email_percent_delivered_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-delivered")
    stats_email_percent_delivered_click.click()
    time.sleep(15)
    stats_email_percent_delivered = stats_email_percent_delivered_click.text

    stats_email_percent_clicked_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-clicked")
    stats_email_percent_clicked_click.click()
    time.sleep(15)
    stats_email_percent_clicked = stats_email_percent_clicked_click.text

    stats_email_percent_opened_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-opened")
    stats_email_percent_opened_click.click()
    time.sleep(15)
    stats_email_percent_opened = stats_email_percent_opened_click.text

    stats_email_percent_replied_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-replied")
    stats_email_percent_replied_click.click()
    time.sleep(15)

    stats_email_percent_replied = stats_email_percent_replied_click.text

    stats_email_percent_bounced_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-permanentFail")
    stats_email_percent_bounced_click.click()                      
    time.sleep(15)
    stats_email_percent_bounced = stats_email_percent_bounced_click.text

    stats_email_percent_unsubscribed_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-unsubscribed")
    stats_email_percent_unsubscribed_click.click()
    time.sleep(15)
    stats_email_percent_unsubscribed = stats_email_percent_unsubscribed_click.text

    email_stats_data = {
        "last_updated_date": get_current_utc_time(),  # Example timestamp
        
        "stats_email_total_count": stats_email_total_count,
        # stats_email_total_count_click =  driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/div/div[2]/div[3]/div/div/div[2]/div/div[3]/label')
        "stats_email_percent_delivered": stats_email_percent_delivered,
        # "stats_email_count_delivered": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/div/div[2]/div[3]/div/div/div[2]/div/div[3]/label').text,
        "stats_email_percent_clicked": stats_email_percent_clicked,
        # "stats_email_count_clicked": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/div/div[2]/div[3]/div/div/div[2]/div/div[3]/label').text,
        "stats_email_percent_opened": stats_email_percent_opened,
        # "stats_email_count_opened": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/div/div[2]/div[3]/div/div/div[2]/div/div[3]/label').text,
        "stats_email_percent_replied": stats_email_percent_replied,
        # "stats_email_count_replied": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/div/div[2]/div[3]/div/div/div[2]/div/div[3]/label').text,
        "stats_email_percent_bounced": stats_email_percent_bounced,
        # "stats_email_count_bounced": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/div/div[2]/div[3]/div/div/div[2]/div/div[3]/label').text,
        "stats_email_percent_unsubscribed": stats_email_percent_unsubscribed,
        # "stats_email_count_unsubscribed": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/div/div[2]/div[3]/div/div/div[2]/div/div[3]/label').text,
        "stats_email_percent_rejected": "",
        # "stats_email_count_rejected": "",
        "stats_email_percent_complained": "",
        # "stats_email_count_complained": "",
    }
    logger.info(f"email_stats_data: {email_stats_data}")

    # Apply cleaning to specific fields
    fields_to_clean = [key for key in email_stats_data if 'count' in key or 'percent' in key]
    for field in fields_to_clean:
        email_stats_data[field] = clean_and_convert(email_stats_data[field])

    logger.info(f"Cleaned email_stats_data: {email_stats_data}")

    # Close the details view
    
    driver.find_element(By.XPATH, "//*[name()='svg' and @class='w-6 h-6 cursor-pointer']").click()
    logger.info("click on this x button ")
    driver.find_element(By.XPATH, '//*[@id="cancel-button-aside-section"]/span').click()
    logger.info("click on this cancel  button ")
    logger.info("Completed SMS scrapping process.")

    time.sleep(15)

    return email_stats_data

def process_sms(driver):
    sms_stats_data = {}
    logger.info("Starting the scrapping process process sms ")
    stats = driver.find_element(By.ID, 'cmp-sms-act__tab--stats')
    # stats.click()
    driver.execute_script("arguments[0].click();", stats)
    time.sleep(10)

    details = driver.find_element(By.ID, 'cmp-sms-stats__link--details-delivered')
    driver.execute_script("arguments[0].click();", details)
    time.sleep(15)

    logger.info("start for clicking box")
    
    stats_sms_count_total_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-total")
    stats_sms_count_total_click.click()
    time.sleep(15)
    stats_sms_count_total = stats_sms_count_total_click.text
    
    # stats_sms_total_count_click = driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/form/div[2]/div[2]/div/div/div[2]/div/div[3]/label')
    # stats_sms_total_count_click.click()
    # time.sleep(15)
    # stats_sms_total_count = stats_sms_total_count_click.text

    stats_sms_percent_delivered_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-delivered")
    stats_sms_percent_delivered_click.click()
    time.sleep(15)
    stats_sms_percent_delivered = stats_sms_percent_delivered_click.text

    stats_sms_percent_clicked_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-clicked")
    stats_sms_percent_clicked_click.click()
    time.sleep(15)
    stats_sms_percent_clicked = stats_sms_percent_clicked_click.text
    stats_sms_percent_failed_click = driver.find_element(By.ID, "cmp-stat-modal__btn--stat-card-unfulfilled")
    stats_sms_percent_failed_click.click()
    time.sleep(15)
    stats_sms_percent_failed = stats_sms_percent_failed_click.text

    sms_stats_data = {
        "stats_sms_count_total": stats_sms_count_total,
        # "stats_sms_total_count": stats_sms_total_count,

        "stats_sms_percent_delivered": stats_sms_percent_delivered,
        # "stats_sms_count_delivered": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/form/div[2]/div[2]/div/div/div[2]/div/div[3]/label').text,

        "stats_sms_percent_clicked": stats_sms_percent_clicked,
        # "stats_sms_count_clicked": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/form/div[2]/div[2]/div/div/div[2]/div/div[3]/label').text,

        "stats_sms_percent_failed": stats_sms_percent_failed,
        # "stats_sms_count_failed": driver.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[2]/div/fieldset/form/div[2]/div[2]/div/div/div[2]/div/div[3]/label').text
    }

    logger.info(f"Sms Stats data: {sms_stats_data}")

    # Apply cleaning to specific fields
    fields_to_clean = [key for key in sms_stats_data if 'count' in key or 'percent' in key]

    for field in fields_to_clean:
        sms_stats_data[field] = clean_and_convert(sms_stats_data[field])

    logger.info(f"Sms Stats data cleaned :{sms_stats_data}")


    # Close the details view
    driver.find_element(By.XPATH, "//*[name()='svg' and @class='w-6 h-6 cursor-pointer']").click()
    driver.find_element(By.XPATH, '//*[@id="cancel-button-aside-section"]/span').click()
    time.sleep(15)
    logger.info("Completed SMS scrapping process.")
    return sms_stats_data

def scrapp_email_sms(driver, url):
    logger.info("Starting scrapp_email_sms.")
    action_type = ''
    try:
    
        logger.info(f"Navigating to URL: {url}")
        driver.get(url)
        time.sleep(85)

        # Switch to the correct iframe
        logger.info("Switching to iframe 'workflow-builder'.")
        driver.switch_to.frame('workflow-builder')
        time.sleep(20)

        # # Zoom out to view the full workflow
        # logger.info("Zooming out to view the workflow diagram.")
        # zoom_out_button = driver.find_element(By.ID, "workflow-fit-to-screen")
        # for _ in range(13):
        #     driver.execute_script("arguments[0].click();", zoom_out_button)
        #     time.sleep(3)
            
        try:
            logger.info("Wait for fit to screen button")
            logger.info("wait for fit to screen button----------->>>>")
            wait = WebDriverWait(driver, 20)
            fit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="workflow-fit-to-screen"]')))
            logger.info("button found------------->>>>")
            time.sleep(2)
            driver.execute_script("arguments[0].click();", fit_button)
            logger.info("Click on fit screen to view the workflow diagram.")
            logger.info(" Clicked 'Fit to Screen' button.")
            time.sleep(8) 
        except Exception as e:
            logger.error(f"Button not found{e}")


        # Click on the 'All Data' section
        # logger.info("Clicking on the 'All Data' section.")
        # all_data = driver.find_element(By.XPATH, '//*[@id="main"]/div[1]/div/div[4]/div[1]/div[2]')
        # # all_data.click()
        # driver.execute_script("arguments[0].click();", all_data)
        # time.sleep(10)

        # Locate all boxes
        all_data_count_boxes = driver.find_elements(By.XPATH, '//*[@id="main"]/div[1]/div/div[1]/div/div/div[2]/div')

        logger.info(f"Total boxes found: {len(all_data_count_boxes)}")

        for index, box in enumerate(all_data_count_boxes):
            action_type = ''
            name = ''
            step = ''
            name = box.text.strip()
            # processed_name = re.sub(r'^\d+\s*', '', name.strip())  # Remove leading digits and whitespace
            processed_name = name.strip()
            processed_name = re.sub(r'^\d+\s*\n', '', processed_name)
            logger.info(f"Checking box #{index + 1} name -- {processed_name}")
            email_stats_data = {}
            sms_stats_data = {}
          
            # match = re.match(r'^Wait$', processed_name, re.IGNORECASE)
            if re.search(r'\bWait\b', processed_name, re.IGNORECASE):
                if re.match(r'^\s*\d*\s*Wait\s*$', processed_name, re.IGNORECASE):
                    name = "Wait"
                else:
                    name = processed_name
            else:
                name = processed_name
                
            box_class = box.get_attribute('class')

            if name == 'END' or 'vue-flow__node-branch' in box_class:
                logger.info(f"Skipping box #{index + 1} due to name 'END' or invalid class.")
                continue
            if name == 'Add New Trigger':
                logger.info(f"Skipping box #{index + 1} due to name Add new Trigger button.")
                continue

            # Try to click the box
            try:
                time.sleep(5)
                driver.execute_script("arguments[0].click();", box)
                time.sleep(20)
                # box.click()
                # time.sleep(10)
                # Extract action type after clicking the box
                action_type_xpath = box.find_element(By.XPATH, '//*[@id="main"]/section/div/div/div[1]/div[1]/div/header/div[1]/div[1]/h2')
                action_type = action_type_xpath.text.strip()
                url = driver.current_url
                step = index + 1
                if 'Trigger' in name:
                    name = 'Trigger'
                rows_to_insert = [
                {
                    "id": 0,
                    "workflow_id": url.split('/')[-1],  # Extract UUID from the URL
                    "name": name,
                    "step": step,
                    "type": action_type,
                    "last_updated_date":get_current_utc_time()
                }
                ]
                workflow_action_id = insert_data_in_work_flow_actions(rows_to_insert)
                
                if action_type == "Sms":
                    sms_stats_data = process_sms(driver)
                elif action_type == "Email":
                    email_stats_data = process_email(driver)
                if action_type == "Sms" or action_type == "Email":
                    logger.info("start function for data inserting")
                    insert_data_into_workflow_actions_stats(workflow_action_id, email_stats_data, sms_stats_data)
                    
                else:
                    # Close the panel after processing
                    back = driver.find_element(By.XPATH, './/*[@aria-label="Close panel"]')
                    # back.click()
                    time.sleep(15)
                    driver.execute_script("arguments[0].click();", back)
                    time.sleep(15)

            except Exception:
                logger.error("No element found\n" + traceback.format_exc())
                continue

    except Exception as e:
        logger.error(f"An error occurred in scrapp_email_sms{e}")


def click_on_folder_or_file(driver,row):
    logger.info("----------------------------- >> Checking for file and folder")
    clicked_name = row.find_element(By.CSS_SELECTOR, "span.flex.group p")
    logger.info("------------------------->>>> found row for file and folder...........")
    logger.info(f"folder clicked_name : {clicked_name.text}")
    driver.execute_script("arguments[0].click();", clicked_name)
    time.sleep(15)
    click_url = driver.current_url 
    return click_url


main_publish_list = []
main_folder_list = []

def status_check_folder_or_not(driver):
    logger.info("Checking file status.")
    logger.info("Checking file status.")
    global main_folder_list
    global main_publish_list

    try:
        logger.info("workflow table search")
        tbody = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'n-data-table-tbody'))
        )
        logger.info("")
        logger.info("workflow table Found -------------------------------")
        # Scroll the page to make sure elements are loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
        logger.info("--------------  Scrolling")
        time.sleep(7)

        # Click dropdown to select "50 / page" option
        try:
            icon_arrow = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//i[contains(@class, "n-base-icon n-base-suffix__arrow")]'))
            )
            icon_arrow.click()
            time.sleep(5)
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[contains(@class, "n-base-select-option__content") and text()="50 / page"]')
                )
            )
            option.click()
            time.sleep(5)
            logger.info("Rows per page set to 50.")
            
        except Exception as e:
            logger.info(f"Dropdown for rows per page not found or clickable: {e}")

         # Process rows in the table
        rows = tbody.find_elements(By.CLASS_NAME, 'n-data-table-tr')
        logger.info(f"Number of Rows Found: {len(rows)}")
        logger.info("Number of Rows Found : ", len(rows))
        
        for i in range(len(rows)):
            current_url = driver.current_url
            tbody = driver.find_element(By.CLASS_NAME, 'n-data-table-tbody')
            rows = tbody.find_elements(By.CLASS_NAME, 'n-data-table-tr')
            
            name_cell = rows[i].find_element(By.XPATH, './td[2]')
            updated_date = rows[i].find_element(By.XPATH, './td[5]')
            updated_date_text = updated_date.text
            parsed_date = datetime.strptime(updated_date_text, "%b %d %Y, %I:%M %p")
            formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            
            if name_cell.text == 'Published':
                logger.info("Processing Published status")
                logger.info(f"Processing Published status : {name_cell.text}")
                click_url = click_on_folder_or_file(driver, rows[i])
                logger.info(f"STARTING SCRAP FOR PUBLISHED WORKFLOW: {click_url}")
                main_publish_list.append(click_url)
                logger.info("Main Publish List:", main_publish_list)
                try:
                    # action_type = scrapp_email_sms(driver, click_url)
                    scrapp_email_sms(driver, click_url)
                except Exception as e:
                    logger.info(f"Error while scrapp_email_sms function call : {e}")

                driver.get(current_url)
                time.sleep(60)
                driver.switch_to.frame("workflow-builder")
                time.sleep(15)

            elif name_cell.text == "Draft":
                logger.info("Processing Draft status")
                logger.info("Processing Draft status")
            
            else:
                logger.info("Processing Folder")
                logger.info("Processing Folder")
                click_url = click_on_folder_or_file(driver, rows[i])
                logger.info(f"STARTING SCRAP FOR FOLDER: {click_url}")
                main_folder_list.append(click_url)
                driver.get(current_url)
                time.sleep(40)
                driver.switch_to.frame("workflow-builder")

    except Exception as e:
        logger.error(f"Table not Found")
        logger.info("Table not Found")

    logger.info("main_publish_list",main_publish_list)
    
    if len(main_folder_list) >=1:
        next_url = main_folder_list[0]
        try:
            driver.get(next_url)
            time.sleep(35)
            driver.switch_to.frame("workflow-builder")
            main_folder_list.pop(0)
            status_check_folder_or_not(driver)
        except Exception as e:
            logger.error(f"Error navigating to folder: {e}")
            logger.error("Error navigating to folder:", str(e))
    
    logger.info("Final Main Publish List:", main_publish_list)
    logger.info(f"Final Main Publish List: {main_publish_list}")
    return main_publish_list

