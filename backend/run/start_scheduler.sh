#!/bin/bash

set -o errexit
set -eo pipefail
set -o nounset

mkdir -p /var/run/celery /var/log/celery
chown -R nobody:nogroup /var/run/celery /var/log/celery

/usr/local/bin/celery --app=mnt.backend.api.tasks worker --beat -l info -Q main-queue -c 1 --uid=nobody --gid=nogroup
