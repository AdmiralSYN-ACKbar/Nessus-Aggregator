from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nessus-aggregator",
    version="0.2.3",
    description="Aggregate Nessus vulnerability scan results into consolidated Excel reports.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Admiral SYN-ACKbar",
    author_email="admiral@admiralsyn-ackbar.com",
    url="https://github.com/admiralsyn-ackbar/nessus-aggregator",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=1.0.0",
        "requests>=2.25.0",
        "urllib3>=1.26.0",
        "nessus-file-reader>=0.1.0",
        "xlsxwriter>=3.0.0"
    ],
    entry_points={
        "console_scripts": [
            "nessus-aggregator=nessus_aggregator.config:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7',
)