"""
Core automation module for sending WhatsApp messages and images via WhatsApp Web,
using Selenium. This module contains no UI or CLI code - see cli.py and gui.py.
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger("whatsapp_core")

MESSAGE_BOX_XPATH = '//div[@contenteditable="true"][@data-tab="10"]'
ATTACH_BUTTON_XPATH = '//button[@aria-label="Attach"]'
IMAGE_INPUT_XPATH = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
SEND_BUTTON_XPATH = '//span[@data-icon="send"]'

DEFAULT_PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".whatsapp_automation_profile")


@dataclass
class SendResult:
    phone_number: str
    success: bool
    error: Optional[str] = None


def create_driver(profile_dir: str = DEFAULT_PROFILE_DIR, headless: bool = False) -> webdriver.Chrome:
    """Launch Chrome with a persistent profile so the WhatsApp Web login survives restarts."""
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    return driver


def wait_for_login(driver: webdriver.Chrome, timeout: int = 120) -> None:
    """Block until WhatsApp Web has finished loading the chat list (i.e. QR has been scanned)."""
    driver.get("https://web.whatsapp.com")
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
    )
    logger.info("WhatsApp Web logged in and ready.")


def _retry(action, retries: int, delay: float, description: str):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return action()
        except (TimeoutException, WebDriverException) as exc:
            last_exc = exc
            logger.warning("%s failed (attempt %d/%d): %s", description, attempt, retries, exc)
            time.sleep(delay)
    raise last_exc


def send_text_message(
    driver: webdriver.Chrome,
    phone_number: str,
    message: str,
    wait_timeout: int = 60,
    retries: int = 2,
    retry_delay: float = 3.0,
) -> SendResult:
    """Open a chat with phone_number and send message, preserving line breaks."""

    def _do_send():
        driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")
        wait = WebDriverWait(driver, wait_timeout)
        input_box = wait.until(EC.presence_of_element_located((By.XPATH, MESSAGE_BOX_XPATH)))
        time.sleep(1.5)

        lines = message.split("\n")
        for i, line in enumerate(lines):
            if line:
                input_box.send_keys(line)
            if i < len(lines) - 1:
                input_box.send_keys(Keys.SHIFT, Keys.ENTER)

        input_box.send_keys(Keys.ENTER)
        time.sleep(1.5)

    try:
        _retry(_do_send, retries, retry_delay, f"send_text_message({phone_number})")
        logger.info("Text message sent to %s", phone_number)
        return SendResult(phone_number, True)
    except Exception as exc:
        logger.error("Could not send text to %s: %s", phone_number, exc)
        return SendResult(phone_number, False, str(exc))


def send_image(
    driver: webdriver.Chrome,
    phone_number: str,
    image_path: str,
    caption: Optional[str] = None,
    wait_timeout: int = 60,
    retries: int = 2,
    retry_delay: float = 3.0,
) -> SendResult:
    """Open a chat with phone_number and send an image, with an optional caption."""

    def _do_send():
        driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")
        wait = WebDriverWait(driver, wait_timeout)
        wait.until(EC.presence_of_element_located((By.XPATH, MESSAGE_BOX_XPATH)))
        time.sleep(1.5)

        attach_btn = wait.until(EC.element_to_be_clickable((By.XPATH, ATTACH_BUTTON_XPATH)))
        attach_btn.click()
        time.sleep(1)

        file_input = wait.until(EC.presence_of_element_located((By.XPATH, IMAGE_INPUT_XPATH)))
        file_input.send_keys(os.path.abspath(image_path))
        time.sleep(2)

        if caption:
            caption_box = wait.until(EC.presence_of_element_located((By.XPATH, MESSAGE_BOX_XPATH)))
            lines = caption.split("\n")
            for i, line in enumerate(lines):
                if line:
                    caption_box.send_keys(line)
                if i < len(lines) - 1:
                    caption_box.send_keys(Keys.SHIFT, Keys.ENTER)
            time.sleep(1)

        send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, SEND_BUTTON_XPATH)))
        send_btn.click()
        time.sleep(2)

    try:
        _retry(_do_send, retries, retry_delay, f"send_image({phone_number})")
        logger.info("Image sent to %s", phone_number)
        return SendResult(phone_number, True)
    except Exception as exc:
        logger.error("Could not send image to %s: %s", phone_number, exc)
        return SendResult(phone_number, False, str(exc))
