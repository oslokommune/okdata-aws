import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-aws",
    version="4.0.0",
    author="Oslo Origo",
    author_email="dataplattform@oslo.kommune.no",
    description="Collection of helpers for working with AWS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oslokommune/okdata-aws",
    packages=setuptools.find_namespace_packages(
        include="origo.aws.*", exclude=["tests*"]
    ),
    namespace_packages=["okdata"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    install_requires=[
        "boto3",
        "okdata-sdk>=3.1.1,<4",
        "requests",
        "starlette>=0.36.3,<1.0.0",
        "structlog",
    ],
)
