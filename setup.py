# setup.py
from setuptools import setup, find_packages

setup(
    name="llm-api-interface",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "aiohttp",
        "python-dotenv",
        "pytest",
        "pytest-asyncio"
    ],
    python_requires=">=3.12",
)