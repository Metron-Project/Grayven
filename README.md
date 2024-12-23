# Grayven

[![PyPI - Python](https://img.shields.io/pypi/pyversions/Grayven.svg?logo=Python&label=Python&style=flat-square)](https://pypi.python.org/pypi/Grayven/)
[![PyPI - Status](https://img.shields.io/pypi/status/Grayven.svg?logo=Python&label=Status&style=flat-square)](https://pypi.python.org/pypi/Grayven/)
[![PyPI - Version](https://img.shields.io/pypi/v/Grayven.svg?logo=Python&label=Version&style=flat-square)](https://pypi.python.org/pypi/Grayven/)
[![PyPI - License](https://img.shields.io/pypi/l/Grayven.svg?logo=Python&label=License&style=flat-square)](https://opensource.org/licenses/MIT)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-informational?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/badge/ruff-enabled-informational?logo=ruff&style=flat-square)](https://github.com/astral-sh/ruff)

[![Github - Contributors](https://img.shields.io/github/contributors/Metron-Project/Grayven.svg?logo=Github&label=Contributors&style=flat-square)](https://github.com/Metron-Project/Grayven/graphs/contributors)
[![Github Action - Testing](https://img.shields.io/github/actions/workflow/status/Metron-Project/Grayven/testing.yaml?branch=main&logo=Github&label=Testing&style=flat-square)](https://github.com/Metron-Project/Grayven/actions/workflows/testing.yaml)
[![Github Action - Publishing](https://img.shields.io/github/actions/workflow/status/Metron-Project/Grayven/publishing.yaml?branch=main&logo=Github&label=Publishing&style=flat-square)](https://github.com/Metron-Project/Grayven/actions/workflows/publishing.yaml)

[![Read the Docs](https://img.shields.io/readthedocs/grayven?label=Read-the-Docs&logo=Read-the-Docs&style=flat-square)](https://grayven.readthedocs.io/en/stable)

A [Python](https://www.python.org/) wrapper for the [Grand Comics Database API](https://github.com/GrandComicsDatabase/gcd-django/wiki/API).

## Installation

```console
pip install --user Grayven
```

### Example Usage

```python
from grayven.grand_comics_database import GrandComicsDatabase
from grayven.sqlite_cache import SQLiteCache

session = GrandComicsDatabase(cache=SQLiteCache())

# Search for Series
results = session.list_series(name="Green Lantern")
for series in results:
    print(f"{series.id} | {series.name} ({series.year_began})")

# Get an issue's release date
result = session.get_issue(id=242700)
print(result.on_sale_date)
```

## Documentation

- [Grayven](https://grayven.readthedocs.io/en/stable)
- [GrandComicsDatabase API](https://github.com/GrandComicsDatabase/gcd-django/wiki/API)

## Bugs/Requests

Please use the [GitHub issue tracker](https://github.com/Metron-Project/Grayven/issues) to submit bugs or request features.

## Socials

[![Social - Matrix](https://img.shields.io/matrix/metron-general:matrix.org?label=Metron%20General&logo=matrix&style=for-the-badge)](https://matrix.to/#/#metron-general:matrix.org)
[![Social - Matrix](https://img.shields.io/matrix/metron-devel:matrix.org?label=Metron%20Development&logo=matrix&style=for-the-badge)](https://matrix.to/#/#metron-development:matrix.org)
