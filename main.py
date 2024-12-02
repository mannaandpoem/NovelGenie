import asyncio

from web_novel_gpt.generate_novel import WebNovelGPT
from web_novel_gpt.logger import logger


async def main():
    novel_generator = WebNovelGPT()
    user_input = "普通上班族意外获得系统，开始了自己的职场逆袭之路。"

    novel = await novel_generator.generate_novel(user_input=user_input)
    logger.info(f"Generated novel: \n{novel}")


if __name__ == "__main__":
    asyncio.run(main())
