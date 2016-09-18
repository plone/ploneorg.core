#!/bin/sh
rm -r ./lib ./include ./local ./bin
virtualenv --clear .
./bin/pip install --upgrade pip setuptools zc.buildout
./bin/buildout
