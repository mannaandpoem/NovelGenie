# NovelGenie

[中文](README.md) | English

NovelGenie is an AI-powered web novel creation assistant that generates multi-volume stories based on user-provided creative concepts. The system seamlessly supports checkpoint-based writing continuation and sequel generation, providing creators with a natural and flexible way to craft extensive narratives without interruption.

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/mannaandpoem/NovelGenie.git
    cd NovelGenie
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

from novel_genie.generate_novel import NovelGenie
from novel_genie.logger import logger


async def main():
   web_novel_gpt = NovelGenie()
   user_input = "An ordinary office worker accidentally obtains a system and begins their journey of workplace counterattack."

   novel = await web_novel_gpt.generate_novel(user_input=user_input)
   logger.info(f"Generated novel: \n{novel}")


if __name__ == "__main__":
   asyncio.run(main())
```

### Resume Novel Generation from Checkpoint

```python
import asyncio

from novel_genie.generate_novel import NovelGenie
from novel_genie.logger import logger


async def main():
   web_novel_gpt = NovelGenie()
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
