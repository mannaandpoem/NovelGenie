# WebNovelGPT

WebNovelGPT 是一个用于生成网络小说的 Python 项目。该项目可以根据用户输入的描述生成多卷小说，并支持从检查点恢复生成过程。

## 特性

- 根据用户输入的描述生成网络小说
- 支持生成多卷小说
- 支持从检查点恢复生成过程
- 保存生成过程中的检查点

## 安装

1. 克隆此仓库：
    ```sh
    git clone https://github.com/mannaandpoem/WebNovelGPT.git
    cd WebNovelGPT
    ```

2. 创建并激活虚拟环境：
    ```sh
    conda create -n webnovel python=3.10 -y
    conda activate webnovel
    ```

3. 安装依赖：
    ```sh
    pip install -r requirements.txt
    ```

## 使用方法

### 配置
在使用之前，请先查看 `config.example.yaml` 并根据需要创建和配置 `config.yaml` 文件。

1. 打开 `config.example.yaml` 文件，查看并理解各个配置项的含义。
2. 创建一个新的 `config.yaml` 文件，并根据 `config.example.yaml` 中的示例进行配置。

### 从头开始生成小说

```python
import asyncio
import json
from web_novel_gpt.generate_novel import WebNovelGPT


async def main():
    novel_generator = WebNovelGPT()
    user_input = "这是一个非常非常短的故事，一个普通上班族意外获得系统，开始了自己的职场逆袭之路。要求网文共2卷，每卷2章，每章1000字，共计4000字。"

    novel = await novel_generator.generate_novel(
        user_input=user_input,
        section_word_count=1000,
        num_volumes=2
    )
    print(json.dumps(novel, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
```

### 从检查点恢复生成小说

```python
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
      resume_novel_id="your_novel_id"
   )
   print(json.dumps(novel, indent=4, ensure_ascii=False))


if __name__ == '__main__':
   asyncio.run(main())
```

## 贡献

欢迎贡献代码！请 fork 此仓库并提交 pull request。

## 许可证

此项目使用 MIT 许可证。有关更多信息，请参阅 `LICENSE` 文件。
