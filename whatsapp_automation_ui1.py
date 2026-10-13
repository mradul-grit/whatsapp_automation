"""
Troubleshooting-ready WhatsApp automation GUI (diagnostic first).

Requirements:
    pip install selenium webdriver-manager

How to use:
1. Run this script.
2. Click "Test Browser" — it will try to open Chrome via webdriver-manager.
   - If it opens a browser and visits google.com, Selenium+Chrome are working.
   - If it fails, use "Set ChromeDriver" to point to a downloaded chromedriver.exe
     (download the correct chromedriver matching your Chrome from https://chromedriver.chromium.org/).
   - Optionally click "Set Chrome Binary" to point to chrome.exe (if Chrome is non-standard).
3. Once Test Browser works, use Start Sending (it will open WhatsApp Web and ask you to scan QR).
"""

import os
import sys
import time
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# optional for send later (kept minimal)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------- App-level state -----------------
CHROMEDRIVER_PATH = None   # user can set via GUI
CHROME_BINARY_PATH = None  # optional: user can set path to chrome.exe

# ----------------- Helpers -----------------
def log_exception_to_textbox(log_fn, exc: Exception):
    tb = traceback.format_exc()
    log_fn("EXCEPTION: " + str(exc))
    log_fn(tb)

# ----------------- Browser creation -----------------
def create_driver_with_fallback(log_fn):
    """
    Tries to create a Chrome WebDriver:
     - First attempt: webdriver-manager (automatic download)
     - If that fails and CHROMEDRIVER_PATH is set, use it
     - Allows specifying CHROME_BINARY_PATH
    Returns: webdriver instance or raises Exception
    """
    global CHROMEDRIVER_PATH, CHROME_BINARY_PATH
    opts = Options()
    # use a persistent profile so QR can be reused between runs (change if unwanted)
    profile_dir = os.path.join(os.path.expanduser("~"), "SeleniumWhatsAppProfile")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # Make sure not to use headless for WhatsApp Web
    # opts.add_argument("--headless")  # DON'T use headless for WhatsApp Web

    if CHROME_BINARY_PATH:
        opts.binary_location = CHROME_BINARY_PATH
        log_fn(f"Using chrome binary: {CHROME_BINARY_PATH}")

    last_exc = None

    # Try webdriver-manager first
    try:
        log_fn("Trying webdriver-manager to install/start chromedriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
        driver.maximize_window()
        log_fn("✅ Driver launched via webdriver-manager")
        return driver
    except Exception as e:
        last_exc = e
        log_fn("webdriver-manager attempt failed:")
        log_exception_to_textbox(log_fn, e)

    # If user provided chromedriver path, try that
    if CHROMEDRIVER_PATH:
        try:
            log_fn(f"Trying local chromedriver at: {CHROMEDRIVER_PATH}")
            service = Service(CHROMEDRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=opts)
            driver.maximize_window()
            log_fn("✅ Driver launched via local chromedriver")
            return driver
        except Exception as e:
            last_exc = e
            log_fn("Local chromedriver attempt failed:")
            log_exception_to_textbox(log_fn, e)

    # Nothing worked — raise the last exception so caller can show it
    raise last_exc if last_exc else RuntimeError("Unknown driver start failure")


# ----------------- Minimal send helpers (safe/simple) -----------------
def wait_for_chat_loaded(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_elements(By.XPATH, "//div[@contenteditable='true']")) > 0
    )

def send_text_simple(driver, phone, message, log_fn):
    """Open chat and try to send message (simple reliable approach)."""
    try:
        url = f"https://web.whatsapp.com/send?phone={phone}"
        log_fn(f"Opening chat: {url}")
        driver.get(url)
        wait_for_chat_loaded(driver, timeout=40)
        time.sleep(0.8)

        # find contenteditable boxes and choose a visible one
        boxes = [b for b in driver.find_elements(By.XPATH, "//div[@contenteditable='true']") if b.is_displayed()]
        if not boxes:
            log_fn("❌ No visible message box found.")
            return False

        box = boxes[-1]
        box.click()
        # clear prefilled text
        box.send_keys(Keys.CONTROL, "a")
        box.send_keys(Keys.BACKSPACE)
        # type message in small chunks
        for chunk in [message[i:i+200] for i in range(0, len(message), 200)]:
            box.send_keys(chunk)
            time.sleep(0.03)
        time.sleep(0.2)

        # try clicking a 'send' button if present
        try:
            send_btn = driver.find_element(By.XPATH, "//button[.//span[@data-icon='send']]")
            driver.execute_script("arguments[0].click();", send_btn)
            log_fn("✅ Clicked send button (button/span).")
            return True
        except Exception:
            # fallback to ENTER
            try:
                box.send_keys(Keys.ENTER)
                log_fn("✅ Sent message via ENTER fallback.")
                return True
            except Exception as e:
                log_fn(f"❌ Failed to send via send button and ENTER: {e}")
                return False
    except Exception as e:
        log_exception_to_textbox(log_fn, e)
        return False


# ----------------- GUI -----------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Automation — Diagnostic Edition")
        self.root.geometry("760x700")

        # Numbers input
        tk.Label(root, text="Enter Numbers (comma or one per line)").pack(anchor="w", padx=8, pady=(8,0))
        self.numbers = scrolledtext.ScrolledText(root, height=8)
        self.numbers.pack(fill="x", padx=8)

        # Message input
        tk.Label(root, text="Message to send").pack(anchor="w", padx=8, pady=(8,0))
        self.message = scrolledtext.ScrolledText(root, height=5)
        self.message.pack(fill="x", padx=8)

        # Image path (optional)
        tk.Label(root, text="(Optional) Local image to send").pack(anchor="w", padx=8, pady=(8,0))
        frame_img = tk.Frame(root)
        frame_img.pack(fill="x", padx=8)
        self.img_btn = tk.Button(frame_img, text="Choose image", command=self.choose_image)
        self.img_btn.pack(side="left")
        self.img_label = tk.Label(frame_img, text="No image selected", anchor="w")
        self.img_label.pack(side="left", padx=8)

        self.send_images_var = tk.IntVar(value=0)
        tk.Checkbutton(root, text="Send chosen image after text (not implemented in diagnostic)", variable=self.send_images_var).pack(anchor="w", padx=8, pady=(6,0))

        # Chrome options area
        tk.Label(root, text="Chrome / Chromedriver (for troubleshooting)").pack(anchor="w", padx=8, pady=(12,0))
        frame_paths = tk.Frame(root)
        frame_paths.pack(fill="x", padx=8, pady=(4,0))
        self.set_chrome_bin_btn = tk.Button(frame_paths, text="Set Chrome Binary (chrome.exe)", command=self.set_chrome_binary)
        self.set_chrome_bin_btn.pack(side="left")
        self.set_driver_btn = tk.Button(frame_paths, text="Set Chromedriver (chromedriver.exe)", command=self.set_chromedriver)
        self.set_driver_btn.pack(side="left", padx=6)
        self.paths_label = tk.Label(frame_paths, text="No custom paths set", anchor="w")
        self.paths_label.pack(side="left", padx=8)

        # Test & start buttons
        frame_actions = tk.Frame(root)
        frame_actions.pack(fill="x", padx=8, pady=(12,0))
        self.test_btn = tk.Button(frame_actions, text="Test Browser", command=self.test_browser, bg="#0078D7", fg="white")
        self.test_btn.pack(side="left")
        self.start_btn = tk.Button(frame_actions, text="Start Sending (diagnostic)", command=self.start_sending, bg="green", fg="white")
        self.start_btn.pack(side="left", padx=8)

        # Log box
        tk.Label(root, text="Logs (copy & paste here if you need help)").pack(anchor="w", padx=8, pady=(12,0))
        self.log_box = scrolledtext.ScrolledText(root, height=14, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.driver = None
        self.image_path = None
        self.update_paths_label()

    def log(self, *args):
        msg = " ".join(str(a) for a in args)
        print(msg)
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)

    def choose_image(self):
        p = filedialog.askopenfilename(title="Select image", filetypes=[("Images","*.jpg *.jpeg *.png *.webp *.gif")])
        if p:
            self.image_path = p
            self.img_label.config(text=os.path.basename(p))
            self.log("Selected image:", p)

    def set_chrome_binary(self):
        global CHROME_BINARY_PATH
        p = filedialog.askopenfilename(title="Select chrome.exe / chromium binary")
        if p:
            CHROME_BINARY_PATH = p
            self.log("Set Chrome binary to:", p)
            self.update_paths_label()

    def set_chromedriver(self):
        global CHROMEDRIVER_PATH
        p = filedialog.askopenfilename(title="Select chromedriver executable")
        if p:
            CHROMEDRIVER_PATH = p
            self.log("Set chromedriver to:", p)
            self.update_paths_label()

    def update_paths_label(self):
        txt = []
        if CHROME_BINARY_PATH:
            txt.append("Chrome:" + CHROME_BINARY_PATH)
        if CHROMEDRIVER_PATH:
            txt.append("Chromedriver:" + CHROMEDRIVER_PATH)
        if not txt:
            self.paths_label.config(text="No custom paths set")
        else:
            self.paths_label.config(text=" | ".join(txt))

    def test_browser(self):
        """Quick test to check if Selenium can launch Chrome"""
        self.log("=== Testing browser launch ===")
        try:
            driver = create_driver_with_fallback(self.log)
            self.log("Opened browser — navigating to https://www.google.com ...")
            driver.get("https://www.google.com")
            time.sleep(2)
            self.log("Page title:", driver.title)
            driver.quit()
            self.log("✅ Test browser success — driver quit cleanly.")
        except Exception as e:
            self.log("❌ Test browser failed:")
            log_exception_to_textbox(self.log, e)
            messagebox.showerror("Test Browser Failed", f"See logs for details. Exception: {e}")

    def start_sending(self):
        """Main start: first try to create driver and show helpful errors if it fails"""
        numbers_raw = self.numbers.get("1.0", tk.END).strip()
        message = self.message.get("1.0", tk.END).strip()

        if not numbers_raw:
            messagebox.showerror("Input required", "Please enter at least one phone number.")
            return
        if not message:
            messagebox.showerror("Input required", "Please enter a message to send.")
            return

        # process numbers
        numbers = []
        for line in numbers_raw.replace(",", "\n").split("\n"):
            l = line.strip()
            if not l:
                continue
            if not l.startswith("91"):
                l = "91" + l
            numbers.append(l)

        if not numbers:
            messagebox.showerror("Input", "No valid numbers found.")
            return

        self.log("Creating driver (this may take a few seconds)...")
        try:
            driver = create_driver_with_fallback(self.log)
            self.driver = driver
        except Exception as e:
            self.log("❌ Could not start driver. See logs above.")
            messagebox.showerror("Driver start failed", f"Could not start Chrome driver. See logs. Error: {e}")
            return

        # Ask to scan QR
        messagebox.showinfo("Scan QR", "WhatsApp Web will open. Scan the QR code in the browser. Click OK here after scanning.")
        # Send first message as a single-test to observe behaviour
        try:
            for idx, phone in enumerate(numbers, start=1):
                self.log(f"[{idx}/{len(numbers)}] Sending text to {phone} ...")
                ok = send_text_simple(driver, phone, message, log_fn=self.log)
                self.log("Result:", ok)
                time.sleep(2)
            self.log("All done (driver remains open so you can inspect). Quitting driver now.")
            driver.quit()
            self.log("Driver quit.")
            messagebox.showinfo("Done", "Attempt finished. Check logs for details.")
        except Exception as e:
            log_exception_to_textbox(self.log, e)
            try:
                if driver:
                    driver.quit()
            except:
                pass
            messagebox.showerror("Error during sending", f"See logs. Exception: {e}")

    def on_close(self):
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()



