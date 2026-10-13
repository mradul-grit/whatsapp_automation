# WhatsApp Automation

Selenium-based scripts for sending bulk WhatsApp messages and images via WhatsApp Web.

## Scripts

- `whatsapp_auto.py` - Tkinter UI for sending bulk text messages.
- `whatsapp_automation.py` - Simple bulk text message sender.
- `auto.py` - Sends both text messages and images in bulk.
- `whatsapp_automation_ui.py` - UI with image selection and multi-line caption support.
- `whatsapp_automation_ui1.py` - Diagnostic UI with chromedriver fallback and logging.

## Requirements

- Python 3.8+
- Google Chrome installed
- `pip install selenium webdriver-manager`

## Download

Clone the repository:

```
git clone https://github.com/mradul-grit/whatsapp_automation.git
cd whatsapp_automation
```

(Optional) create and activate a virtual environment before installing dependencies:

```
python -m venv venv
venv\Scripts\activate
pip install selenium webdriver-manager
```

## Running

Run any script directly with Python, for example:

```
python auto.py
```

or for a UI-based script:

```
python whatsapp_automation_ui.py
```

On first run, a Chrome window opens to WhatsApp Web — scan the QR code with your
phone to log in. The Chrome profile is then persisted locally (in the folder set
inside the script), so you won't need to scan again on later runs.
