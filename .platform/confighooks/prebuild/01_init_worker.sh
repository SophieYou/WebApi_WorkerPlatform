#!/bin/bash
if [[ "$WORKER" == "true" ]]; then
  echo 'This is worker'
  pwd
  cat Procfile-worker > Procfile
else
  echo 'This is web'
  pwd
  cat Procfile-web > Procfile
fi
