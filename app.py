import argparse
import asyncio
import sys
from typing import Optional

import easyocr
import pyautogui
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from novel_genie.generate_novel import NovelGenie
from novel_genie.logger import logger


# 配置快捷键
SHORTCUT_COMBINATION = {Key.ctrl, Key.shift, KeyCode(char="s")}


def parse_arguments():
    parser = argparse.ArgumentParser(description="Novel Genie - 生成你的专属小说")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--input", type=str, help="直接输入文字需求生成小说")
    group.add_argument("-s", "--screenshot", action="store_true", help="启用截图快捷键生成小说")
    return parser.parse_args()


async def generate_and_display_novel(user_input: str):
    novel_genie = NovelGenie()
    try:
        novel = await novel_genie.generate_novel(user_input=user_input)
        logger.info(f"生成的小说:\n{novel}")
    except Exception as e:
        logger.error(f"小说生成失败: {e}")


def take_screenshot() -> Optional[str]:
    try:
        screenshot = pyautogui.screenshot()
        screenshot_path = "screenshot.png"
        screenshot.save(screenshot_path)
        logger.info(f"已保存截图到 {screenshot_path}")
        return screenshot_path
    except Exception as e:
        logger.error(f"截图失败: {e}")
        return None


def extract_text_from_image(image_path: str) -> Optional[str]:
    try:
        reader = easyocr.Reader(["ch_sim", "en"])  # 支持简体中文和英文
        results = reader.readtext(image_path, detail=0, paragraph=True)
        extracted_text = "\n".join(results)
        logger.info(f"从截图中提取的文本: {extracted_text}")
        return extracted_text
    except Exception as e:
        logger.error(f"OCR 识别失败: {e}")
        return None


def start_keyboard_listener(loop: asyncio.AbstractEventLoop):
    def handle_screenshot_trigger():
        current_keys = set()

        def on_press(key):
            nonlocal current_keys
            if key in SHORTCUT_COMBINATION:
                current_keys.add(key)
                if all(k in current_keys for k in SHORTCUT_COMBINATION):
                    logger.info("检测到截图快捷键，正在处理...")
                    screenshot_path = take_screenshot()
                    if not screenshot_path:
                        return
                    extracted_text = extract_text_from_image(screenshot_path)
                    if not extracted_text:
                        logger.error("未能从截图中提取到文本。")
                        return
                    # 将生成小说的任务提交给事件循环
                    asyncio.run_coroutine_threadsafe(
                        generate_and_display_novel(extracted_text), loop
                    )
            else:
                current_keys.clear()

        def on_release(key):
            if key in current_keys:
                current_keys.remove(key)

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    import threading

    listener_thread = threading.Thread(target=handle_screenshot_trigger, daemon=True)
    listener_thread.start()


async def main():
    args = parse_arguments()

    if args.input:
        user_input = args.input
        await generate_and_display_novel(user_input)
    elif args.screenshot:
        logger.info("已启用截图快捷键 (Ctrl+Shift+S)。按下快捷键以生成小说。")
        loop = asyncio.get_event_loop()
        start_keyboard_listener(loop)
        # 保持主线程运行，等待事件
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序已终止。")
        sys.exit(0)
