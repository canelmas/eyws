import setuptools
from eyws.about import __version__, __author__, __license__, __email__, __description__, __name__, __url__

requires = [
    "jinja2>=2.10",
    "python-dateutil>= 2.7.3",
    "boto3==1.8.1",
    "botocore==1.11.1",
]

setuptools.setup(
    name=__name__,
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    keywords="aws cli",
    install_requires=requires,
    python_requires=">=3.1",
    include_package_data=False,
    entry_points={
        "console_scripts": [
            "eyws = eyws.parser:execute"
        ]
    },
    zip_safe=False,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"]
)
