from setuptools import find_packages, setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.rst", "r", encoding="utf-8") as f:
    README = f.read()

setup(
    name='scrapy-x',
    packages=find_packages(),
    install_requires=required,
    version='1.2',
    author='Mohamed Al Ashaal',
    author_email='m7medalash3al@gmail.com',
    license='Apache License V2.0',
    description='a scrapy subcommand for easily enqueuing crawling jobs in a scalable and high performance way',
    summary='a scrapy serving module',
    url='https://github.com/alash3al/scrapyx',
    python_requires='>=3.6.9',
    entry_points={
        'scrapy.commands': [
            'x=scrapyx.x:Command',
        ],
    },
    long_description=README,
)
