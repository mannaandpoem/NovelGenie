import openai

from web_novel_gpt.prompts.detail_outline_generator_prompt import (
    DETAILED_OUTLINE_GENERATOR_PROMPT,
    DETAILED_OUTLINE_SUMMARY_PROMPT,
)


def generate_detailed_outline(rough_outline, config):
    prompt = DETAILED_OUTLINE_GENERATOR_PROMPT.format(rough_outline=rough_outline)
    response = openai.ChatCompletion.create(
        model=config["model"],
        prompt=prompt,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
    )
    return response["choices"][0]["text"].strip()


def generate_detailed_outline_summary(detailed_outline, config):
    prompt = DETAILED_OUTLINE_SUMMARY_PROMPT.format(detailed_outline=detailed_outline)
    response = openai.ChatCompletion.create(
        model=config["model"],
        prompt=prompt,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
    )
    return response["choices"][0]["text"].strip()
