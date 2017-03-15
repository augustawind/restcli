from setuptools import setup

setup(
    name='apicli',
    version='0.1',
    py_modules=['restcli'],
    install_requires=[
        'click>=6,<7',
        'jinja2>=2,<3',
        'Pygments>=2,<3',
        'PyYAML>=3,<4',
        'requests>=2,<3',
    ],
    entry_points='''
        [console_scripts]
        apicli=apicli:cli
    ''',
)
