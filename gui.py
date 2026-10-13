"""
Tkinter GUI for bulk-sending WhatsApp text messages and/or an image, built on
top of whatsapp_core.py. Run with: python gui.py
"""

import logging
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from whatsapp_core import create_driver, send_image, send_text_message, wait_for_login

logger = logging.getLogger("gui")


def parse_numbers(raw: str, default_country_code: str = "91"):
    numbers = []
    for line in raw.replace(",", "\n").split("\n"):
        n = line.strip()
        if not n:
            continue
        if not n.startswith(default_country_code) and len(n) == 10:
            n = default_country_code + n
        numbers.append(n)
    return numbers


class WhatsAppAutomationApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("WhatsApp Automation")
        self.root.geometry("700x650")
        self.image_path = None

        tk.Label(root, text="Phone numbers (comma separated or one per line):").pack(anchor="w", padx=10, pady=(10, 0))
        self.numbers_text = scrolledtext.ScrolledText(root, height=8)
        self.numbers_text.pack(fill="x", padx=10)

        tk.Label(root, text="Message (optional if sending only an image):").pack(anchor="w", padx=10, pady=(10, 0))
        self.message_text = scrolledtext.ScrolledText(root, height=8)
        self.message_text.pack(fill="x", padx=10)

        image_frame = tk.Frame(root)
        image_frame.pack(fill="x", padx=10, pady=(10, 0))
        self.image_btn = tk.Button(image_frame, text="Choose image", command=self.select_image)
        self.image_btn.pack(side="left")
        self.image_label = tk.Label(image_frame, text="No image selected")
        self.image_label.pack(side="left", padx=8)

        self.start_btn = tk.Button(root, text="Start sending", command=self.start_sending, bg="green", fg="white")
        self.start_btn.pack(pady=15)

        tk.Label(root, text="Log:").pack(anchor="w", padx=10)
        self.log_box = scrolledtext.ScrolledText(root, height=10, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def log(self, message: str):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)
        logger.info(message)

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.webp")])
        if path:
            self.image_path = path
            self.image_label.config(text=path)

    def start_sending(self):
        numbers_raw = self.numbers_text.get("1.0", tk.END).strip()
        message = self.message_text.get("1.0", tk.END).strip()

        if not numbers_raw:
            messagebox.showerror("Error", "Enter at least one phone number.")
            return
        if not message and not self.image_path:
            messagebox.showerror("Error", "Enter a message and/or choose an image to send.")
            return

        numbers = parse_numbers(numbers_raw)
        if len(numbers) > 200:
            messagebox.showerror("Error", "You can only send to 200 numbers at once.")
            return

        self.log(f"Launching Chrome for {len(numbers)} recipient(s)...")
        try:
            driver = create_driver()
        except Exception as exc:
            self.log(f"Failed to launch Chrome: {exc}")
            messagebox.showerror("Driver error", str(exc))
            return

        try:
            messagebox.showinfo("Scan QR", "Scan the WhatsApp Web QR code in the browser, then click OK.")
            wait_for_login(driver)

            for phone in numbers:
                if message:
                    result = send_text_message(driver, phone, message)
                    self.log(f"Text to {phone}: {'OK' if result.success else result.error}")

                if self.image_path:
                    result = send_image(driver, phone, self.image_path, caption=None)
                    self.log(f"Image to {phone}: {'OK' if result.success else result.error}")

            messagebox.showinfo("Done", "Finished sending. See log for per-number results.")
        finally:
            driver.quit()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    root = tk.Tk()
    WhatsAppAutomationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
