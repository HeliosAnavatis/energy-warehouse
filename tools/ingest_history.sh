#!/bin/bash

set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage:"
    echo "  $0 START_DATE END_DATE [DELAY_SECONDS]"
    exit 1
fi

START_DATE="$1"
END_DATE="$2"
DELAY="${3:-2}"

current="$START_DATE"

echo "Starting historical ingest"
echo "From : $START_DATE"
echo "To   : $END_DATE"
echo "Delay: ${DELAY}s"
echo

while true
do
    echo "================================================="
    echo "Ingesting $current"
    echo "================================================="

    if python3 ingest_day.py "$current"
    then
        echo "SUCCESS: $current"
    else
        echo "FAILED : $current"
    fi

    if [ "$current" = "$END_DATE" ]; then
        break
    fi

    sleep "$DELAY"

    current=$(date -I -d "$current + 1 day")
done

echo
echo "Historical ingest complete"