#!/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

docker build \
    --pull \
    --build-arg branch=stable \
    -t ${PWD##*/}:pytest-samplebuilder \
    -f $SCRIPT_DIR/Dockerfile \
    .

# Build test samples from source files
mkdir -p $SCRIPT_DIR/samples

docker run \
    -t \
    --rm \
    -v $SCRIPT_DIR/samples-src:/samples-src:ro \
    -v $SCRIPT_DIR/samples:/samples-out \
    -u $(id -u):$(id -g) \
    ${PWD##*/}:pytest-samplebuilder \
    bash -c "(cd /samples-src && make all BUILDDIR=/samples-out)"
