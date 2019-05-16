#!/bin/bash
VERSION="$1"
twine upload dist/imacropy-${VERSION}.tar.gz dist/imacropy-${VERSION}-py3-none-any.whl
