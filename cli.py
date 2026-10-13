"""
Command-line entry point for bulk-sending WhatsApp text messages and/or an image.

Examples:
    python cli.py --numbers 911234567890,919876543210 --message "Hello!"
    python cli.py --numbers-file numbers.txt --message "Hello!" --image photo.jpg
"""

import argparse
import logging
import sys
from typing import List

from whatsapp_core import create_driver, send_image, send_text_message, wait_for_login

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cli")


def load_numbers(numbers_arg: str, numbers_file: str) -> List[str]:
    numbers: List[str] = []

    if numbers_arg:
        numbers.extend(n.strip() for n in numbers_arg.split(",") if n.strip())

    if numbers_file:
        with open(numbers_file, "r", encoding="utf-8") as f:
            numbers.extend(line.strip() for line in f if line.strip())

    # de-duplicate while preserving order
    seen = set()
    unique = []
    for n in numbers:
        if n not in seen:
            seen.add(n)
            unique.append(n)
    return unique


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send bulk WhatsApp messages and/or an image.")
    parser.add_argument("--numbers", help="Comma-separated list of phone numbers (with country code, no +).")
    parser.add_argument("--numbers-file", help="Path to a text file with one phone number per line.")
    parser.add_argument("--message", help="Text message to send.")
    parser.add_argument("--image", help="Path to an image to send (optional).")
    parser.add_argument("--retries", type=int, default=2, help="Retries per message/image on failure (default: 2).")
    parser.add_argument("--wait-timeout", type=int, default=60, help="Seconds to wait for WhatsApp Web elements (default: 60).")
    parser.add_argument("--profile-dir", help="Custom Chrome profile directory for persisting login.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    numbers = load_numbers(args.numbers, args.numbers_file)
    if not numbers:
        parser.error("No phone numbers provided. Use --numbers or --numbers-file.")
    if not args.message and not args.image:
        parser.error("Provide --message and/or --image.")

    driver_kwargs = {}
    if args.profile_dir:
        driver_kwargs["profile_dir"] = args.profile_dir

    driver = create_driver(**driver_kwargs)
    try:
        wait_for_login(driver)

        failures = []
        for phone in numbers:
            if args.message:
                result = send_text_message(
                    driver, phone, args.message,
                    wait_timeout=args.wait_timeout, retries=args.retries,
                )
                if not result.success:
                    failures.append(phone)

            if args.image:
                result = send_image(
                    driver, phone, args.image, caption=None,
                    wait_timeout=args.wait_timeout, retries=args.retries,
                )
                if not result.success:
                    failures.append(phone)

        if failures:
            logger.warning("Finished with %d failure(s): %s", len(failures), ", ".join(failures))
            return 1

        logger.info("All messages sent successfully.")
        return 0
    finally:
        driver.quit()


if __name__ == "__main__":
    sys.exit(main())
