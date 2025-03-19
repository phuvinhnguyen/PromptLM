from setuptools import setup, find_packages

setup(
    name="PromptLM",  # Change this to your actual project name
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "git+https://github.com/phuvinhnguyen/FlowDesign.git"
    ],
    python_requires=">=3.7",
)
