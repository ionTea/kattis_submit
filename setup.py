from setuptools import setup

setup(name='kattis_submit',
        version='1.0',
        description='CLI for submission to kattis',
        url='http://github.com/iontea/kattis_submit',
        author='Jonathan Ohlsson',
        packages=['kattis_submit'],
        entry_points = {
            'console_scripts': ['kattis=kattis_submit']
            },
        install_requires=[
            'beautifulsoup4',
            'colorama',
            'requests',
            ],
        zip_safe=False)
