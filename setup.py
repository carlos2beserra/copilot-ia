#!/usr/bin/env python3
# =============================================================================
# Copilot-IA - Setup
# =============================================================================
"""
Setup para instalação do pacote Copilot-IA.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Ler README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Ler requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text().split("\n")
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="copilot-ia",
    version="0.1.0",
    author="Copilot-IA Team",
    author_email="contato@copilot-ia.dev",
    description="Plataforma de Copilotos de Desenvolvimento Inteligentes com Agno",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/copilot-ia",
    project_urls={
        "Bug Tracker": "https://github.com/seu-usuario/copilot-ia/issues",
        "Documentation": "https://github.com/seu-usuario/copilot-ia#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "notebooks"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=5.0.0",
            "black>=24.0.0",
            "ruff>=0.5.0",
            "mypy>=1.11.0",
        ],
        "docs": [
            "mkdocs>=1.6.0",
            "mkdocs-material>=9.5.0",
            "mkdocstrings[python]>=0.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "copilot=examples.cli_example:app",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

