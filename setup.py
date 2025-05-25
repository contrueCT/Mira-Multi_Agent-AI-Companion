from setuptools import setup, find_packages

setup(
    name="emotional-companion",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "autogen-agentchat>=0.2.0",  # 尝试使用替代包名
        "chromadb>=0.4.17",
        "sentence-transformers>=2.2.2",
        "schedule>=1.2.0",
        "pyfiglet>=0.8.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "companion=emotional_companion.cli:main",
        ],
    },
)
