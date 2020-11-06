import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-awslambda",
    version="0.1.0",
    author="Oslo Origo",
    author_email="dataplattform@oslo.kommune.no",
    description="Collection of helpers for working with AWS Lambda",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oslokommune/okdata-awslambda",
    packages=setuptools.find_namespace_packages(
        include="origo.awslambda.*", exclude=["tests*"]
    ),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "dataplatform-common-python",  # Temporary for the status classes
        "structlog",
    ],
)
