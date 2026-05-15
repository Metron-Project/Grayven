# Grayven

[![PyPI - Python](https://img.shields.io/pypi/pyversions/Grayven.svg?logo=Python&label=Python&style=flat-square)](https://pypi.python.org/pypi/Grayven/)
[![PyPI - Status](https://img.shields.io/pypi/status/Grayven.svg?logo=Python&label=Status&style=flat-square)](https://pypi.python.org/pypi/Grayven/)
[![PyPI - Version](https://img.shields.io/pypi/v/Grayven.svg?logo=Python&label=Version&style=flat-square)](https://pypi.python.org/pypi/Grayven/)
[![PyPI - License](https://img.shields.io/pypi/l/Grayven.svg?logo=Python&label=License&style=flat-square)](https://opensource.org/licenses/MIT)

[![prek](https://img.shields.io/badge/prek-enabled-informational?logo=prek&style=flat-square)](https://github.com/j178/prek)
[![Ruff](https://img.shields.io/badge/Ruff-enabled-informational?logo=ruff&style=flat-square)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/ty-enabled-informational?logo=ruff&style=flat-square)](https://github.com/astral-sh/ty)

[![Linting](https://github.com/Metron-Project/Grayven/actions/workflows/linting.yaml/badge.svg)](https://github.com/Metron-Project/Grayven/actions/workflows/linting.yaml)
[![Testing](https://github.com/Metron-Project/Grayven/actions/workflows/testing.yaml/badge.svg)](https://github.com/Metron-Project/Grayven/actions/workflows/testing.yaml)
[![Publishing](https://github.com/Metron-Project/Grayven/actions/workflows/publishing.yaml/badge.svg)](https://github.com/Metron-Project/Grayven/actions/workflows/publishing.yaml)
[![Read the Docs](https://img.shields.io/readthedocs/grayven?label=Read-the-Docs&logo=Read-the-Docs)](https://grayven.readthedocs.io/en/stable)

A [Python](https://www.python.org/) wrapper for the [Grand Comics Database API](https://github.com/GrandComicsDatabase/gcd-django/wiki/API).

## Installation

```sh
pip install Grayven
```

### Example Usage

```python
from datetime import timedelta
from pathlib import Path

from grayven.grand_comics_database import GrandComicsDatabase

session = GrandComicsDatabase(
    email="email@example.com",
    password="Password",
    cache=Path("cache.sqlite"),  # Optional, defaults to ~/.cache/grayven/cache.sqlite
    cache_expiry=timedelta(days=1),  # Optional, defaults to 14 days
)

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
