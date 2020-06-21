#!/bin/sh
celery worker -A tasks.celery --loglevel=INFO --concurrency=8
