from setuptools import setup


setup(
    name="ledger",
    version="0.1.0",
    py_modules=["ledger"],
    install_requires=[
        'Click',
        'pandas',
    ],
    entry_points='''
        [console_scripts]
        ledger=ledger:cli
    '''
)