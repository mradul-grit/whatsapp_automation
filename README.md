# WhatsApp Automation

Selenium-based scripts for sending bulk WhatsApp messages and images via WhatsApp Web.

## Scripts

- `whatsapp_auto.py` - Tkinter UI for sending bulk text messages.
- `whatsapp_automation.py` - Simple bulk text message sender.
- `auto.py` - Sends both text messages and images in bulk.
- `whatsapp_automation_ui.py` - UI with image selection and multi-line caption support.
- `whatsapp_automation_ui1.py` - Diagnostic UI with chromedriver fallback and logging.

## Requirements

```
pip install selenium webdriver-manager
```

## Usage

Run any script directly with Python. On first run, scan the WhatsApp Web QR code
in the browser window that opens; the Chrome profile is then persisted locally
so you won't need to scan again on later runs.
