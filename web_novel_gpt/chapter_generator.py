import openai

from web_novel_gpt.prompts.chapter_generator_prompt import CHAPTER_GENERATOR_PROMPT


def generate_chapters(detailed_outline, config):
    chapters = []
    for i, outline in enumerate(detailed_outline.split("\n\n"), start=1):
        prompt = CHAPTER_GENERATOR_PROMPT.format(
            detailed_outline=outline, chapter_number=i
        )
        response = openai.ChatCompletion.create(
            model=config["model"],
            prompt=prompt,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
        )
        chapters.append(response["choices"][0]["text"].strip())
    return chapters
