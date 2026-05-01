from setuptools import setup, find_packages

setup(
    name="gimed",
    version="1.4.0",
    description="Give Me a Desktop — headless Linux desktop setup tool",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "gimed=gimed.cli:main",
        ],
    },
    install_requires=[
        "questionary>=2.0",
        "rich>=13.0",
    ],
)