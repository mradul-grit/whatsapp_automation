# Contributing

Thanks for considering a contribution to this project.

## Getting started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a branch for your change: `git checkout -b my-change`.

## Guidelines

- Keep changes focused — one feature or fix per pull request.
- Follow the existing code style (standard library `logging`, type hints where practical).
- Test your changes manually against WhatsApp Web before submitting, since there is
  no automated test suite for the Selenium flows.
- Do not commit real phone numbers, personal images, or any other personal data.
  Use the provided `.example` files as templates for local config.
- Update the README if you add or rename a script, command-line flag, or config option.

## Reporting issues

When WhatsApp Web changes its layout, the CSS/XPath selectors in this project can
break. If you open an issue about a broken selector, please include:

- The error message / traceback.
- Whether you can see the relevant element in the browser DOM, and its current
  attributes (useful for updating the selector).

## Code of conduct

Be respectful. This project automates a product in ways outside its intended use;
see the Disclaimer section in the README before using or extending it.
