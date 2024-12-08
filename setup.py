from setuptools import find_packages, setup


# 读取中文和英文的README
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# 可选：读取英文版README的内容
with open("README_EN.md", encoding="utf-8") as f:
    long_description_en = f.read()

# 合并两部分内容
full_long_description = long_description + "\n\n" + long_description_en

setup(
    name="novel-genie",
    version="0.1.0",
    author="mannaandpoem",
    author_email="1580466765@qq.com",
    description="A tool to generate novels via command line input or screenshots",
    long_description=full_long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mannaandpoem/NovelGenie",
    packages=find_packages(),
    install_requires=[
        "openai~=0.28.0",
        "pyyaml~=6.0.2",
        "pydantic~=2.10.2",
        "loguru~=0.7.2",
        "easyocr~=1.7.2",
        "pyautogui~=0.9.54",
        "pynput~=1.7.7",
        "Pillow~=11.0.0",
    ],
    entry_points={
        "console_scripts": [
            "novel=novel_genie.app:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    package_data={
        "novel_genie": ["README.md", "README_EN.md"],
    },
)
