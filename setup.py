import os
import setuptools

INSTALL_REQUIRES = []
_requirements_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "requirements.txt"
)
if os.path.isfile(_requirements_path):
    with open(_requirements_path, "r") as rf:
        INSTALL_REQUIRES = rf.read().splitlines()

LONG_DESCRIPTION = ""
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="magla",
    version="0.0.1",
    author="Jacob Martinez",
    author_email="info@magnetic-lab.com",
    description="A free data pipeline for animation and visual-effects freelancers and studios, with an emphasis on dynamically generated `opentimelineio` timelines.",
    license="GNU General Public License v3 or later (GPLv3+)",
    platform="OS Independent",
    py_modules=["magla"],
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": [
            "flake8",
            "pytest",
            "pytest-cov",
        ]
    },
    long_description=LONG_DESCRIPTION,
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
    python_requires='>=2.7, <4',
    keywords="vfx post-production animation editing pipeline opentimelineio sql"
)
