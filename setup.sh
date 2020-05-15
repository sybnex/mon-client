#!/bin/bash

set -e

# checks
python3 tests.py

# migrate
if [ -d "$HOME/.monitor" ]; then
  cp $HOME/.monitor/config.yaml .
  rm -rf $HOME/.monitor/
fi

# configfile
if [ ! -f config.yaml ]; then
  cp config_example.yaml config.yaml
  vi config.yaml
fi

set +e
CRONTAB=$(crontab -lu $USER 2>/dev/null | grep client.py)
if [[ ! "$CRONTAB" == *"client.py"* ]]; then
  CRON="* * * * * $(which python3) $PWD/client.py >/dev/null 2>/dev/null"
  (crontab -lu $USER; echo "$CRON" ) | crontab -u $USER -
fi

# testrun
$(which python3) $PWD/client.py

echo "Crontab:"; crontab -l

exit 0
