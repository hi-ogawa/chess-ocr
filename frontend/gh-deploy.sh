#!/bin/bash

node node_modules/gh-pages/bin/gh-pages-clean
NODE_DEBUG=gh-pages npx gh-pages -d . -s "index.*" -m "Deploy $(git rev-parse --short HEAD)"
