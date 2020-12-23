from setuptools import find_packages, setup

setup(
    name='scrapy-x',
    packages=find_packages(),
    version='1.0.0',
    author='Mohamed Al Ashaal',
    description='a scrapy subcommand for easily enqueuing crawling jobs in a scalable and high performance way',
    url='https://github.com/alash3al/scrapyx',
    python_requires='>=3.6.9',
    entry_points={
        'scrapy.commands': [
            'x=scrapyx.x:Command',
        ],
    },
)
