import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="magla-jacobmartinez3d",
	version="0.0.17",
	author="Jacob Martinez",
	description="A free data pipeline for animation and visual-effects freelancers and studios, with an emphasis on dynamically generated `opentimelineio` timelines.",
	license="GNU General Public License v3 or later (GPLv3+)",
 	platform="OS Independent",
 	py_modules=["magla"],
	install_requires = [
		"sqlalchemy",
		"opentimelineio",
		"PyYaml",
		"psycopg2",
		"pyaaf2",
		"cmake"
	],
	extras_require = {
		"dev": [
			"sqlalchemy-utils"
			"pytest",
			"pytest-cov"
		]
	},
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/magnetic-lab/magla",
	packages=setuptools.find_packages(),
	classifiers=[
     		"Development Status :: 2 - Pre-Alpha",
        	"Programming Language :: Python :: 2.7",
        	"Operating System :: OS Independent",
			"Framework :: Pytest",
			"Topic :: Multimedia :: Video"
	],
	python_requires='>=2.7'
)
