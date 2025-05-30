from setuptools import setup, find_packages

setup(
    name="calendar_bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "google-api-python-client",
        "google-auth-oauthlib",
        "requests",
        "python-dotenv",
        "langchain",
        "langchain-community",
        "langchain-core",
        "openai",
        "mistralai"
    ],
) 