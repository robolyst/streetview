from setuptools import setup

from version import VERSION


def readme():
    with open("readme.md") as f:
        return f.read()


setup(
    name="streetview",
    version=VERSION,
    description="Retrieve current and historical photos from Google Street View",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/robolyst/streetview",
    author="Adrian Letchford",
    author_email="me@dradrian.com",
    license="MIT",
    packages=["streetview"],
    zip_safe=False,
    install_requires=[
        "requests",
        "pillow",
        "pydantic",
    ],
)
