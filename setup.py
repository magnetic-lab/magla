import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="magla-jacobmartinez3d",
    version="0.0.181",
    author="Jacob Martinez",
    author_email="info@magnetic-lab.com",
    description="A free data pipeline for animation and visual-effects freelancers and studios, with an emphasis on dynamically generated `opentimelineio` timelines.",
    license="GNU General Public License v3 or later (GPLv3+)",
    platform="OS Independent",
    py_modules=["magla"],
    install_requires=[
        "appdirs",
        "cmake",
        "opentimelineio>=0.13",
        "PyYAML",
        "psycopg2",
        "pyaaf2",
        "configparser",
        "sqlalchemy",
        "sqlalchemy-utils==0.36.6; python_version < '3.0'",
        "sqlalchemy-utils>=0.36.6; python_version >= '3.0'"
    ],
    extras_require={
        "dev": [
            "flake8",
            "pytest",
            "pytest-cov",
        ]
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/magnetic-lab/magla",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Framework :: SQLAlchemy",
        "Topic :: Multimedia :: Video"
    ],
    python_requires='>=2.7, <=3.9',
    keywords="vfx post-production animation editing pipeline opentimelineio sql"
)
