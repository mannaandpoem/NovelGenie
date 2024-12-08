from setuptools import find_packages, setup


setup(
    name="NovelGenie",
    version="0.1.0",
    author="mannaandpoem",
    author_email="1580466765@qq.com",
    description="A tool to generate novels via command line input or screenshots",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_data={
        "novel_genie": ["README.md", "README_EN.md"],
    },
    url="https://github.com/mannaandpoem/NovelGenie",  # Replace with your project URL
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
            "novel=novel_genie.app:main",  # Defines the 'novel' command
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
