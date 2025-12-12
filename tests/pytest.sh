#!/bin/bash
set -euo pipefail

docker build \
    --pull \
    --build-arg branch=stable \
    -t ${PWD##*/}:pytest \
    -f ./Dockerfile \
    --target testbuilder \
    .

# Build test samples from source files

docker run \
    -t \
    --rm \
    -v $(pwd)/tests/samples-src:/samples-src:ro \
    -v $(pwd)/tests/samples:/samples-out \
    ${PWD##*/}:pytest \
    bash -c "(cd /samples-src && make all BUILDDIR=/samples-out)"

if [[ -n "$FULL_SAMPLES_LOCATION" ]]; then
    MOUNT_SAMPLES="-v ${FULL_SAMPLES_LOCATION}:/opt/samples"
    ENV_SAMPLES="-e FULL_SAMPLES_LOCATION=/opt/samples"
fi
docker run \
    -t \
    --rm \
    -e FULL_SELF_LOCATION=/opt/al_service \
    $ENV_SAMPLES \
    -v /usr/share/ca-certificates/mozilla:/usr/share/ca-certificates/mozilla \
    -v $(pwd)/tests/:/opt/al_service/tests/ \
    $MOUNT_SAMPLES \
    ${PWD##*/}:pytest \
    bash -c "pip install -U -r tests/requirements.txt; pytest -p no:cacheprovider --durations=10 -rsx -vv -x"
