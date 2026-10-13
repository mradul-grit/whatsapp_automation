import time
import urllib.parse
import tkinter as tk
from tkinter import scrolledtext, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


def start_sending(numbers, message):
    # --- Chrome Profile Setup ---
    options = Options()
    options.add_argument(r"--user-data-dir=C:\\Users\\Lenovo\\whatsapp_profile")
    options.add_argument(r"--profile-directory=Default")

    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com")

    wait = WebDriverWait(driver, 60)

    # --- URL encode the message ---
    encoded_message = urllib.parse.quote(message)

    # --- Function to send message ---
    def send_message(phone_number, text):
        try:
            driver.get(f"https://web.whatsapp.com/send?phone={phone_number}&text={text}")
            time.sleep(8)  # Wait for chat to load

            chat_box = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            chat_box.send_keys(Keys.ENTER)
            print(f"✅ Message sent to {phone_number}")
            time.sleep(4)

        except Exception as e:
            print(f"❌ Could not send to {phone_number}: {e}")

    # --- Run ---
    for number in numbers:
        send_message(number, encoded_message)

    print("🎉 All messages sent successfully!")
    driver.quit()
    messagebox.showinfo("Success", "All messages sent successfully!")


# --- UI Interface ---
def run_ui():
    root = tk.Tk()
    root.title("WhatsApp Bulk Sender")
    root.geometry("600x500")

    tk.Label(root, text="Enter Phone Numbers (one per line with country code, no +):").pack(anchor="w", padx=10, pady=5)
    numbers_text = scrolledtext.ScrolledText(root, width=70, height=10)
    numbers_text.pack(padx=10, pady=5)

    tk.Label(root, text="Enter Message:").pack(anchor="w", padx=10, pady=5)
    message_text = scrolledtext.ScrolledText(root, width=70, height=10)
    message_text.pack(padx=10, pady=5)

    def on_send():
        numbers_raw = numbers_text.get("1.0", tk.END).strip()
        message = message_text.get("1.0", tk.END).strip()

        if not numbers_raw or not message:
            messagebox.showerror("Error", "Please enter numbers and a message!")
            return

        numbers = [n.strip() for n in numbers_raw.splitlines() if n.strip()]
        if len(numbers) > 200:
            messagebox.showerror("Error", "You can only send to max 200 numbers at once!")
            return

        root.destroy()  # close UI
        start_sending(numbers, message)

    tk.Button(root, text="Send Messages", command=on_send, bg="green", fg="white", width=20).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    run_ui()
