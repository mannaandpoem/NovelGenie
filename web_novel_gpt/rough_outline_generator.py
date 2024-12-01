import openai

from web_novel_gpt.prompts.rough_outline_prompt import ROUGH_OUTLINE_GENERATOR_PROMPT
def generate_rough_outline(config):
    theme = config.get("theme", "奇幻冒险")
    prompt = ROUGH_OUTLINE_GENERATOR_PROMPT.format(theme=theme)
    response = openai.ChatCompletion.create(
        model=config["model"],
        prompt=prompt,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"]
    )
    return response["choices"][0]["text"].strip()

def generate_detailed_outline(rough_outline, config):
    prompt = DETAIL_OUTLINE_PROMPT.format(rough_outline=rough_outline)
    response = openai.ChatCompletion.create(
        model=config["model"],
        prompt=prompt,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"]
    )
    return response["choices"][0]["text"].strip()
