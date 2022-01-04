from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

version = "0.0.2"

setup(
    name="linked-dict",
    version=version,

    author="Alex Lovser",
    author_email="tabalex2005@gmail.com",

    description="Advanced Python Dictionary which can link it-self keys into it-self values",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/AlexLovser/LinkedDict",
    download_url='https://github.com/AlexLovser/LinkedDict/archive/v{}.zip'.format(version),

    license='Apache Licence, Version 2.0, see LICENSE file',

    packages=['linked_dict'],
    platforms=['Windows', 'Linux', 'OSX'],
    keywords='python types dictionary dict hashmap hashtable self-link',
    requires=[],
    classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
