# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


with open("./README.md") as f:
    long_description = f.read()

setup(
    name="pytest-github-annotations",
    version="0.1.6",
    description="forked pytest plugin to annotate failed tests with a workflow command for GitHub Actions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="utgwkk",
    author_email="dciborow@microsoft.com",
    url="https://github.com/dciborow/pytest-github-annotations",
    license="MIT",
    classifiers=["Framework :: Pytest",],
    packages=find_packages(),
    entry_points={
        "pytest11": [
            "pytest_github_actions_annotate_failures = pytest_github_actions_annotate_failures.plugin",
        ],
    },
    install_requires=["pytest>=4.0.0",],
)
