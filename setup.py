from setuptools import setup, find_packages

setup(
    name="TreeExplorer-Python",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "ete3",
        "pandas",
        "openpyxl",
        "Pillow"
    ],
    entry_points={
        'console_scripts': [
            'trex=TreeExplorer:main',
        ],
    },
    author="Damian Magill",
    author_email="damian.magill@iff.com",
    description="A GUI application enabling the labelling and exploration of phylogenetic trees based on genogroup file information.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/DamianJM/T-REX",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
