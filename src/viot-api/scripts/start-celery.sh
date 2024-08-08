#!/usr/bin/env bash

celery -A app.modules.celery_task.celery worker -l info -B &
celery -A app.modules.celery_task.celery flower --port=8555 --basic-auth=admin:1234
