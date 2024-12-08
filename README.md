# NovelGenie

中文 | [English](README_EN.md)

NovelGenie 是一款智能网文创作助手，能够基于用户提供的创意构思自动生成完整的多卷小说作品。它不仅支持断点续写和续作功能，还能让创作过程变得更加灵活自然，帮助作者轻松驾驭长篇故事创作。

## 安装

1. 克隆此仓库：
    ```sh
    git clone https://github.com/mannaandpoem/NovelGenie.git
    cd NovelGenie
    ```

2. 创建并激活虚拟环境：
    ```sh
    conda create -n NovelGenie python=3.10 -y
    conda activate NovelGenie
    ```

3. 安装依赖：
    ```sh
    pip install -r requirements.txt
    或
    pip install -e .
    ```

## 使用方法

### 配置

在使用之前，请先查看 `config.example.yaml` 并根据需要创建和配置 `config.yaml` 文件。

1. 打开 `config.example.yaml` 文件，查看并理解各个配置项的含义。
2. 创建一个新的 `config.yaml` 文件，并根据 `config.example.yaml` 中的示例进行配置。

### 使用 Python 脚本生成小说
#### 从头开始生成小说

```python
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
```

#### 从检查点恢复生成小说

```python
import asyncio

from novel_genie.generate_novel import NovelGenie
from novel_genie.logger import logger


async def main():
   novel_genie = NovelGenie()

   novel = await novel_genie.generate_novel(user_input="", resume_novel_id="your_novel_id")
   logger.info(f"Generated novel: \n{novel}")


if __name__ == '__main__':
   asyncio.run(main())
```

### 使用命令行生成小说

以下是命令行的三种用法：

#### 从截图生成小说

```sh
# 执行以下命令
novel -s
# 使用快捷键 Ctrl + Shift + S 截图生成小说
````

#### 从头开始生成小说

```sh
novel -i "普通上班族意外获得系统，开始了自己的职场逆袭之路。"
```

#### 从检查点恢复生成小说

```sh
novel -r "your_novel_id"
```

## 贡献

欢迎贡献代码！请 fork 此仓库并提交 pull request。

## 许可证

此项目使用 MIT 许可证。有关更多信息，请参阅 `LICENSE` 文件。
