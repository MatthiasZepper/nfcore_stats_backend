#!/bin/bash

set -o errexit
set -eo pipefail
set -o nounset

/usr/local/bin/celery --app=backend.api.tasks worker --beat -l info -Q main-queue -c 1
