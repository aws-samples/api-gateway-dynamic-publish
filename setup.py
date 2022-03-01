import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="api-gateway-dynamic-publish",
    version="0.0.1",

    description="A sample CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "api-gateway-dynamic-publish"},
    packages=setuptools.find_packages(where="api-gateway-dynamic-publish"),

    install_requires=[
        "aws-cdk.core==2.14.0",
        "aws-cdk.aws_iam==2.14.0",
        "aws-cdk.aws_lambda==2.14.0",
        "aws-cdk.aws_logs==2.14.0",
        "aws-cdk.custom_resources==2.14.0",
        "aws-cdk.aws_s3==2.14.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
