import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="multi-exchange-kktkk", # Replace with your own username
    version="0.0.1",
    author="kktkk",
    author_email="ko.ktk@pm.me",
    description="A multi exchange wrapper support with standardized output.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/arbator/server/exchange_wrappers.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)