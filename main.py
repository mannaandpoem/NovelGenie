import asyncio

from novel_genie.generate_novel import NovelGenie
from novel_genie.logger import logger


async def main():
    novel_genie = NovelGenie()
    user_input = "普通上班族意外获得系统，开始了自己的职场逆袭之路。"

    novel = await novel_genie.generate_novel(user_input=user_input)
    logger.info(f"Generated novel: \n{novel}")


if __name__ == "__main__":
    asyncio.run(main())
