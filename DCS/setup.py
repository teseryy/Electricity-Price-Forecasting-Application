from setuptools import setup, find_packages

setup(
    name="dcs",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "pytest",
        "pytest-asyncio",
        "aiohttp",
        "clickhouse-connect",
        "faststream",
        "httpx",
        "zeep"
    ],
) 