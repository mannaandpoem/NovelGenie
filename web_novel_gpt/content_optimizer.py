import openai

from web_novel_gpt.prompts.content_optimizer_prompt import CONTENT_OPTIMIZER_PROMPT


def optimize_content(chapters, config):
    optimized = []
    for chapter in chapters:
        prompt = CONTENT_OPTIMIZER_PROMPT.format(chapter_content=chapter)
        response = openai.ChatCompletion.create(
            model=config["model"],
            prompt=prompt,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
        )
        optimized.append(response["choices"][0]["text"].strip())
    return optimized
