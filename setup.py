import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-aws",
    version="0.4.0",
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
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    install_requires=["structlog", "pydantic", "okdata-sdk>=0.8.1"],
)
