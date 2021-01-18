from setuptools import setup, find_packages

setup(
    name='chase',
    version='1.0.0',
    author='Szymon Jeziorski',
    author_email='216784@edu.p.lodz.pl',
    description='Package allowing to run wolf chasing sheep simulation.',
    long_description='Package consisting of script allowing to run wolf chasing sheep simulation, setup its run configuration and export necessary run data.',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['chase = chase.main:main']
    },
    python_requires='>=3.9'
)
