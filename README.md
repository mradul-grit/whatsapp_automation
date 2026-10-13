# WhatsApp Automation

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

Selenium-based tooling for sending bulk WhatsApp messages and images via WhatsApp Web,
with both a command-line interface and a Tkinter GUI.

## Disclaimer

WhatsApp's Terms of Service prohibit unauthorized bulk or automated messaging, and
automating WhatsApp Web is outside its intended use. Accounts used for spam or mass
unsolicited messaging risk being banned. This project is intended for sending
messages to contacts who have agreed to receive them (e.g. your own customers,
team, or community members) — use it responsibly and at your own risk.

## Project structure

- `whatsapp_core.py` - Core automation module: Chrome driver setup, login wait,
  and send functions with retry logic. No UI/CLI code lives here.
- `cli.py` - Command-line entry point (argparse-based), supports a comma-separated
  list of numbers or a numbers file.
- `gui.py` - Tkinter GUI for interactive use.

## Requirements

- Python 3.8+
- Google Chrome installed
- Dependencies in `requirements.txt`

## Download

Clone the repository:

```
git clone https://github.com/mradul-grit/whatsapp_automation.git
cd whatsapp_automation
```

Create a virtual environment and install dependencies:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Running

### Command line

```
python cli.py --numbers 911234567890,919876543210 --message "Hello!"
python cli.py --numbers-file numbers.txt --message "Hello!" --image photo.jpg
```

Copy `numbers.example.txt` to `numbers.txt` and fill in real numbers (git-ignored,
so your contacts stay local) if you prefer a file over `--numbers`.

### GUI

```
python gui.py
```

Enter phone numbers and a message and/or image, then click "Start sending".

On first run, a Chrome window opens to WhatsApp Web — scan the QR code with your
phone to log in. The Chrome profile is then persisted locally, so you won't need
to scan again on later runs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT - see [LICENSE](LICENSE).
