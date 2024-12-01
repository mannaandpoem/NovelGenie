import openai
from web_novel_gpt.prompts.chapter_generator_prompt import CHAPTER_GENERATOR_PROMPT


def generate_chapters(detailed_outline, config):
    chapters = []
    for i, outline in enumerate(detailed_outline.split("\n\n"), start=1):
        prompt = CHAPTER_GENERATOR_PROMPT.format(detailed_outline=outline, chapter_number=i)
        response = openai.ChatCompletion.create(
            model=config["model"],
            prompt=prompt,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"]
        )
        chapters.append(response["choices"][0]["text"].strip())
    return chapters

# 对于chapter_generator.py，content_optimizer.py，detailed_outline_generator.py和rough_outline_generator.py这些python脚本。请你对它们进行封装，作为一个WebNovelGPT类，其中包含一个通用的ask方法，该方法接受一个prompt字符串并生成网文。
