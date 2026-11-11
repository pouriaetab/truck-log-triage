#!/usr/bin/env bash
# get_metadata.sh: step 1 of truck-log-triage.
# Downloads the metadata of MAN TruckScenes mini (about 14 MB, no account needed) into data/
# and checks that all 14 tables arrived. Safe to run again: a copy that is already there is kept.
set -euo pipefail
 
URL="https://man-truckscenes.s3.eu-central-1.amazonaws.com/release/mini/man-truckscenes_metadata_v1.2-mini.zip"
DIR="data/man-truckscenes/v1.2-mini"
 
if [ -d "$DIR" ]; then
  echo "already here: $DIR"
else
  mkdir -p data
  curl -fsSL "$URL" -o data/metadata.zip   # -f: fail on an HTTP error instead of saving the error page
  unzip -q data/metadata.zip -d data
  rm data/metadata.zip
fi
 
n=$(ls "$DIR"/*.json | wc -l)
if [ "$n" -ne 14 ]; then
  echo "expected 14 tables, found $n" >&2
  exit 1
fi
echo "ok: $n tables in $DIR"