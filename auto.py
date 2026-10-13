import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_driver():
    """Initialize Chrome with Selenium options"""
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=C:/Temp/SeleniumProfile")  # persistent profile for WhatsApp login
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def send_text_message(driver, phone_number, message):
    """Send only a text message"""
    driver.get(f"https://web.whatsapp.com/send?phone={phone_number}&text={message}")

    try:
        wait = WebDriverWait(driver, 60)
        input_box = wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        time.sleep(2)
        input_box.send_keys(Keys.ENTER)
        print(f"✅ Text message sent to {phone_number}")
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error sending text to {phone_number}: {e}")


def send_image(driver, phone_number, image_path, caption=None):
    """Send an image with optional caption"""
    driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")

    try:
        wait = WebDriverWait(driver, 60)

        # Wait until chat input box is ready
        wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        time.sleep(2)

        # Click 📎 attachment button
        attach_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Attach"]'))
        )
        attach_btn.click()
        time.sleep(1)

        # Upload image
        file_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
        )
        file_input.send_keys(os.path.abspath(image_path))
        time.sleep(2)

        # Add caption if provided
        if caption:
            caption_box = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            caption_box.send_keys(caption)
            time.sleep(1)

        # Send button
        send_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        send_btn.click()

        print(f"✅ Image sent to {phone_number}")
        time.sleep(3)

    except Exception as e:
        print(f"❌ Error sending image to {phone_number}: {e}")


if __name__ == "__main__":
    # ✅ Your numbers
    numbers = [
        "911234567890",
        "919876543210",
        "911112223334",
        "915556667778",
        "919998887776"
    ]

    # ✅ Your message
    message = "hye sir/madam this messages is forward by whatsapp automation from the edufutura's side"

    # ✅ Image in same folder as script
    image_path = os.path.join(os.getcwd(), "GOA TRIP.jpeg")

    driver = create_driver()

    # --- Step 1: Send text messages ---
    for phone_number in numbers:
        send_text_message(driver, phone_number, message)

    # --- Step 2: Send images ---
    for phone_number in numbers:
        send_image(driver, phone_number, image_path, caption=None)  # use caption=message if you want text with image

    driver.quit()
