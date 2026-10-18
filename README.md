## pygris

__pygris__ is a Python package to help users access US Census Bureau TIGER/Line and cartographic boundary shapefiles and load them into Python as GeoDataFrames.  The goal of the package is to make it simple to access US Census geographic data; data can be acquired with a single function for a given geography (e.g. `tracts()` for Census tracts) along with a few options.

The package is a general port of the [R __tigris__ package](https://github.com/walkerke/tigris) with a few modifications.  The framework of and philosophy behind the __tigris__ package is covered in [Chapter 5 of my book, _Analyzing US Census Data: Methods, Maps and Models in R_](https://walker-data.com/census-r/census-geographic-data-and-applications-in-r.html).

Install __pygris__ from PyPI with the following command:

```bash
pip install pygris

# For optional dependencies to support interactive examples in the documentation:
# pip install pygris[explore]
```

Or via `conda-forge` with:

```bash
conda install pygris

# For optional dependencies to support interactive examples in the documentation:
# conda install "pygris[explore]"
```

Alternatively, install the development version from GitHub:

```bash
pip install git+https://github.com/walkerke/pygris.git
```

Support for installation with `conda` is forthcoming.

Read the following articles for more information on how to use the package:

* [Basic usage of pygris](https://walker-data.com/pygris/01-basic-usage)
* [Working with geometries in pygris](https://walker-data.com/pygris/02-geometries)
* [Data utilities in pygris](https://walker-data.com/pygris/03-data-utilities)
* [Geocoding and custom filters in pygris](https://walker-data.com/pygris/04-geocoding)

## Contributing

Contributions are welcome. This repository uses [pre-commit](https://pre-commit.com/) to run lint checks and code formatting (via [ruff](https://docs.astral.sh/ruff/)) on every commit, and the same checks run on every pull request in continuous integration.

To set it up:

```bash
pip install pre-commit
pre-commit install
```

The configured checks will then run automatically when you create a commit. To run them against all files in the repository manually:

```bash
pre-commit run --all-files
```

If a check fails:

* Formatting checks (like `ruff-format`, `trailing-whitespace`, and `end-of-file-fixer`) will typically fix the files automatically. Add the modified files and create the commit again.
* Check errors that don't modify files (like `ruff-check` findings) need to be fixed manually before re-committing. Some warnings can be suppressed with a `# noqa` comment where the rule is not applicable; see the [ruff rules documentation](https://docs.astral.sh/ruff/rules/) for details.
* If a check fails, the same failure will show up as a failing check on your pull request, so it is easiest to resolve them locally before submitting.
