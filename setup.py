import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="natsulang",
    version="1.0.0.b1",
    author="CJC Apps",
    author_email="jrgdcharlieyan@gmail.com",
    description="A text-processing language based on Python 3.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CJC-Apps/natsulang",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'natsulang = natsulang:run'
        ]
    },
    python_requires='>=3.4',
)