import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


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


# ================= UI Code ==================
class WhatsAppAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Automation - Edufutura")
        self.root.geometry("700x600")

        # Numbers input
        tk.Label(root, text="Enter Numbers (comma separated or one per line):").pack(anchor="w")
        self.numbers_text = scrolledtext.ScrolledText(root, height=10)
        self.numbers_text.pack(fill="x")

        # Message input
        tk.Label(root, text="Enter Message:").pack(anchor="w")
        self.message_entry = scrolledtext.ScrolledText(root, height=5)
        self.message_entry.pack(fill="x")

        # Image selection
        self.image_path = None
        self.image_btn = tk.Button(root, text="Choose Image", command=self.select_image)
        self.image_btn.pack(pady=5)

        # Start button
        self.start_btn = tk.Button(root, text="Start Sending", command=self.start_sending, bg="green", fg="white")
        self.start_btn.pack(pady=10)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")]
        )
        if self.image_path:
            messagebox.showinfo("Image Selected", f"Selected: {self.image_path}")

    def start_sending(self):
        numbers_raw = self.numbers_text.get("1.0", tk.END).strip()
        message = self.message_entry.get("1.0", tk.END).strip()

        if not numbers_raw or not message:
            messagebox.showerror("Error", "Please enter both numbers and message.")
            return

        # Process numbers
        numbers = []
        for n in numbers_raw.replace(",", "\n").split("\n"):
            n = n.strip()
            if n:
                if not n.startswith("91"):
                    n = "91" + n  # Ensure India country code
                numbers.append(n)

        if not numbers:
            messagebox.showerror("Error", "No valid numbers entered.")
            return

        driver = create_driver()
        messagebox.showinfo("Scan QR", "Please scan WhatsApp QR code in the opened browser.\nThen press OK to continue.")

        # Step 1: Send text messages
        for phone_number in numbers:
            send_text_message(driver, phone_number, message)

        # Step 2: Send images (if selected)
        if self.image_path:
            for phone_number in numbers:
                send_image(driver, phone_number, self.image_path, caption=None)

        driver.quit()
        messagebox.showinfo("Done", "All messages and images sent successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppAutomationApp(root)
    root.mainloop()
