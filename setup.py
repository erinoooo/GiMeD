from setuptools import setup, find_packages

setup(
    name="gimed",
    version="1.5.0",
    description="Give Me a Desktop — headless Linux desktop setup tool",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "gimed=gimed.cli:main",
        ],
    },
    install_requires=[
        "InquirerPy>=0.3.4",
        "rich>=13.0",
    ],
)
