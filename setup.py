import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-aws",
    version="7.0.0",
    author="Oslo kommune",
    author_email="dataspeilet@oslo.kommune.no",
    description="Collection of helpers for working with AWS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oslokommune/okdata-aws",
    packages=setuptools.find_namespace_packages(include=["okdata.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
    ],
    install_requires=[
        "boto3",
        "starlette>=0.36.3,<2.0.0",
        "structlog",
    ],
)
