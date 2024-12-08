import argparse
import asyncio
import platform
import queue
import subprocess
import sys
import threading
import time
from typing import Optional

import easyocr
import pyautogui
from PIL import ImageGrab
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from novel_genie.generate_novel import NovelGenie
from novel_genie.logger import logger


# Define the shortcut combination: Ctrl + Shift + S
SHORTCUT_COMBINATION = {Key.ctrl, Key.shift, KeyCode.from_char("s")}

# Create a thread-safe queue for communication between threads
shortcut_queue = queue.Queue()


async def generate_and_display_novel(
    user_input: str, resume_novel_id: Optional[str] = None
):
    novel_genie = NovelGenie()
    try:
        novel = await novel_genie.generate_novel(
            user_input=user_input, resume_novel_id=resume_novel_id
        )
        logger.info(f"Generated Novel:\n{novel}")
    except Exception as e:
        logger.error(f"Failed to generate novel: {e}")


def extract_text_from_image(image_path: str) -> Optional[str]:
    try:
        reader = easyocr.Reader(
            ["ch_sim", "en"]
        )  # Supports Simplified Chinese and English
        results = reader.readtext(image_path, detail=0, paragraph=True)
        extracted_text = "\n".join(results)
        logger.info(f"Extracted Text from Screenshot:\n{extracted_text}")
        return extracted_text
    except Exception as e:
        logger.error(f"OCR Recognition Failed: {e}")
        return None


def take_screenshot_mac() -> Optional[str]:
    """
    Use macOS's screencapture tool for region-based screenshots
    """
    try:
        screenshot_path = "screenshot.png"
        logger.info("Launching macOS region screenshot tool...")
        # Invoke screencapture with interactive mode
        subprocess.run(["screencapture", "-i", screenshot_path], check=True)
        logger.info(f"Screenshot saved to {screenshot_path}")
        return screenshot_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Screenshot Failed: {e}")
        return None


def take_screenshot_windows() -> Optional[str]:
    """
    Use Windows' built-in screenshot tool for region-based screenshots
    """
    try:
        screenshot_path = "screenshot.png"
        logger.info("Launching Windows region screenshot tool...")
        # Simulate pressing Win + Shift + S
        pyautogui.hotkey("win", "shift", "s")
        logger.info("Please select the screenshot area within the next few seconds...")
        # Wait for the user to take the screenshot
        time.sleep(3)  # Adjust the sleep time as needed
        # Retrieve the image from the clipboard
        image = ImageGrab.grabclipboard()
        if image is not None:
            image.save(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
            return screenshot_path
        else:
            logger.error("Failed to retrieve screenshot from clipboard.")
            return None
    except Exception as e:
        logger.error(f"Screenshot Failed: {e}")
        return None


def take_screenshot() -> Optional[str]:
    system = platform.system()
    if system == "Darwin":
        return take_screenshot_mac()
    elif system == "Windows":
        return take_screenshot_windows()
    else:
        logger.error(f"Unsupported Operating System: {system}")
        return None


def keyboard_listener_thread(shortcut_queue: queue.Queue):
    """
    Run the keyboard listener in a separate thread.
    When the shortcut is detected, put a task in the queue.
    """
    current_keys = set()

    def on_press(key):
        current_keys.add(key)
        if all(k in current_keys for k in SHORTCUT_COMBINATION):
            logger.info("Screenshot shortcut detected, enqueueing screenshot task.")
            shortcut_queue.put_nowait("screenshot")

    def on_release(key):
        if key in current_keys:
            current_keys.remove(key)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


async def handle_shortcut_queue(shortcut_queue: queue.Queue):
    """
    Asynchronous coroutine to handle tasks from the queue.
    """
    while True:
        try:
            # Block until a task is available
            task = await asyncio.to_thread(shortcut_queue.get)
            if task == "screenshot":
                logger.info("Processing screenshot task...")
                # Execute screenshot
                screenshot_path = take_screenshot()
                if not screenshot_path:
                    logger.error("Screenshot failed, skipping task.")
                    continue
                # Perform OCR
                extracted_text = extract_text_from_image(screenshot_path)
                if not extracted_text:
                    logger.error(
                        "Failed to extract text from screenshot, skipping task."
                    )
                    continue
                # Generate novel
                await generate_and_display_novel(extracted_text)
        except Exception as e:
            logger.error(f"Error while processing queue: {e}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Novel Genie - A tool to generate novels via command line input or screenshots"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i", "--input", type=str, help="Direct text input to generate a novel"
    )
    group.add_argument(
        "-s",
        "--screenshot",
        action="store_true",
        help="Enable screenshot shortcut to generate a novel",
    )
    group.add_argument(
        "-r",
        "--resume_novel_id",
        action="store_true",
        help="Resume the novel generation from the last checkpoint",
    )
    return parser.parse_args()


async def run_main():
    args = parse_arguments()
    if args.resume_novel_id:
        resume_novel_id = args.resume_novel_id
        await generate_and_display_novel(user_input="", resume_novel_id=resume_novel_id)
    elif args.input:
        user_input = args.input
        await generate_and_display_novel(user_input)
    elif args.screenshot:
        logger.info("Screenshot mode enabled. Press Ctrl+Shift+S to generate a novel.")
        # Start the keyboard listener thread
        listener_thread = threading.Thread(
            target=keyboard_listener_thread, args=(shortcut_queue,), daemon=True
        )
        listener_thread.start()
        # Start handling the queue
        await handle_shortcut_queue(shortcut_queue)


def main():
    try:
        asyncio.run(run_main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
