#!/bin/bash

set -o errexit
set -eo pipefail
set -o nounset

/usr/local/bin/uvicorn mnt.backend.api.main:app --host 0.0.0.0 --port 8000 --reload
