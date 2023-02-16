import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-aws",
    version="1.0.1",
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "okdata-sdk>=0.9.1",
        "pydantic",
        "requests",
        "starlette>=0.25.0,<1.0.0",
        "structlog",
    ],
)
