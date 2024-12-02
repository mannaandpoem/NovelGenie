# WebNovelGPT

[中文](README.md) | English

WebNovelGPT is a Python project designed for generating web novels. This project can generate multi-volume novels based
on user input descriptions and supports resuming the generation process from checkpoints.

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/mannaandpoem/WebNovelGPT.git
    cd WebNovelGPT
    ```

2. Create and activate a virtual environment:
    ```sh
    conda create -n webnovel python=3.10 -y
    conda activate webnovel
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Configuration

Before using, please check `config.example.yaml` and create and configure your `config.yaml` file as needed.

1. Open the `config.example.yaml` file to understand the meaning of each configuration item.
2. Create a new `config.yaml` file and configure it according to the examples in `config.example.yaml`.

### Generate a Novel from Scratch

```python
import asyncio

from web_novel_gpt.generate_novel import WebNovelGPT
from web_novel_gpt.logger import logger


async def main():
    web_novel_gpt = WebNovelGPT()
    user_input = "An ordinary office worker accidentally obtains a system and begins their journey of workplace counterattack."

    novel = await web_novel_gpt.generate_novel(user_input=user_input)
    logger.info(f"Generated novel: \n{novel}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Resume Novel Generation from Checkpoint

```python
import asyncio

from web_novel_gpt.generate_novel import WebNovelGPT
from web_novel_gpt.logger import logger


async def main():
    web_novel_gpt = WebNovelGPT()
    user_input = "An ordinary office worker accidentally obtains a system and begins their journey of workplace counterattack."

    novel = await web_novel_gpt.generate_novel(user_input=user_input, resume_novel_id="your_novel_id")
    logger.info(f"Generated novel: \n{novel}")


if __name__ == '__main__':
    asyncio.run(main())
```

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request.

## License

This project is licensed under the MIT License. For more information, please see the `LICENSE` file.
