#!/bin/bash

export $(grep -v '^#' .env | xargs -d '\n')
rq worker --with-scheduler --worker-class rq.SimpleWorker