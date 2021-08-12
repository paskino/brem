# GitHub Actions

## Building the Conda Package: [conda](https://github.com/paskino/brem/blob/main/.github/workflows/conda.yml)
This github action builds and tests the conda package, by using the [conda-package-publish-action](https://github.com/paskino/conda-package-publish-action)

When pushing to main *all* variants are built and tested.

When making an [annotated](https://git-scm.com/book/en/v2/Git-Basics-Tagging) tag, *all* variants are built, tested and published to the [paskino conda channel for brem](https://anaconda.org/paskino/brem/files). This includes linux, windows and macOS versions.

When opening or modifying a pull request to main, a single variant is built and tested, but not published. This variant is `python=3.7` and `numpy=1.18`.

## Building the PyPi Package: [CI](https://github.com/paskino/brem/blob/main/.github/workflows/CI.yml)
This github action builds the pypi package, by using the [deploy-pypi action](https://github.com/casperdcl/deploy-pypi).

When pushing to main it is built and checked.

When making an [annotated](https://git-scm.com/book/en/v2/Git-Basics-Tagging) tag, it is built and published to the [PyPi](https://pypi.org/project/brem/#description).
