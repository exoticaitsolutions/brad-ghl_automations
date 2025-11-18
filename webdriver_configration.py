from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import traceback
import time


def driver_confrigration():
    try:
        print("Driver function called")

        # Set Chrome options
        options = webdriver.ChromeOptions()
        # Comment out headless while debugging
        # options.add_argument("--headless=new")
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")

        # Initialize Chrome driver using WebDriverManager
        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Chrome driver started successfully!")

        
        return driver

    except Exception as e:
        print("❌ Error while initializing the driver:")
        print(f"Exception: {e}")
        traceback.print_exc()
        return None
