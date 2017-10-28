from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='streetview',
    version='0.1',
    description='Retrieve current and historical photos from Google Street View',
    long_description=readme(),
    url='https://github.com/robolyst/streetview',
    author='Adrian Letchford',
    author_email='me@dradrian.com',
    license='MIT',
    packages=['streetview'],
    zip_safe=False,
    install_requires=[
        'requests',
        'pillow',
    ],
)
