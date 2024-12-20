from setuptools import setup, find_packages

setup(
    name="firecrawl",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "playwright>=1.40.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "black>=23.12.0",
            "isort>=5.13.2",
            "flake8>=6.1.0",
            "flake8-docstrings>=1.7.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
        ],
    },
    python_requires=">=3.8",
    author="SoundMinds AI",
    description="An intelligent web scraper using Playwright and LangGraph",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="web scraping, playwright, ai, langgraph",
    project_urls={
        "Documentation": "https://github.com/your-username/firecrawl#readme",
        "Source": "https://github.com/your-username/firecrawl",
        "Tracker": "https://github.com/your-username/firecrawl/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_data={
        "firecrawl": ["py.typed"],
    },
)
