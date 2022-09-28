#!/bin/sh

set -a
. ./.env
alembic upgrade head
