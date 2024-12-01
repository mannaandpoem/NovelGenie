import asyncio
import json

from web_novel_gpt.generate_novel import WebNovelGPT


async def main():
    novel_generator = WebNovelGPT()
    user_input = "这是一个非常非常短的故事，一个普通上班族意外获得系统，开始了自己的职场逆袭之路。要求网文共2卷，每卷2章，每章1000字，共计4000字。"

    novel = await novel_generator.generate_novel(
        user_input=user_input,
        section_word_count=1000,
        num_volumes=2,
    )
    print(json.dumps(novel, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
