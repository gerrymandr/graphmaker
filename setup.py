import setuptools

setuptools.setup(
    name='graphmaker',
    version='0.1.0',

    author='Max Hully',
    author_email='max.hully@gmail.com',

    packages=setuptools.find_packages(),
    include_package_data=True,

    url='https://github.com/gerrymandr/graphmaker',
    license='LICENSE',

    description='',
    long_description='',

    install_requires=[
        'Click',
        'geopandas',
        'pandas',
        'networkx',
        'numpy',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        gerry=graphmaker.cli:cli
    ''',
)
