"""
Setup script for Django Project Generator
Install globally with: pip install -e .
"""
from setuptools import setup, find_packages

setup(
    name="django-nfxinit",
    version="1.0.0",
    description="AI-powered Django project scaffolder by Nickelfox",
    author="Nickelfox",
    author_email="info@nickelfox.com",
    packages=find_packages(),
    py_modules=["main"],
    include_package_data=True,
    install_requires=[
        "typer[all]==0.12.3",
        "requests>=2.31.0",
        "rich==13.7.1",
        "python-dotenv==1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "NFXinit=main:app",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
