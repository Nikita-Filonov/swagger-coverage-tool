from setuptools import setup, find_packages

setup(
    name="swagger-coverage-tool",
    version="0.27.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "httpx",
        "pyyaml>=6.0.2",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.8.0",
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'swagger-coverage-tool = swagger_coverage_tool.cli.main:cli',
        ],
    },
    author="Nikita Filonov",
    author_email="filonov.nikitkaa@gmail.com",
    description="A tool for measuring API test coverage based on Swagger",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nikita-Filonov/swagger-coverage-tool",
    project_urls={
        "Bug Tracker": "https://github.com/Nikita-Filonov/swagger-coverage-tool/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
