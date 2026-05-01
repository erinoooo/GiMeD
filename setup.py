from setuptools import setup, find_packages

setup(
    name="gimed",
    version="0.1.0",
    description="Give Me a Desktop — headless Linux desktop setup tool",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "gimed=gimed.cli:main",
        ],
    },
    install_requires=[
        "simple-term-menu>=1.6",
        "rich>=13.0",
    ],
)
