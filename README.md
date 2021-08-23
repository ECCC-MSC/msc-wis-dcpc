[![Build Status](https://github.com/ECCC-MSC/msc-wis-dcpc/workflows/test%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/ECCC-MSC/msc-wis-dcpc/actions)

# msc-wis-dcpc

## Overview

MSC WIS DCPC implementation 

## Installation

### Requirements
- Python 3
- [virtualenv](https://virtualenv.pypa.io/)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during msc-wis-dcpc installation.

Dependencies of note:
 - [pycsw](https://pycsw.org)
 - [pygeometa](https://geopython.github.io/pygeometa)

### Installing msc-wis-dcpc
```bash
# setup virtualenv
python3 -m venv --system-site-packages msc-wis-dcpc
cd msc-wis-dcpc
source bin/activate

# clone pycsw and install
git clone https://github.com/geopython/pycsw.git
cd pycsw
python setup.py install
pip install -r requirements-standalone.txt
cd ..

# clone codebase and install
git clone https://github.com/ECCC-MSC/msc-wis-dcpc.git
cd msc-wis-dcpc
python setup.py build
python setup.py install

# configure environment
cp msc-wis-dcpc.env dev.env
vi dev.env # edit paths accordingly
. dev.env
cd ..

# serve API
cd pycsw
python pycsw/wsgi_flask.py
```

## Running

Server will be located at http://localhost:8000 with links to all supported search API endpoints

### Managing metadata

```bash
# harvest a CSW's metadata
msc-wis-dcpc metadata add --type OGC:CSW --url https://example.org/csw

# harvest MSC GeoMet configuration and MCFs
msc-wis-dcpc metadata add --type MSC:GeoMet:config --config /path/to/geomet-config.yml --mcf-dir /path/to/mcfs
```

Use the [pycsw-admin.py](https://docs.pycsw.org/en/latest/administration.html) utility for all other metadata repository workflows

### Sample Queries

See HowTo page examples at:

- https://gist.github.com/kalxas/6ecb06d61cdd487dc7f9
- https://gist.github.com/kalxas/5ab6237b4163b0fdc930 

## Development

### Running Tests

TODO

## Releasing

```bash
python setup.py sdist bdist_wheel --universal
twine upload dist/*
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/ECCC-MSC/msc-wis-dcpc/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
