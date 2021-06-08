#!/bin/sh

pytest --cov docman --cov-branch --cov-report term-missing $@
