from setuptools import setup, find_packages

setup(
    name="stock_predictor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open(".streamlit/dependencies.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.9,<3.10",
)
