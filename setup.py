from setuptools import setup

setup(
    name='apicli',
    version='0.1',
    py_modules=['restcli'],
    entry_points='''
        [console_scripts]
        apicli=apicli:cli
    '''
)
